# -*- coding: utf-8 -*-
""" Defines the Activity and Activities classes and methods.

An Activity is a unit of the techjournal; this module defines methods to 
import them from files and return metadata and tracks in dataframes.

From `towardsdatascience`_ blog

.. _towardsdatascience`:
   https://towardsdatascience.com/\
       parsing-fitness-tracker-data-with-python-a59e7dc17418

https://github.com/polyvertex/fitdecode
https://github.com/bunburya/fitness_tracker_data_parsing/blob/main/parse_fit.py
"""

LOG_TO_FILE = True

import os
import pandas as pd
import logging
from pathlib import Path
import parse_activity_file


# import src.parser as parser
import helpers as h

if LOG_TO_FILE:
    logging.basicConfig(filename='log.log',
                        filemode="w",
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)
    
    
class Activity():
    def __init__(self):
        logging.info('Init activity')
        # metadata
        self.source_file_path = None
        self.source_file_name = None
        self.source_file_extension = None
        self.id = None
        self.activity = pd.DataFrame()
        self.laps = pd.DataFrame()
        self.points = pd.DataFrame()
    
    def _get_extension(self):
        suffixes = Path(self.source_file_path).suffixes
        return(''.join(suffixes))
    
    def define_source_file(self, source_file_path: str):
        self.source_file_path = source_file_path
        self.source_file_name = os.path.basename(source_file_path)
        self.source_file_extension = self._get_extension()
    
    def get_hash(self):
        return(hash(self))
    

    def create_from_file(self):
        """Parse source and create the activity, data and points dataframes.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        
        Args:
            self.source_file_path: source file path.
            self.source_file_name: source file name.
            self.source_file_extension: source file extension.
        
        Returns:
            Create self.points, self.laps, self.activity.
        
        """
        logging.info('Parsing file: ' + self.source_file_name)
        file_path = self.source_file_path
        activity, laps, points = parse_activity_file.parse_file(file_path)
        self.id = self.get_hash()
        if not laps.empty:
            laps = laps.assign(activity_id=self.id)
        points = points.assign(activity_id=self.id)  #add hash as id
        activity = activity.assign(activity_id=self.id,
                                    avg_latitude=points.latitude.mean(),
                                    avg_longitude=points.longitude.mean(),
                                    source_file_path=self.source_file_path,
                                    source_file_name=self.source_file_name)
        self.activity, self.laps, self.points = activity, laps, points
        
    def get_start_time(self):
        return(self.activity['start_time'].strftime('%Y-%m-%d %H:%M'))
    
    def get_sport(self):
        return(self.activity['sport'])
    
    def get_total_distance(self):
        return(h.pretty_length(meters=self.activity['total_distance']))
    
    def get_total_elapsed_time(self):
        seconds = self.activity['total_elapsed_time'].values[0]
        return(h.pretty_duration(s=seconds, light=True))
    
class Activities():
    def __init__(self, reset=False):
        """Initialize the database.
        
        Args:
            reset: to reset the pickles.
        
        Returns:
            The three self.dataframes.
        """
        self.activities = pd.DataFrame()
        self.laps = pd.DataFrame()
        self.points = pd.DataFrame()
        self.pickles = {'laps': '../laps.pickle',
                        'points': '../points.pickle',
                        'activities': '../activities.pikle'}
        if reset:
            self.save_to_pickle()
        else:
            self.load_from_pickle()
    
    def _get_pickle_name(self, which: str) -> str:
        return(self.pickles[which])
    
    def load_from_pickle(self):
        try:
            logging.info('Retrieving from pickle')
            self.activities = pd.read_pickle(self._get_pickle_name('activities'))
            self.laps = pd.read_pickle(self._get_pickle_name('laps'))
            self.points = pd.read_pickle(self._get_pickle_name('points'))
        except(FileNotFoundError):
            logging.info('Pickle not found')
                    
    def save_to_pickle(self):
        logging.info('Saving data to pickle')
        self.activities.to_pickle(self._get_pickle_name('activities'))
        self.laps.to_pickle(self._get_pickle_name('laps'))
        self.points.to_pickle(self._get_pickle_name('points'))
    
    def check_activity_in_database(self,
                                   activity_id=None,
                                   file_name=None):
        logging.info('Checking activity in database:')
        if self.activities.empty:
            logging.info('self.activities is empty')
            result = False
        elif activity_id:
            logging.info('  activity_id: ' + activity_id)
            result = activity_id in self.activities.activity_id.values
            logging.info('activity_id present: ' + str(result))
        elif file_name:
            logging.info('  filename: ' + file_name)
            result = file_name in self.activities['source_file_name'].values
            logging.info('filename present: ' + str(result))
        else:
            logging.error('  no data to check!')
            result = False
        return(result)

    def build_from_folder(self, folder, n=3):
        """Iterate files in the folder, and create dataframe of results."""
        max_files, counter = n, 0
        directory = os.fsencode(folder)
        logging.info('Building database from folder ' + folder)
        for file in os.listdir(directory):
            file_name = os.fsdecode(file) 
            if counter < max_files:
                file_path = os.path.join(folder, file_name)
                if not self.check_activity_in_database(file_name=file_name):
                    session = Activity()
                    session.define_source_file(file_path)
                    session.create_from_file()
                    # session_activity_df = session.get_summary()
                    self.activities = pd.concat([self.activities,
                                                 session.activity],
                                          # ignore_index=True,
                                          )
                    self.points = pd.concat([self.points, session.points],
                                           ignore_index=True,
                                          )
                    self.laps = pd.concat([self.laps, session.laps],
                                           ignore_index=True,
                                          )
                counter += 1
        self.save_to_pickle()
    
    
folder_name = 'C:\\dev\\techjournal\\data'
# file_name = '911320533.tcx.gz'
# file_name = '1049737836.gpx.gz'
file_name = 'Move_2014_04_04_18_20_11_Running.fit'
f = Path(os.path.join(folder_name, file_name))


# a = Activity()
# a.define_source_file(f)
# a.create_from_file()
# print(a.laps.T)
# print(a.points.T)x
# print(a.get_sport())
# print(a.get_total_elapsed_time())

db = Activities()
db.load_from_pickle()
db.build_from_folder(folder_name, n=3)