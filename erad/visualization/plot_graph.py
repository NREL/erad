""" Module for handling graph plots. """

# standard imports
import os
import abc
from typing import List, Dict

# third-party libraries
import networkx as nx
import plotly.graph_objects as go
from dotenv import load_dotenv

# internal libraries
from erad.utils.util import path_validation

load_dotenv()


class AbstractGraphPlot(abc.ABC):
    """Abstract interface for developing subclass to plot network graph."""

    @abc.abstractmethod
    def add_network_data(self, *args, **kwargs):
        """Abstract method for adding network data."""

    @abc.abstractmethod
    def prepare_plot(self, *args, **kwargs):
        """Abstract method for preparing and showing teh plot"""


class PloltyGraph(AbstractGraphPlot):
    """Class for managing graph plot using Plotly.

    Attributes:
        access_token (str): MapBox API token
        style (str): MapBox style
        zoom_level (int): Zoom level for the plot
        data (List): Stores the data to be fed to plotly for plotting
        scatter_data (Dict): Stores longitudes and latitudes of nodes
            from network
        fig (go.Figure): Plotly graph objects figure instance
    """

    def __init__(
        self,
        access_token: str = None,
        style: str = "carto-darkmatter",
        zoom_level: int = 13,
    ) -> None:
        """Constructor for `PlotlyGraph` Subclass.

        Args:
            access_token (str): MapBox API token
            style (str): MapBox style
            zoom_level (int): Zoom level for the plot
        """

        if access_token:
            self.access_token = access_token
        else:
            self.access_token = os.getenv("MAPBOX_API_KEY")
        self.style = style
        self.zoom_level = zoom_level

        self.data = []

    def _get_map_centre(self, longitudes: List[float], latitudes: List[float]):
        """Returns map center."""
        return {
            "lon": sum(longitudes) / len(longitudes),
            "lat": sum(latitudes) / len(latitudes),
        }

    def add_network_data(
        self,
        network: nx.Graph,
        latitude_property: str = "lat",
        longitude_property: str = "long",
        node_color: str = "blue",
        line_color: str = "red",
    ) -> None:
        """Method to add network data to plot data.

        Args:
            network (nx.Graph): Networkx graph instance
            latitude_property (str): Property name to be
                used as latitude
            longitude_property (str): Property name to be
                used as longitude
            node_color (str): Color name to be used to plot
                nodes
            line_color (str): Color name to be used to plot
                line segments
        """

        # Add nodes
        self.scatter_data = {"latitudes": [], "longitudes": []}

        for node in network.nodes.data():

            # Storing the lat lons in scatter data
            # container
            self.scatter_data["latitudes"].append(node[1][latitude_property])
            self.scatter_data["longitudes"].append(node[1][longitude_property])

        # Stroing the edge data in container
        line_data = {"latitudes": [], "longitudes": []}
        node_data = {node[0]: node[1] for node in network.nodes.data()}

        for edge in network.edges():
            line_data["latitudes"].extend(
                [
                    node_data[edge[0]][latitude_property],
                    node_data[edge[1]][latitude_property],
                    None,
                ]
            )

            line_data["longitudes"].extend(
                [
                    node_data[edge[0]][longitude_property],
                    node_data[edge[1]][longitude_property],
                    None,
                ]
            )

        # Adding plots to plotly graph object
        self.data.append(
            go.Scattermapbox(
                mode="markers",
                lon=self.scatter_data["longitudes"],
                lat=self.scatter_data["latitudes"],
                marker={"size": 5, "color": node_color},
            )
        )

        self.data.append(
            go.Scattermapbox(
                mode="markers+lines",
                lon=line_data["longitudes"],
                lat=line_data["latitudes"],
                marker={"size": 0},
                line={"color": line_color},
            )
        )

    def add_scatter_points(
        self,
        latitudes: List[float],
        longitudes: List[float],
        color: str = "yellow",
        size: int = 5,
    ) -> None:
        """Method for scatter points to plot data.

        Args:
            latitudes (List[float]): List of latitude points
            longitudes (List[float]): List of longitude points
            color (str): Color to be used for scatter points
            size (int): Size of scatter points
        """

        self.data.append(
            go.Scattermapbox(
                mode="markers",
                lon=longitudes,
                lat=latitudes,
                marker={"size": size, "color": color},
            )
        )

    def add_polygon(
        self,
        latitudes: List[float],
        longitudes: List[float],
        fill: str = "toself",
    ) -> None:
        """Method for adding polygon to the plot.

        Args:
            latitudes (List[float]): List of latitude points
            longitudes (List[float]): List of longitude points
            fill (str): Accepted fill value by plotly
        """
        self.data.append(
            go.Scattermapbox(
                lon=longitudes, lat=latitudes, fill=fill, mode="lines"
            )
        )

    def prepare_plot(self, show: bool = True):
        """Method to prepare and show the plot.

        Args:
            show (bool): True if want to see the plot.
        """
        self.fig = go.Figure(data=self.data)
        self.fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        self.fig.update_mapboxes(
            {
                "accesstoken": self.access_token,
                "style": self.style,
                "center": self._get_map_centre(
                    self.scatter_data["longitudes"],
                    self.scatter_data["latitudes"],
                ),
                "zoom": self.zoom_level,
            }
        )

        if show:
            self.fig.show()

    def html_export(self, html_file_path: str):
        """Method for exporting plot as HTML file."""
        path_validation(html_file_path)
        self.fig.write_html(html_file_path)

