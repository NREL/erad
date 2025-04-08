import tarfile
import os

from shapely import MultiPolygon, Point, LineString
from pyhigh import get_elevation, get_elevation_batch
from datetime import datetime, timedelta
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import stateplane
import itertools
import requests

from erad.scenarios.utilities import ProbabilityFunctionBuilder, GeoUtilities
from erad.scenarios.utilities import ProbabilityFunctionBuilder
from erad.constants import DATA_FOLDER, FLOOD_HISTORIC_SHP_PATH
from erad.scenarios.abstract_scenario import BaseScenario
from erad.scenarios.common import AssetTypes

plt.ion()
class FloodScenario(BaseScenario, GeoUtilities):
    """Base class for FlooadScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        origin (Point): Earthquake origin point
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
        kwargs (dict): Additional parameters relevant for a particular scenario type      
    """
    
    fragility_curves = {
        # Electrical Grid Risk Assessment Against Flooding in Barcelona and Bristol Cities
        AssetTypes.substation.name : ProbabilityFunctionBuilder("norm", [1.5, 0.2]),
        AssetTypes.solar_panels.name : ProbabilityFunctionBuilder("norm", [0.04, .01]),
        # AssetTypes.buried_lines.name : ProbabilityFunctionBuilder("norm", [80, 10]),
        # estimated
        AssetTypes.wind_turbines.name : ProbabilityFunctionBuilder("lognorm", [0.8, 3, 2]),
        AssetTypes.battery_storage.name : ProbabilityFunctionBuilder("norm", [0.04, .01]),
        # estimated
        AssetTypes.transmission_poles.name  :  ProbabilityFunctionBuilder("lognorm", [0.8, 5, 3]),
        # Tsunami Fragility Functions for Road and Utility Pole Assets Using Field Survey and Remotely Sensed Data from the 2018 Sulawesi Tsunami, Palu, Indonesia
        AssetTypes.distribution_poles.name  : ProbabilityFunctionBuilder("lognorm", [1, 0.2, 1]),
        AssetTypes.transmission_overhead_lines.name  : ProbabilityFunctionBuilder("norm", [0.04, .01]),    
        AssetTypes.distribution_overhead_lines.name  : ProbabilityFunctionBuilder("norm", [0.04, .01]),
    }
    
    
    def __init__(self,  poly : MultiPolygon , probability_model : dict, timestamp : datetime, **kwargs) -> None:
        super(FloodScenario, self).__init__(poly, probability_model, timestamp, **kwargs)
        self.kwargs = kwargs
        self.samples = 20
    
        if 'type' in kwargs and kwargs['type'] == 'live':
            self.flows = pd.DataFrame()
            self.levels = pd.DataFrame()
            self.real_time()
        else:
            from shapely import wkt
            self.flows = pd.read_csv(kwargs['file_flow'],index_col=0, parse_dates=True)
            self.levels = pd.read_csv(kwargs['file_levels'], index_col=0, parse_dates=True)
            df = pd.read_csv(kwargs['file_gaugues'])
            df['geometry'] = df['geometry'].apply(wkt.loads)
            self.gauges = gpd.GeoDataFrame(df).set_geometry('geometry')

        return
    
    @classmethod
    def from_historical_flood_by_code(cls, flood_code : str, probability_function : dict = None):
        data_file = os.path.join(DATA_FOLDER, FLOOD_HISTORIC_SHP_PATH)
        assert os.path.exists(data_file), f"The data file {data_file} not found"
        flood_data = gpd.read_file(data_file)
        flood_data = flood_data[flood_data['DFIRM_ID'] == flood_code]
        raise NotImplementedError("Model has not been implemented")
    
    def get_gauge_locations(self):
        x_i = []
        y_i = []
        for x, y in zip(self.gauges['Longitude'], self.gauges['Latitude']):
            x, y = stateplane.from_lonlat(x, y)
            x_i.append(x)
            y_i.append(y)
        return [x_i, y_i, self.gauges['GaugeLID'].to_list()]  

    def real_time(self):
        self.gauges = self.get_flow_measurements(0)
        elevation = get_elevation_batch([(x, y) for x, y in zip(self.gauges['Latitude'], self.gauges['Longitude'])])
        self.gauges["elevation"] = elevation
        flows, levels = self.gauges_in_polygon()
        
        for df, df_name in zip([levels], ['levels']):  #zip([levels, flows], ['levels', 'flows']):    
            df = df.drop_duplicates()
            df.index = [idx.round("15min") for idx in df.index]
            df = df.groupby(df.index).sum()
            df = df.replace(0, np.NaN)
            for c in df.columns:
                df[c] = df[c].interpolate(method='polynomial', order=2)
            df = df.ffill(axis = 0)
            df = df.bfill(axis = 0)
            df = df.resample("15min").interpolate()
            setattr(self, df_name, df)


    @property
    def valid_timepoints(self):
        """
        Returns a list of valid timepoints for this scenario. The timepoints
        are the timepoints at which the scenario has data available.

        Returns
        -------
        list
            List of valid timepoints
        """
        return list(self.levels.index)
    
    def gauges_in_polygon(self):
        all_flows_dfs = pd.DataFrame()
        all_levels_dfs = pd.DataFrame()
        for _, gauge in self.gauges.iterrows():   
            gauge_id = gauge['GaugeLID']

            url =f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"
            print(url)
            reply = requests.get(url, allow_redirects=True)
            data = reply.json()
            observed= data['observed']['data']
            forcasted= data['forecast']['data']

            observed = pd.DataFrame(observed)
            forcasted = pd.DataFrame(forcasted)
            complete_gauge_data = pd.concat([observed, forcasted])
    
            index = pd.to_datetime(complete_gauge_data['validTime'])
            
            flow = pd.DataFrame(index=index.tolist())
            level = pd.DataFrame(index=index.tolist())
            level[gauge_id] = complete_gauge_data['primary'].to_list()
            flow[gauge_id] = complete_gauge_data['secondary'].to_list()
            
            all_flows_dfs = pd.merge(all_flows_dfs, flow, left_index=True, right_index=True, how='outer')
            all_levels_dfs = pd.merge(all_levels_dfs, level, left_index=True, right_index=True, how='outer')

        return all_flows_dfs, all_levels_dfs
    
    def get_flow_measurements(self, forecast_day: int = 0):
        if forecast_day == 0:
            forecast_tag = "obs"
        else:
            if forecast_day == 1:    
                forecast_tag = "fcst_f024"
            else:
                forecast_tag = f"fcst_f{forecast_day*24}"

        url =f"https://water.noaa.gov/resources/downloads/shapefiles/national_shapefile_{forecast_tag}.tgz"
        #old_interface_url = f"https://water.weather.gov/ahps/download.php?data=tgz_{forecast_tag}"
        r = requests.get(url, allow_redirects=True)
        date = str(datetime.now()).replace(":", "_").replace(".", "_").replace(" ", "_")
        shape_file_path = os.path.join(DATA_FOLDER, f'flood_shapefile_{date}.tgz')
        open(shape_file_path, 'wb').write(r.content)
        file_path = self.extract(shape_file_path, forecast_tag)
        data = gpd.read_file(file_path)
        if not data.empty:
            water_info = []
            for _, row in data.iterrows():
                point = Point(row['Latitude'], row['Longitude'])
                if self.multipolygon.contains(point):
                    water_info.append(row)
            return gpd.GeoDataFrame(water_info)
        else:
            raise Exception("No water measurement found in selected area.")
    
    def extract(self, tar_url, ext):
        extract_path = os.path.join(DATA_FOLDER, "flood_shape_file")
        tar = tarfile.open(tar_url, 'r')
        for item in tar:
            tar.extract(item, extract_path)
            if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
                self.extract(item.name, "./" + item.name[:item.name.rfind('/')])
        return os.path.join(extract_path, f'national_shapefile_{ext}.shp')
    
    @classmethod
    def from_live_data(
        cls,
        poly : MultiPolygon, 
        probability_function : dict, 
        startrime: datetime, 
        duration: timedelta, 
        timestep: timedelta
        ):
        kwargs = {
            'startrime' : startrime, 
            'duration' : duration,
            'timestep' : timestep,
            'type' : 'live',
        }
        
        return cls(poly, probability_function, startrime, **kwargs)


    def calc_polyhedron_volume(self, pts):

        def tetrahedron_volume(a, b, c, d):
            return np.abs(np.einsum('ij,ij->i', a-d, np.cross(b-d, c-d))) / 6
        
        dt = Delaunay(pts)
        tets = dt.points[dt.simplices]
        self.polyhedron_volume = np.sum(tetrahedron_volume(tets[:, 0], tets[:, 1], 
                                        tets[:, 2], tets[:, 3]))
        
        return self.polyhedron_volume
   
    @property
    def area(self) -> float:
        """Method to calculate area of affected region."""
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    @property
    def polygon(self) -> MultiPolygon:
        """Method to return polygon for the affected region."""
        raise NotImplementedError("Method needs to be defined in derived classes")
        
    @property
    def boundary(self) -> LineString:
        """Method to return boundary for the affected region."""
        raise NotImplementedError("Method needs to be defined in derived classes")
        
    @property
    def centroid(self) -> Point:
        """Method to return the centroid of the affected region."""
        return self.multipolygon.centroid
    
    def increment_time(self) -> dict:
        """Method to increment simulation time for time evolviong scenarios."""
        raise NotImplementedError("Method needs to be defined in derived classes")

    def calculate_survival_probability(self, assets : dict, timestamp: datetime) -> dict:
        """Method to calculate survival probaility of asset types.

        Args:
            assets (dict): The dictionary of all assets and their corresponding asset types
        """
        print('Calculating survival probaiblity ...')
        water_elevations = []
        coords = [
            [],[],[]
        ]
        z = []
        for idx, row in self.gauges.iterrows():
            
            gauge = row['GaugeLID']
            level = self.levels[gauge][timestamp] 
        
            x_i, y_i = stateplane.from_lonlat(row['Longitude'] , row['Latitude'])
            coords[0].append(x_i)
            coords[1].append(y_i)
            print(gauge, row['elevation'], float(level))
            water_elevation = row['elevation'] + float(level)

            z.append(water_elevation) #water_elevation, flow
            coords[2].append(f"Gauge: {gauge}\nElevation: {row['elevation']}\nWater level: {level}")
            water_elevations.append(water_elevation)
        self.gauges["water_level"] = water_elevations
        self.fitted_params = self.polyfit2d(np.array(coords[0]), np.array(coords[1]), np.array(z))
        
        for asset_type, asset_dict in assets.items():
            Xs = []
            Ys = []
            for asset, asset_data in asset_dict.items():
                Xs.append(asset_data['coordinates'][1])
                Ys.append(asset_data['coordinates'][0])
                x_i, y_i = stateplane.from_lonlat(asset_data['coordinates'][1], asset_data['coordinates'][0])
       
                z_i = self.polyval2d(x_i, y_i, self.fitted_params)
                assets[asset_type][asset]['asset_water_level_ft'] = z_i.tolist()  #list(self.polyval2d(x_i, y_i, m))
                assets[asset_type][asset]['elevation_ft'] = get_elevation(
                    asset_data['coordinates'][0], 
                    asset_data['coordinates'][1]
                )

            i = 0
            for asset, asset_data in asset_dict.items():
                h =   asset_data['asset_water_level_ft'] - asset_data['elevation_ft']
                assets[asset_type][asset]['submerge_depth_ft'] = h
                if asset_type in self.probability_model:
                    probability_function = self.probability_model[asset_type]
                    failure_probability = probability_function.probability(h)
                    assets[asset_type][asset]["survival_probability"] = 1 - failure_probability
                else:
                    assets[asset_type][asset]["survival_probability"] = 1
                i+=1
        
        return assets
    
    def polyfit2d(self, x, y, z, order=3):
        ncols = (order + 1)**2
        G = np.zeros((x.size, ncols))
        ij = itertools.product(range(order+1), range(order+1))
        for k, (i,j) in enumerate(ij):
            G[:,k] = x**i * y**j
        m, _, _, _ = np.linalg.lstsq(G, z)
        return m

    def polyval2d(self, x, y, m):
        order = int(np.sqrt(len(m))) - 1
        ij = itertools.product(range(order+1), range(order+1))
        z = np.zeros_like(x)
        for a, (i,j) in zip(m, ij):
            z += a * x**i * y**j
        return z
    
    def map_elevation(self, time_stamp: datetime):
        y_min, x_min, y_max, x_max = self.multipolygon.bounds
        ys = np.linspace(y_min, y_max, self.samples, endpoint=True)
        xs = np.linspace(x_min, x_max, self.samples, endpoint=True)
        X, Y = np.meshgrid(xs, ys)
        X_flattened = X.flatten()
        Y_flattened = Y.flatten()
        
        coordinates =[(y, x) for x, y in zip(X_flattened, Y_flattened)]
        Z = get_elevation_batch(coordinates)
        Z = np.reshape(Z, X.shape)
      
        r, c = X.shape
        for i in range(r):
            for j in range(c):
                x_sp, y_sp = stateplane.from_lonlat(X[i, j], Y[i, j])
                X[i, j] =x_sp
                Y[i, j] =y_sp
    
        pts = np.array([X.flatten(), Y.flatten(), Z.flatten()]).T
        self.volume = self.calc_polyhedron_volume(pts)
        W = self.get_water_surface(time_stamp, X, Y)
        return X, Y, Z, W

    def get_water_surface(self, time_stamp: datetime, X, Y):
        w_s = []
        x_s = []
        y_s = []
        z_s = []
        texts = []
        water_elevations = []
        for idx, row in self.gauges.iterrows():      
            gauge = row['GaugeLID']
            level = self.levels[gauge][time_stamp] 
        
            x_i, y_i = stateplane.from_lonlat(row['Longitude'] , row['Latitude'])
            x_s.append(x_i)
            y_s.append(y_i)
            water_elevation = row['elevation'] + float(level)
            z_s.append(water_elevation) #water_elevation, flow
            texts.append(f"Gauge: {gauge}\nElevation: {row['elevation']}\nWater level: {level}")
            water_elevations.append(water_elevation)
        self.gauges["water_level"] = water_elevations
        self.fitted_params = self.polyfit2d(np.array(x_s), np.array(y_s), np.array(z_s))

        for x, y in zip(X.flatten(), Y.flatten()):
            w_s.append(self.polyval2d(x, y, self.fitted_params))
        w = np.reshape(w_s, X.shape)
        w =np.full(w.shape, np.mean(w))
        return w

