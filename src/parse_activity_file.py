# -*- coding: utf-8 -*-



"""Some functions for parsing a FIT file (specifically, a FIT file
generated by a Garmin vívoactive 3) and creating a Pandas DataFrame
with the data.
From `towardsdatascience`_ blog

.. _towardsdatascience`:
   https://towardsdatascience.com/\
       parsing-fitness-tracker-data-with-python-a59e7dc17418

https://github.com/polyvertex/fitdecode
https://github.com/bunburya/fitness_tracker_data_parsing/blob/main/parse_fit.py
"""

import parse_fit, parse_tcx, parse_gpx
import pandas as pd
import os.path
from pathlib import Path
import gzip

POINTS_COLUMNS = ['latitude',
                       'longitude',
                       'lap',
                       'altitude',
                       'timestamp',
                       'heart_rate',
                       'cadence',
                       'speed']

LAPS_COLUMNS = ['number',
                     'start_time',
                     'total_distance',
                     'total_elapsed_time',
                     'max_speed',
                     'max_heart_rate',
                     'avg_heart_rate']

ACTIVITY_COLUMNS = ['sport',
                         'start_time',
                         'total_distance',
                         'total_elapsed_time',
                         'avg_latitude',
                         'avg_longitude',
                         'source_file_path',
                         'source_file_name',
                         'activity_id',
                         ]

def get_extension(file_path) -> str:
    suffixes = Path(file_path).suffixes
    return(''.join(suffixes))

def parse_file(file_path):
    laps = pd.DataFrame()
    points = pd.DataFrame()
    if get_extension(file_path) == '.fit':
        activity, laps, points = parse_fit.create_dfs(file_path,
                                                      ACTIVITY_COLUMNS,
                                                      POINTS_COLUMNS,
                                                      LAPS_COLUMNS)
    elif get_extension(file_path) == '.fit.gz':
        with gzip.open(file_path,'r') as file_obj:
            activity, laps, points = parse_fit.create_dfs(file_obj,
                                                      ACTIVITY_COLUMNS,
                                                      POINTS_COLUMNS,
                                                      LAPS_COLUMNS)
    elif get_extension(file_path) == '.tcx.gz':
        with gzip.open(file_path,'r') as file_obj:
            activity, laps, points = parse_tcx.create_dfs(file_obj,
                                                          ACTIVITY_COLUMNS,
                                                          POINTS_COLUMNS,
                                                          LAPS_COLUMNS)
    elif get_extension(file_path) == '.gpx.gz':
        with gzip.open(file_path,'r') as file_obj:
            activity, laps, points = parse_gpx.create_dfs(file_obj,
                                                          ACTIVITY_COLUMNS,
                                                          POINTS_COLUMNS,
                                                          LAPS_COLUMNS)
    return(activity, laps, points)

# folder_name = 'C:\\dev\\techjournal\\data'
# file_name = 'Move_2014_04_04_18_20_11_Running.fit'
# file_name = '911320533.tcx.gz'
# file_name = '1049737836.gpx.gz'
# file_path = Path(os.path.join(folder_name, file_name))

# activity, laps, points = parse_file(file_path)

# print(activity.T)
# print(laps.head(1).T)
# print(points.head(1).T)
