# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 05:40:51 2022

@author: c740
"""

import pandas as pd
import fitdecode
from typing import Dict, Union, Optional
from datetime import datetime, timedelta


def get_fit_point_data(frame: fitdecode.records.FitDataMessage, points_cols) -> \
                Optional[Dict[str, Union[float, int, str, datetime]]]:
    """Extract some data from an FIT frame representing a track point
    and return it as a dict.
    """
    data: Dict[str, Union[float, int, str, datetime]] = {}
    
    if not (frame.has_field('position_lat') and frame.has_field('position_long')):
        # Frame does not have any latitude or longitude data.
        # We will ignore these frames in order to keep things
        # simple, as we did when parsing the TCX file.
        return None
    else:
        if frame.get_value('position_lat') != None:
            data['latitude'] = frame.get_value('position_lat') / ((2**32) / 360)
            data['longitude'] = frame.get_value('position_long') / ((2**32) / 360)
        else:
            # TODO do not save at zero but find another way
            data['latitude'] = 0
            data['longitude'] = 0
    for field in points_cols[3:]:
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    return(data)

def get_fit_lap_data(frame: fitdecode.records.FitDataMessage, laps_cols) -> \
                            Dict[str, Union[float, datetime, timedelta, int]]:
    """Extract data from a FIT frame representing a lap and return
    it as a dict.
    """
    data: Dict[str, Union[float, datetime, timedelta, int]] = {}
    for field in laps_cols[1:]:
        # Exclude 'number' (lap number) because we don't get that
        # from the data but rather count it ourselves
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    return(data)

def create_dfs(file_path, activity_cols, points_cols, laps_cols):
    activity_data = {}
    points_data = []
    laps_data = []
    lap_no = 1
    with fitdecode.FitReader(file_path) as fit_file:
        for frame in fit_file:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                if frame.name == 'record':
                    single_point_data = get_fit_point_data(frame, points_cols)
                    if single_point_data is not None:
                        single_point_data['lap'] = lap_no
                        points_data.append(single_point_data)
                elif frame.name == 'lap':
                    single_lap_data = get_fit_lap_data(frame, laps_cols)
                    single_lap_data['number'] = lap_no
                    laps_data.append(single_lap_data)
                    lap_no += 1
                elif frame.name == 'session':
                    if frame.has_field('sport'):
                        activity_data['sport'] = frame.get_value('sport')
    laps = pd.DataFrame(laps_data, columns=laps_cols)
    laps.set_index('number', inplace=True)
    # 
    points = pd.DataFrame(points_data, columns=points_cols)
    # 
    activity_data['avg_latitude'] = points.latitude.mean()
    activity_data['avg_longitude'] = points.longitude.mean()
    activity_data['total_distance'] = sum(laps['total_distance'])
    activity_data['start_time'] = min(laps['start_time'])
    activity_data['total_elapsed_time'] = laps['total_elapsed_time'].sum()
    activity = pd.DataFrame(activity_data,
                            columns=activity_cols,
                            index=[0])
    return(activity, laps, points)