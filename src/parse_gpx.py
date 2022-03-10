# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 14:08:47 2022

@author: c740
"""
import os
import pandas as pd
import logging
from pathlib import Path
import gzip
from typing import Dict, Union, Optional
from datetime import datetime, timedelta
import dateutil.parser as dp
import gpxpy
import gpxpy.gpx

def get_gpx_point_data(point: gpxpy.gpx.GPXTrackPoint) -> \
                                Dict[str, Union[float, datetime, int]]:
    """Return a tuple containing some key data about `point`."""
    ns = {'garmin_tpe': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}
    data = {
        'latitude': point.latitude,
        'longitude': point.longitude,
        'altitude': point.elevation,
        'timestamp': point.time
    }

    # Parse extensions for heart rate and cadence data, if available
    try:
        elem = point.extensions[0]  # Assuming we know there is only one extension
        try:
            data['heart_rate'] = int(elem.find('garmin_tpe:hr', ns).text)
        except AttributeError:
            # "text" attribute not found, so data not available
            pass
            
        try:
            data['cadence'] = int(elem.find('garmin_tpe:cad', ns).text)
        except AttributeError:
            pass
    except:
        pass
    return(data)


def create_dfs(file_obj, activity_cols, points_cols, laps_cols):
    activity_data = {}
    points_data = []
    laps_data = []
    # lap_no = 1
    
    gpx = gpxpy.parse(file_obj)
    # TODO check if there are more than one track or segment.
    # segment = gpx.tracks[0].segments[0]  # Assuming we know that there is only one track and one segment
    # points_data = [get_gpx_point_data(point) for point in segment.points]
    for segment in gpx.tracks[0].segments:
        points_data = points_data + [get_gpx_point_data(point) for point in segment.points]
   
    laps = pd.DataFrame(laps_data, columns=laps_cols)
    laps.set_index('number', inplace=True)
    # 
    points = pd.DataFrame(points_data, columns=points_cols)
    # 
    activity_data['avg_latitude'] = points.latitude.mean()
    activity_data['avg_longitude'] = points.longitude.mean()
    if not laps.empty:
        activity_data['total_distance'] = sum(laps['total_distance'])
        activity_data['start_time'] = min(laps['start_time'])
        activity_data['total_elapsed_time'] = laps['total_elapsed_time'].sum()
    activity = pd.DataFrame(activity_data,
                            columns=activity_cols,
                            index=[0])
    return(activity, laps, points)

        