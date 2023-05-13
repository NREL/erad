""" Module for storing pydantic model for injecting scenarios. """

from typing import Dict, Optional, List
import datetime

from pydantic import BaseModel, validator, confloat


class PointEarthquake(BaseModel):
    longitude: confloat(ge=-180, le=180)
    latitude: confloat(ge=-90, le=90)
    probability_model: Optional[Dict]
    timestamp: datetime.datetime
    magnitude: confloat(ge=0, le=10)
    depth: confloat(ge=0)

class PolygonFlooding(BaseModel):
    polygon: List
    probability_model: Optional[Dict]
    timestamp: datetime.datetime
    file_flow: str 
    file_levels: str 
    file_gaugues: str
