
from click import format_filename
import matplotlib.pyplot as plt
from erad.scenarios.utilities import ProbabilityFunctionBuilder, GeoUtilities
from erad.constants import ELEVATION_RASTER_FILE, DATA_FOLDER, FLOOD_HISTORIC_SHP_PATH
from shapely.geometry import MultiPolygon, Point, LineString, Polygon
from erad.scenarios.abstract_scenario import BaseScenario
from datetime import datetime, timedelta
from scipy.optimize import curve_fit
from scipy.spatial import Delaunay
import geopandas as gpd
import pandas as pd
import numpy as np
import stateplane
import xmltodict
import itertools
import requests
import rasterio
import tarfile
import time
import sys
import os

from erad.scenarios.common import AssetTypes, asset_list
from erad.scenarios.utilities import ProbabilityFunctionBuilder

#plt.ion()
class FlooadScenario(BaseScenario, GeoUtilities):
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
        super(FlooadScenario, self).__init__(poly, probability_model, timestamp, **kwargs)
        self.kwargs = kwargs
        self.samples = 100
        self.use_api = True
        
        # self.map_elevation() 
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
            crs = {'init': 'epsg:4326'}
            self.gauges = gpd.GeoDataFrame(df).set_geometry('geometry')
            #self.gauges = gpd.read_file(kwargs['file_gaugues'])
            pass
        # self.plot = DynamicUpdate(self.X, self.Y, self.Z, self.levels)
        return
    
    @classmethod
    def from_historical_flood_by_code(cls, flood_code : str, probability_function : dict = None):
        data_file = os.path.join(DATA_FOLDER, FLOOD_HISTORIC_SHP_PATH)
        assert os.path.exists(data_file), f"The data file {data_file} not found"
        flood_data = gpd.read_file(data_file)
        flood_data = flood_data[flood_data['DFIRM_ID'] == flood_code]
        raise NotImplementedError("Model has not been implemented")
        
    def real_time(self):
        self.gauges = self.get_flow_measurements(0)
        self.gauges.to_csv("gauges.csv")
        flows, levels = self.gauges_in_polygon()
        for c in flows.columns:
            flows[c] = flows[c].interpolate(method='polynomial', order=2)
            levels[c] = levels[c].interpolate(method='polynomial', order=2)
        flows = flows.ffill(axis = 0)
        levels = levels.ffill(axis = 0)
        flows = flows.bfill(axis = 0)
        levels = levels.bfill(axis = 0)
        self.flows = flows.resample("15T").interpolate()
        self.levels = levels.resample("15T").interpolate()
        self.flows.to_csv("flows.csv")
        self.levels.to_csv("levels.csv")

    @property
    def valid_timepoints(self):
        return list(self.flows.index)
    
    def gauges_in_polygon(self):
        all_flows = pd.DataFrame()
        all_levels = pd.DataFrame()
        for idx, gauge in self.gauges.iterrows():
            flow = pd.DataFrame()
            level = pd.DataFrame()
            gauge_id = gauge['GaugeLID']
            url = f'https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage={gauge_id}&output=xml'
            response = requests.get(url)
            #print(response.text)
            data = xmltodict.parse(response.text)
            times_series_data = data['site']['observed']['datum']
            time_points = []
            flow_points = []
            level_points =[]
            for data_point in times_series_data:
                time_points.append(data_point['valid']['#text'])
                flow_points.append(float(data_point['secondary']['#text']))
                level_points.append(float(data_point['primary']['#text']))
            index =pd.to_datetime(time_points)
            flow.index =index
            flow[gauge_id] = flow_points
            level.index =index
            level[gauge_id] = level_points
            print(flow)
            print(level)
            all_flows = flow.merge(all_flows, right_index=True, left_index=True, how="outer")
            all_levels = level.merge(all_levels, right_index=True, left_index=True, how="outer")
        return all_flows, all_levels
    
    def get_flow_measurements(self, forecast_day: int = 0):
        if forecast_day == 0:
            forecast_tag = "obs"
        else:
            if forecast_day == 1:   
                forecast_tag = "fcst_f024"
            else:
                forecast_tag = f"fcst_f{forecast_day*24}"
                
        url = f"https://water.weather.gov/ahps/download.php?data=tgz_{forecast_tag}"
        r = requests.get(url, allow_redirects=True)
        date = str(datetime.now()).replace(":", "_").replace(".", "_").replace(" ", "_")
        shape_file_path = os.path.join(DATA_FOLDER, f'flood_shapefile_{date}.tgz')
        open(shape_file_path, 'wb').write(r.content)
        file_path = self.extract(shape_file_path, forecast_tag)
        data = gpd.read_file(file_path)
        if not data.empty:
            water_info = []
            for idx, row in data.iterrows():
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
   
    def get_elevation_by_latlong(self, lat, lon):
        coords = ((lat,lon), (lat,lon))
        vals = self.raster.sample(coords)
        for val in vals:
            elevation=val[0]
            return 255-elevation

    def map_elevation(self):
        y_min, x_min, y_max, x_max = self.multipolygon.bounds
        ys = np.linspace(y_min, y_max, self.samples, endpoint=True)
        xs = np.linspace(x_min, x_max, self.samples, endpoint=True)
        self.X, self.Y = np.meshgrid(xs, ys)
        
        if self.use_api:
            self.Z = self.create_elevation_profile_using_api()
        else:
            self.Z = self.create_elevation_profile_using_rasterfile() 
  
        r, c = self.X.shape
        for i in range(r):
            for j in range(c):
                x_sp, y_sp = stateplane.from_lonlat(self.X[i, j], self.Y[i, j])
                self.X[i, j] =x_sp
                self.Y[i, j] =y_sp
        
        self.min_elevation = np.min(self.Z)
        self.max_elevation = np.max(self.Z)       

        pts = np.array([self.X.flatten(), self.Y.flatten(), self.Z.flatten()]).T
        self.volume = self.calc_polyhedron_volume(pts)

        return self.X, self.Y, self.Z

    def create_elevation_profile_using_rasterfile(self):
        raster_file = os.path.join(DATA_FOLDER, ELEVATION_RASTER_FILE)
        self.raster = rasterio.open(raster_file)
        r, c = self.X.shape
        self.Z = np.zeros(self.X.shape)
        for i in range(r):
            for j in range(c):
                self.Z[i, j] = self.get_elevation_by_latlong(self.X[i, j], self.Y[i, j])
        return self.Z
    
    def create_elevation_using_api(self, lat, lon):
        response = requests.get(
            f"https://api.airmap.com/elevation/v1/ele?points={lat},{lon}"
            )
        response = response.json()
        if response['status'] == 'success':
            # print(response, '--')
            return response['data'][0] * 3.28084
            
        else:
            print(response)
        
    def create_elevation_profile_using_api(self, X=None, Y=None):
        coords = []
        inputs_passed = True
        if X is None or Y is None:
            inputs_passed = False
            X = self.X.flatten()
            Y = self.Y.flatten()
        
        for x, y in zip(X, Y):
            coords.extend([str(y), str(x)])
 
        offset = 1000
        Z_coords = []
        for i in range(int(len(coords)/offset) + 1):
         
            filt_coords = coords[i * offset: (i + 1) * offset]
            filt_coords = ",".join(filt_coords)    
            response = requests.get(
            f"https://api.airmap.com/elevation/v1/ele?points={filt_coords}"
            )
            response = response.json()
            if response['status'] == 'success':
                Z_coords.extend(response['data'])
                # print(response)
            else:
                print(response)
        
        Z = np.array(Z_coords)
        if inputs_passed:
            return Z
        else:
            Z = np.reshape(Z, self.X.shape) * 3.28084
            return (Z)

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
            
            lat = row['Latitude']
            lon = row['Longitude'] 
            x_i, y_i = stateplane.from_lonlat(lon, lat)
            coords[0].append(x_i)
            coords[1].append(y_i)
            
            
            if self.use_api:
                # elevation = self.create_elevation_using_api(lat, lon)
                # TODO: Don't know the different between level and elevation or
                # how they relate 
                elevation = row['Elevation_ft']
                water_elevation = float(level) + elevation
            else:
                elevation = self.get_elevation_by_latlong(lat, lon)
                water_elevation = self.get_elevation_by_latlong(lat, lon) + float(level)

            self.gauges["elevation"] = elevation
            z.append(water_elevation) #water_elevation, flow
            coords[2].append(f"Gauge: {gauge}\nElevation: {elevation}\nWater level: {level}")
            water_elevations.append(water_elevation)
        self.gauges["water_level"] = water_elevations
        
        m = self.polyfit2d(np.array(coords[0]), np.array(coords[1]), np.array(z))
        # self.z_ = np.zeros(self.X.shape)
        
        for asset_type, asset_dict in assets.items():
            Xs = []
            Ys = []
            for asset, asset_data in asset_dict.items():
                Xs.append(asset_data['coordinates'][1])
                Ys.append(asset_data['coordinates'][0])
                x_i, y_i = stateplane.from_lonlat(asset_data['coordinates'][1], asset_data['coordinates'][0])
                z_i = self.polyval2d(x_i, y_i, m)
                assets[asset_type][asset]['asset_water_level_ft'] = z_i.tolist()  #list(self.polyval2d(x_i, y_i, m))
            
            # if self.use_api:    
            #     asset_elevations_ft = self.create_elevation_profile_using_api(Xs, Ys)
            # else:
            #     asset_elevations_ft = self.get_elevation_by_latlong(lat, lon)

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

    def function_to_fit(self, data, a, b, c):
        x = data[0]
        y = data[1]
        return (a * x) + (y * b) + c
    
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


