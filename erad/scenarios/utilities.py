from shapely.geometry import MultiPolygon, Point, LineString
from shapely.ops import nearest_points
import matplotlib.pyplot as plt
import scipy.stats as stats
import geopy.distance
import numpy as np
import stateplane


class GeoUtilities:
    
    @property
    def identify_stateplane_projection(self) -> str:
        """ Automatically identifies stateplane projection ID  """ 
        x = self.centroid.x
        y = self.centroid.y
        return stateplane.identify(x, y)
    
    def in_polygon(self, point : Point) -> bool:
        return self.multipolygon.contains(point)

    def distance_from_boundary(self, point : Point) -> float:
        """ Calculates distance of a point to polygon boundary. Correct calculations require conversion to cartesian coordinates""" 
        if self.multipolygon.contains(point):
            p1, p2 = nearest_points(self.boundary, point)
        else:
            p1, p2 = nearest_points(self.multipolygon, point)    
        coords_1 = (p1.y, p1.x)
        coords_2 = (p2.y, p2.x)
        return geopy.distance.geodesic(coords_1, coords_2).km    

    def distance_from_centroid(self, point : Point):
        """ Calculates distance of a point to polygon centroid. Correct calculations require conversion to cartesian coordinates """ 
        coords_1 = (self.centroid.y, self.centroid.x)
        coords_2 = (point.y, point.x)
        return geopy.distance.geodesic(coords_1, coords_2).km
    


class ProbabilityFunctionBuilder:
    """Class containing utility fuctions for sceario definations."""
    
    
    def __init__(self, dist, params):
        """Constructor for BaseScenario class.

        Args:
            dist (str): Name of teh distribution. Should follow Scipy naming convention
            params (list): A list of parameters for the chosen distribution function. See Scipy.stats documentation
        """
        
        self.dist = getattr(stats, dist)
        self.params = params
        return 

    def sample(self):
        """Sample the distribution """
        return self.dist.rvs(*self.params, size=1)[0]

    def plot_cdf(self, x:np.linspace, ax =None, label="") -> None:
        """Plot the cumalative distribution fuction"""
        cdf = self.dist.cdf
        if ax is None:
            plt.plot(x,cdf(x, *self.params), label=label)
        else:
            ax.plot(x,cdf(x, *self.params), label=label)
    

    def probability(self, value: float) -> float:
        """Calculates survival probability of a given asset.

        Args:
            value (float): value for vetor of interest. Will change with scenarions
        """
        cdf = self.dist.cdf
        return cdf(value, *self.params)