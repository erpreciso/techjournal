# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 06:20:30 2022

@author: c740
"""
LOG_TO_FILE = False

# import sys
import os
import pandas as pd
import logging

import src.parser as parser
import src.helpers as h
import configs.config as config

if LOG_TO_FILE:
    logging.basicConfig(filename='log.log',
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)




class Activity():
    def __init__(self):
        logging.info('Init activity')
        self.what = None
        self.when = None
        self.length = None
        self.duration = None
        self.timer_time = None
        self.moving_time = None
        self.file_name = None
        self.avg_latitude = None
        self.avg_longitude = None
        self.points = pd.DataFrame()
        self.id = None
    
    def get_hash(self):
        return(hash(self))
    
    def to_dataframe(self):
        dct = {}
        for key, value in vars(self).items():
            if key not in ['id', 'points']:
            # if type(value) in [str, float, int]:
                dct[key] = value
        res = pd.DataFrame(dct, index=[self.id])
        return(res)
    
    def create_from_file(self, file_name: str):
        logging.info('Creating activity from file ' + os.path.basename(file_name))
        session_info = parser.get_session_info(file_name)
        # self.when = session_info['start_time'].strftime('%A %d %B %Y %H:%M')
        self.when = session_info['start_time'].strftime('%Y-%m-%d %H:%M')
        self.what = session_info['sport']
        self.length = h.pretty_length(meters=session_info['total_distance'])
        self.duration = h.pretty_duration(s=session_info['total_elapsed_time'],
                                     light=True)
        self.timer_time = h.pretty_duration(s=session_info['total_timer_time'],
                                       light=True)
        self.moving_time = h.pretty_duration(s=session_info['total_moving_time'],
                                        light=True)
        self.file_name = file_name
        self.id = self.get_hash()
        
    def get_location_data(self):
        logging.info('Get location and points of activity')
        laps, points = parser.get_dataframes(self.file_name)
        self.avg_latitude = points.latitude.mean()
        self.avg_longitude = points.longitude.mean()
        points = points.assign(id=self.id)  #add hash as id
        self.points = points

    
    def check_in_database(self, database):
        pass
    
    def save(self, database):
        pass
    
    
    
class ActivityDatabase():
    def __init__(self,
                 data_pickle='activities.pkl',
                 points_pickle='points.pkl',
                 reset=False):
        """Initialize the database."""
        self.data_pickle = data_pickle
        self.points_pickle = points_pickle
        self.data = pd.DataFrame()
        self.points = pd.DataFrame()
        self.retrieve_from_pickle(reset)
    
    def check_activity_in_database(self, file_name: str):
        logging.info('Checking activity in database: filename ' + file_name)
        if self.data.empty:
            logging.info('self.data is empty')
            return(False)
        else:
            logging.info('self.data is not empty. Checking if filename present')
            result = file_name in self.data.file_name.values
            logging.info('Filename present: ' + str(result))
            return(result)
        
    
    def build_from_folder(self, folder, n=3):
        """Iterate files in the folder, and create dataframe of results."""
        max_files, counter = n, 0
        directory = os.fsencode(folder)
        logging.info('Building database from folder ' + folder)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".fit") and counter < max_files:
                f = os.path.join(folder, filename)
                if not self.check_activity_in_database(f):
                    session = Activity()
                    session.create_from_file(f)
                    session.get_location_data()
                    session_df = session.to_dataframe()
                    self.data = pd.concat([self.data, session_df],
                                          # ignore_index=True,
                                          )
                    self.points = pd.concat([self.points, session.points],
                                           ignore_index=True,
                                          )
                counter += 1
        self.save_to_pickle()
    
    def retrieve_from_pickle(self, reset=False):
        if reset:
            logging.info('Resetting pickle')
            self.data.to_pickle(self.data_pickle)
            self.points.to_pickle(self.points_pickle)
        else:
            try:
                logging.info('Retrieving from pickle')
                self.data = pd.read_pickle(self.data_pickle)
                self.points = pd.read_pickle(self.points_pickle)
            except(FileNotFoundError):
                logging.info('Pickle not found. Writing pickle with empty dataframe')
                self.data.to_pickle(self.data_pickle)
                self.points.to_pickle(self.points_pickle)

    def save_to_pickle(self):
        logging.info('Saving data to pickle')
        self.data.to_pickle(self.data_pickle)
        self.points.to_pickle(self.points_pickle)

db = ActivityDatabase(reset=False)
db.build_from_folder(config.FOLDER_NAME, n=5)
print(db.data.iloc[0].T)

# from flask import Flask

# app = Flask(__name__)

# from flask import render_template

# @app.route('/')
# def hello(name=None):
#     return render_template('base.html', name=name)
