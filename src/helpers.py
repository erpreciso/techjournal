# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 07:36:17 2022

@author: c740
"""

import datetime as dt
import pandas as pd
import math


def pretty_duration(s: float, fmt='{}h:{}m:{}s', light=False) -> str:
    if math.isnan(s):
        return('Not a number')
    turnaround = dt.timedelta(seconds=s)
    total_seconds = int(turnaround.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    if light:
        return('{}h:{}m'.format(hours,minutes))
    else:
        return(fmt.format(hours,minutes,seconds))

def pretty_length(meters, fmt='{}km') -> str:
    rounded = round(meters/1000, ndigits=1)
    return(fmt.format(rounded))

def get_location_description(lat, lon) -> str:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="app")
    location = geolocator.reverse([lat, lon])
    return(location)
