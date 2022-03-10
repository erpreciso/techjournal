# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 05:46:05 2022

@author: c740
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Union, Optional
from datetime import datetime, timedelta
from lxml import etree
import dateutil.parser as dp

NAMESPACES = {
    'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
    'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
    'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
}

def get_tcx_lap_data(lap: etree._Element) -> \
                        Dict[str, Union[float, datetime, timedelta, int]]:
    """Extract some data from an XML element representing a lap and
    return it as a dict.
    """
    data: Dict[str, Union[float, datetime, timedelta, int]] = {}
    
    # Note that because each element's attributes and text are returned
    # as strings, we need to convert those strings
    # to the appropriate datatype (datetime, float, int, etc).
    
    start_time_str = lap.attrib['StartTime']
    data['start_time'] = dp.parse(start_time_str)
    
    distance_elem = lap.find('ns:DistanceMeters', NAMESPACES)
    if distance_elem is not None:
        data['total_distance'] = float(distance_elem.text)
    
    total_time_elem = lap.find('ns:TotalTimeSeconds', NAMESPACES)
    if total_time_elem is not None:
        data['total_elapsed_time'] = float(total_time_elem.text)
    
    max_speed_elem = lap.find('ns:MaximumSpeed', NAMESPACES)
    if max_speed_elem is not None:
        data['max_speed'] = float(max_speed_elem.text)
    
    max_hr_elem = lap.find('ns:MaximumHeartRateBpm', NAMESPACES)
    if max_hr_elem is not None:
        if max_hr_elem.find('ns:Value', NAMESPACES).text is not None:
            data['max_heart_rate'] = \
                float(max_hr_elem.find('ns:Value', NAMESPACES).text)
        else:
            data['max_heart_rate'] = 0.0
    
    avg_hr_elem = lap.find('ns:AverageHeartRateBpm', NAMESPACES)
    if avg_hr_elem is not None:
        data['avg_heart_rate'] = \
                float(avg_hr_elem.find('ns:Value', NAMESPACES).text)
    return(data)

def get_tcx_point_data(point: etree._Element) -> \
            Optional[Dict[str, Union[float, int, str, datetime]]]:
    """Extract some data from an XML element representing a track point
    and return it as a dict.
    """
    
    data: Dict[str, Union[float, int, str, datetime]] = {}
    
    position = point.find('ns:Position', NAMESPACES)
    if position is None:
        # This Trackpoint element has no latitude or longitude data.
        # For simplicity's sake, we will ignore such points.
        return None
    else:
        data['latitude'] = float(position.find('ns:LatitudeDegrees',
                                               NAMESPACES).text)
        data['longitude'] = float(position.find('ns:LongitudeDegrees',
                                                NAMESPACES).text)
    
    time_str = point.find('ns:Time', NAMESPACES).text
    data['timestamp'] = dp.parse(time_str)
        
    elevation_elem = point.find('ns:AltitudeMeters', NAMESPACES)
    if elevation_elem is not None:
        data['altitude'] = float(elevation_elem.text)
    
    hr_elem = point.find('ns:HeartRateBpm', NAMESPACES)
    if hr_elem is not None:
        data['heart_rate'] = int(hr_elem.find('ns:Value',
                                              NAMESPACES).text)
        
    cad_elem = point.find('ns:Cadence', NAMESPACES)
    if cad_elem is not None:
        data['cadence'] = int(cad_elem.text)
    
    # The ".//" here basically tells lxml to search recursively down 
    # the tree for the relevant tag, rather than just the
    # immediate child elements of speed_elem.
    # See https://lxml.de/tutorial.html#elementpath
    speed_elem = point.find('.//ns3:Speed', NAMESPACES)
    if speed_elem is not None:
        data['speed'] = float(speed_elem.text)
    
    return(data)

def create_dfs(file_obj, activity_cols, points_cols, laps_cols):
    activity_data = {}
    points_data = []
    laps_data = []
    lap_no = 1
    xml_string = file_obj.read().lstrip()
    root = etree.fromstring(xml_string)
    activity = root.find('ns:Activities', NAMESPACES)[0]
    # Assuming we know there is only one Activity in the TCX file
    # (or we are only interested in the first one)
    activity_data['sport'] = activity.get('Sport')
    for lap in activity.findall('ns:Lap', NAMESPACES):
        # Get data about the lap itself
        single_lap_data = get_tcx_lap_data(lap)
        single_lap_data['number'] = lap_no
        laps_data.append(single_lap_data)
        
        # Get data about the track points in the lap
        track = lap.find('ns:Track', NAMESPACES) 
        for point in track.findall('ns:Trackpoint',
                                   NAMESPACES):
            single_point_data = get_tcx_point_data(point)
            if single_point_data:
                single_point_data['lap'] = lap_no
                points_data.append(single_point_data)
        lap_no += 1
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