class DynamicUpdate():
    #Suppose we know the x range
    min_x = 0
    max_x = 10

    def __init__(self, X, Y, Z, flows):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.flows = flows
        self.min_elevation = np.min(Z)
        self.max_elevation = np.max(Z) 
        
        ncontours = 15
        step_size = (self.max_elevation - self.min_elevation) / ncontours
        self.levels = np.arange(self.min_elevation, self.max_elevation, step_size)
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(121, projection='3d')        
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(224)

        self.ax1.plot_surface(X, Y, Z, rstride=1, cstride=1, color='0.99', antialiased=True, edgecolor='0.5')

        self.ax2.contour(X, Y, Z, zdir='z', cmap='coolwarm', levels=self.levels)
        self.flows.plot(ax = self.ax3)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.show()
        self.fig.savefig(f"topology_0.png")


    def update(self, water_elevations, scatter_points, water_surface, timestamp):
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
        
        self.ax2.contour(X, Y, Z, zdir='z', cmap='coolwarm', levels=self.levels)
        self.ax2.scatter(scatter_points[0], scatter_points[1], color='red')
        
        for x, y, t in zip(scatter_points[0], scatter_points[1], scatter_points[2]):
            self.ax2.text(x, y, t, fontsize=8)
            print(t)
        
        self.flows.plot(ax = self.ax3)
        self.ax3.axvline(timestamp, color="r")
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        #self.fig.savefig(f"topology_{int(water_elevation)}.png")
       

if __name__ == '__main__':

    
    
    from erad.scenarios.common import asset_list
    
    assets, multiploygon = asset_list(38.46, -122.95, 38.53, -122.80)  
    flood_1 = FlooadScenario(
        multiploygon, 
        None, 
        None, 
        file_flow=r'C:\Users\alatif\Documents\GitHub\erad\erad\scenarios\flows.csv',
        file_levels=r'C:\Users\alatif\Documents\GitHub\erad\erad\scenarios\levels.csv',
        file_gaugues=r'C:\Users\alatif\Documents\GitHub\erad\erad\scenarios\gauges.csv',
        )
    timestamp = flood_1.valid_timepoints[0]
    assets = flood_1.calculate_survival_probability(assets, timestamp)
    print(assets)
    # flood_1 = FlooadScenario.from_live_data(multiploygon, None, None, None, None)
    # timestamp = flood_1.valid_timepoints[-1]
    # for timestamp in flood_1.valid_timepoints:
    #     assets = flood_1.calculate_survival_probability(assets, timestamp)
    #     print(assets)
    #     time.sleep(0.01)
    