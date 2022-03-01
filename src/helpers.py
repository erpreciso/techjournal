# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 07:36:17 2022

@author: c740
"""

import datetime as dt
import pandas as pd

def look_up(lat, lon):
    search = pd.DataFrame({'lat': [lat], 'Lon': [lon]})
    res = pd.merge(search, get_pickle())['Result']
    if not res.empty:
        return(res[0])
    return(None)

def get_pickle(pickle_file):
    return(pd.read_pickle(pickle_file))

def save_to_pickle(pickle_file, lat, lon, result):
    to_save = pd.DataFrame({'lat': [lat], 'Lon': [lon], 'Result': [result]})
    pd.concat([to_save, get_pickle()], ignore_index=True).to_pickle(pickle_file)
    

def create_pickle(pickle_file):
    pd.DataFrame({'lat': [], 'Lon': [], 'Result': []}).to_pickle(pickle_file)

def pretty_duration(s, fmt='{}h:{}m:{}s', light=False) -> str:
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

# x = get_location_description(52.509669, 13.376294)
# x = get_location_description(52.50, 13.37)


# print(x)