class DynamicFloodInterface():
    #Suppose we know the x range
    min_x = 0
    max_x = 10

    def __init__(self, X, Y, Z, levels):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.levels = levels
        self.min_elevation = np.min(Z)
        self.max_elevation = np.max(Z) 
        
        ncontours = 15
        step_size = (self.max_elevation - self.min_elevation) / ncontours
        self.levels_contour = np.arange(self.min_elevation, self.max_elevation, step_size)
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(121, projection='3d')        
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(224)
        self.ax1.plot_surface(X, Y, Z, rstride=1, cstride=1, color='0.99', antialiased=True, edgecolor='0.5')
        self.ax2.contour(X, Y, Z, zdir='z', cmap='coolwarm', levels=self.levels_contour)
        self.levels.plot(ax = self.ax3)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        # plt.show()
        # self.fig.savefig(f"topology_0.png")


    def update(self, scatter_points, water_surface, timestamp):
        print(timestamp)
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        X = self.X
        Y = self.Y
        Z = self.Z
       
        w = np.where(water_surface > Z, water_surface, np.nan)
        w.flat[0] = np.nan
        self.ax1.plot_surface(X, Y, w, rstride=1, cstride=1, color='c', antialiased=True, alpha=0.5, shade=False)
        self.ax1.plot_surface(X, Y, Z, rstride=1, cstride=1, color='0.99', antialiased=True, edgecolor='0.5')
        
        self.ax2.contour(X, Y, Z, zdir='z', cmap='coolwarm', levels=self.levels_contour)
        self.ax2.scatter(scatter_points[0], scatter_points[1], color='red')
        
        for x, y, t in zip(scatter_points[0], scatter_points[1], scatter_points[2]):
            self.ax2.text(x, y, t, fontsize=8)
        
        self.levels.plot(ax = self.ax3)
        self.ax3.axvline(timestamp, color="r")
        self.ax3.set_ylim(0, 100)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        #self.fig.savefig(f"topology_{int(water_elevation)}.png")