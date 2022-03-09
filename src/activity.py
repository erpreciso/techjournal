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

LOG_TO_FILE = False

import os
import pandas as pd
import logging
from pathlib import Path
import gzip
import fitdecode
from typing import Dict, Union, Optional
from datetime import datetime, timedelta
from lxml import etree
import dateutil.parser as dp



import src.parser as parser
import src.helpers as h

if LOG_TO_FILE:
    logging.basicConfig(filename='log.log',
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

class ActivityFile():
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_extension = self._get_extension()
        self.laps = pd.DataFrame()
        self.points = pd.DataFrame()
        self.activity = {}
    
    def _get_extension(self):
        suffixes = Path(self.file_path).suffixes
        return(''.join(suffixes))
    
    POINTS_COLUMN_NAMES = ['latitude',
                           'longitude',
                           'lap',
                           'altitude',
                           'timestamp',
                           'heart_rate',
                           'cadence',
                           'speed']
    LAPS_COLUMN_NAMES = ['number',
                         'start_time',
                         'total_distance',
                         'total_elapsed_time',
                         'max_speed',
                         'max_heart_rate',
                         'avg_heart_rate']
    SUMMARY_COLUMN_NAMES = ['start_time',
                            'sport',
                            'total_distance',
                            'total_elapsed_time']
    NAMESPACES = {
        'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
        'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
    }
    
    def _get_fit_point_data(self, frame: fitdecode.records.FitDataMessage) -> \
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
            data['latitude'] = frame.get_value('position_lat') / ((2**32) / 360)
            data['longitude'] = frame.get_value('position_long') / ((2**32) / 360)
        
        for field in self.POINTS_COLUMN_NAMES[3:]:
            if frame.has_field(field):
                data[field] = frame.get_value(field)
        return(data)
    
    def _get_fit_lap_data(self, frame: fitdecode.records.FitDataMessage) -> \
                                Dict[str, Union[float, datetime, timedelta, int]]:
        """Extract data from a FIT frame representing a lap and return
        it as a dict.
        """
        data: Dict[str, Union[float, datetime, timedelta, int]] = {}
        for field in self.LAPS_COLUMN_NAMES[1:]:
            # Exclude 'number' (lap number) because we don't get that
            # from the data but rather count it ourselves
            if frame.has_field(field):
                data[field] = frame.get_value(field)
        return(data)
    
    def _get_tcx_lap_data(self, lap: etree._Element) -> \
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
        
        distance_elem = lap.find('ns:DistanceMeters', self.NAMESPACES)
        if distance_elem is not None:
            data['total_distance'] = float(distance_elem.text)
        
        total_time_elem = lap.find('ns:TotalTimeSeconds', self.NAMESPACES)
        if total_time_elem is not None:
            data['total_elapsed_time'] = \
                        timedelta(seconds=float(total_time_elem.text))
        
        max_speed_elem = lap.find('ns:MaximumSpeed', self.NAMESPACES)
        if max_speed_elem is not None:
            data['max_speed'] = float(max_speed_elem.text)
        
        max_hr_elem = lap.find('ns:MaximumHeartRateBpm', self.NAMESPACES)
        if max_hr_elem is not None:
            data['max_heart_rate'] = \
                    float(max_hr_elem.find('ns:Value', self.NAMESPACES).text)
        
        avg_hr_elem = lap.find('ns:AverageHeartRateBpm', self.NAMESPACES)
        if avg_hr_elem is not None:
            data['avg_heart_rate'] = \
                    float(avg_hr_elem.find('ns:Value', self.NAMESPACES).text)
        return(data)

    def _get_tcx_point_data(self, point: etree._Element) -> \
                Optional[Dict[str, Union[float, int, str, datetime]]]:
        """Extract some data from an XML element representing a track point
        and return it as a dict.
        """
        
        data: Dict[str, Union[float, int, str, datetime]] = {}
        
        position = point.find('ns:Position', self.NAMESPACES)
        if position is None:
            # This Trackpoint element has no latitude or longitude data.
            # For simplicity's sake, we will ignore such points.
            return None
        else:
            data['latitude'] = float(position.find('ns:LatitudeDegrees',
                                                   self.NAMESPACES).text)
            data['longitude'] = float(position.find('ns:LongitudeDegrees',
                                                    self.NAMESPACES).text)
        
        time_str = point.find('ns:Time', self.NAMESPACES).text
        data['timestamp'] = dp.parse(time_str)
            
        elevation_elem = point.find('ns:AltitudeMeters', self.NAMESPACES)
        if elevation_elem is not None:
            data['altitude'] = float(elevation_elem.text)
        
        hr_elem = point.find('ns:HeartRateBpm', self.NAMESPACES)
        if hr_elem is not None:
            data['heart_rate'] = int(hr_elem.find('ns:Value',
                                                  self.NAMESPACES).text)
            
        cad_elem = point.find('ns:Cadence', self.NAMESPACES)
        if cad_elem is not None:
            data['cadence'] = int(cad_elem.text)
        
        # The ".//" here basically tells lxml to search recursively down 
        # the tree for the relevant tag, rather than just the
        # immediate child elements of speed_elem.
        # See https://lxml.de/tutorial.html#elementpath
        speed_elem = point.find('.//ns3:Speed', self.NAMESPACES)
        if speed_elem is not None:
            data['speed'] = float(speed_elem.text)
        
        return(data)
    
    def parse(self):
        logging.info('Parsing file: ' + self.file_name)
        points_data = []
        laps_data = []
        lap_no = 1
        if self.file_extension == '.fit':
            with fitdecode.FitReader(self.file_path) as fit_file:
                for frame in fit_file:
                    if isinstance(frame, fitdecode.records.FitDataMessage):
                        if frame.name == 'record':
                            single_point_data = self._get_fit_point_data(frame)
                            if single_point_data is not None:
                                single_point_data['lap'] = lap_no
                                points_data.append(single_point_data)
                        elif frame.name == 'lap':
                            single_lap_data = self._get_fit_lap_data(frame)
                            single_lap_data['number'] = lap_no
                            laps_data.append(single_lap_data)
                            lap_no += 1
                        elif frame.name == 'session':
                            if frame.has_field('sport'):
                                self.activity['sport'] =  \
                                                frame.get_value('sport')
        elif self.file_extension == '.tcx.gz':
            with gzip.open(self.file_path,'r') as decompressed:
                xml_string = decompressed.read().lstrip()
                root = etree.fromstring(xml_string)
                activity = root.find('ns:Activities', self.NAMESPACES)[0]
                # Assuming we know there is only one Activity in the TCX file
                # (or we are only interested in the first one)
                self.activity['sport'] = activity.get('Sport')
                for lap in activity.findall('ns:Lap', self.NAMESPACES):
                    # Get data about the lap itself
                    single_lap_data = self._get_tcx_lap_data(lap)
                    single_lap_data['number'] = lap_no
                    laps_data.append(single_lap_data)
                    
                    # Get data about the track points in the lap
                    track = lap.find('ns:Track', self.NAMESPACES) 
                    for point in track.findall('ns:Trackpoint',
                                               self.NAMESPACES):
                        single_point_data = self._get_tcx_point_data(point)
                        if single_point_data:
                            single_point_data['lap'] = lap_no
                            points_data.append(single_point_data)
                    lap_no += 1
        self.laps = pd.DataFrame(laps_data,
                                 columns=self.LAPS_COLUMN_NAMES)
        self.laps.set_index('number', inplace=True)
        self.points = pd.DataFrame(points_data,
                                   columns=self.POINTS_COLUMN_NAMES)
        self.activity['total_distance'] = sum(self.laps['total_distance'])
        self.activity['start_time'] = min(self.laps['start_time'])
        self.activity['total_elapsed_time'] = \
                                    self.laps['total_elapsed_time'].sum()
    
folder_name = 'C:\\dev\\techjournal\\data'
file_name = '911320533.tcx.gz'
# file_name = 'Move_2014_04_04_18_20_11_Running.fit'
f = Path(os.path.join(folder_name, file_name))

a = ActivityFile(f)
a.parse()
print(a.laps.T)
print(a.points.T)
print(a.activity)
    
    
class Activity():
    def __init__(self, source_file_path: str):
        logging.info('Init activity')
        # metadata
        self.source_file_path = source_file_path
        self.file_name = os.path.basename(source_file_path)
        self.file_extension = self._get_extension()
        self.id = None
        # activity data
        self.activity = {}
        # self.what = None
        # self.when = None
        # self.length = None
        # self.duration = None
        # self.timer_time = None
        # self.moving_time = None
        # self.avg_latitude = None
        # self.avg_longitude = None
        # track data
        self.laps = pd.DataFrame()
        self.points = pd.DataFrame()
    
    def _get_extension(self):
        suffixes = Path(self.source_file_path).suffixes
        return(''.join(suffixes))
    
    def get_hash(self):
        return(hash(self))
    
    def to_dataframe(self):
        dct = {}
        for key, value in vars(self).items():
            if key not in ['id', 'points']:
                dct[key] = value
        res = pd.DataFrame(dct, index=[self.id])
        return(res)
    
    def create(self):
        logging.info('Creating activity from file ' + self.file_name)
        session_info = parser.extract_activity_info(self.file_path)
        # self.when = session_info['start_time'].strftime('%A %d %B %Y %H:%M')
        self.when = session_info['start_time'].strftime('%Y-%m-%d %H:%M')
        self.what = session_info['sport']
        self.length = h.pretty_length(meters=session_info['total_distance'])
        self.duration = h.pretty_duration(s=session_info['total_elapsed_time'],
                                     light=True)
        self.timer_time = h.pretty_duration(s=session_info['total_timer_time'],
                                       light=True)
        self.moving_time = h.pretty_duration(
                                        s=session_info['total_moving_time'],
                                        light=True)
        self.id = self.get_hash()
        
    def get_location_data(self):
        logging.info('Get location and points of activity')
        laps, points = parser.get_fit_dataframes(self.file_path)
        self.avg_latitude = points.latitude.mean()
        self.avg_longitude = points.longitude.mean()
        points = points.assign(id=self.id)  #add hash as id
        self.points = points

    
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
            logging.info('self.data not empty. Checking filename present')
            result = file_name in self.data.file_name.values
            logging.info('Filename present: ' + str(result))
            return(result)

    def build_from_folder(self, folder, n=3):
        """Iterate files in the folder, and create dataframe of results."""
        max_files, counter = n, 0
        directory = os.fsencode(folder)
        logging.info('Building database from folder ' + folder)
        for file in os.listdir(directory):
            file_name = os.fsdecode(file)
            if file_name.endswith(".fit") and counter < max_files:
                file_path = os.path.join(folder, file_name)
                if not self.check_activity_in_database(file_name):
                    session = Activity()
                    session.create_from_file(file_path)
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
                logging.info('Pickle not found. Writing an empty dataframe')
                self.data.to_pickle(self.data_pickle)
                self.points.to_pickle(self.points_pickle)

    def save_to_pickle(self):
        logging.info('Saving data to pickle')
        self.data.to_pickle(self.data_pickle)
        self.points.to_pickle(self.points_pickle)
