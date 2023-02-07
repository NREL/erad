""" Module for storing pydantic model for injecting scenarios. """

from typing import Dict
import datetime

from pydantic import BaseModel, validator, confloat


class PointEarthquake(BaseModel):
    longitude: confloat(ge=-180, le=180)
    latitude: confloat(ge=-90, le=90)
    probability_model: Dict
    timestamp: datetime.datetime
    magnitude: confloat(ge=0, le=10)
    depth: confloat(ge=0)
