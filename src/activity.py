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
import gzip
import fitdecode
from typing import Dict, Union, Optional
from datetime import datetime, timedelta
from lxml import etree
import dateutil.parser as dp
import gpxpy
import gpxpy.gpx


# import src.parser as parser
import helpers as h

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
        # metadata
        self.source_file_path = None
        self.source_file_name = None
        self.source_file_extension = None
        self.id = None
        self.activity = {'sport': None,
                         'start_time': None,
                        'total_distance': None,
                        'total_elapsed_time': None,
                        'avg_latitude': None,
                        'avg_longitude': None,
                        'source_file_path': None,
                        'source_file_name': None,
                        'activity_id': None,
                        }
        self.laps = pd.DataFrame()
        self.points = pd.DataFrame()
    
    def get_summary(self):
        return(pd.DataFrame(self.activity, index=[self.id]))
    
    def _get_extension(self):
        suffixes = Path(self.source_file_path).suffixes
        return(''.join(suffixes))
    
    def define_source_file(self, source_file_path: str):
        self.source_file_path = source_file_path
        self.source_file_name = os.path.basename(source_file_path)
        self.source_file_extension = self._get_extension()
    
    def get_hash(self):
        return(hash(self))
    
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
            if frame.get_value('position_lat') != None:
                data['latitude'] = frame.get_value('position_lat') / ((2**32) / 360)
                data['longitude'] = frame.get_value('position_long') / ((2**32) / 360)
            else:
                # TODO do not save at zero but find another way
                data['latitude'] = 0
                data['longitude'] = 0
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
            data['total_elapsed_time'] = float(total_time_elem.text)
        
        max_speed_elem = lap.find('ns:MaximumSpeed', self.NAMESPACES)
        if max_speed_elem is not None:
            data['max_speed'] = float(max_speed_elem.text)
        
        max_hr_elem = lap.find('ns:MaximumHeartRateBpm', self.NAMESPACES)
        if max_hr_elem is not None:
            if max_hr_elem.find('ns:Value', self.NAMESPACES).text is not None:
                data['max_heart_rate'] = \
                    float(max_hr_elem.find('ns:Value', self.NAMESPACES).text)
            else:
                data['max_heart_rate'] = 0.0
        
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
    
    def _get_gpx_point_data(self, point: gpxpy.gpx.GPXTrackPoint) -> \
                                    Dict[str, Union[float, datetime, int]]:
        """Return a tuple containing some key data about `point`."""
        namespaces = {'garmin_tpe': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}
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
                data['heart_rate'] = int(elem.find('garmin_tpe:hr', namespaces).text)
            except AttributeError:
                # "text" attribute not found, so data not available
                pass
                
            try:
                data['cadence'] = int(elem.find('garmin_tpe:cad', namespaces).text)
            except AttributeError:
                pass
        except:
            pass
        return(data)
    
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
        points_data = []
        laps_data = []
        lap_no = 1
        if self.source_file_extension == '.fit':
            with fitdecode.FitReader(self.source_file_path) as fit_file:
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
        elif self.source_file_extension == '.fit.gz':
            with gzip.open(self.source_file_path,'r') as decompressed:
                with fitdecode.FitReader(decompressed) as fit_file:
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
        elif self.source_file_extension == '.tcx.gz':
            with gzip.open(self.source_file_path,'r') as decompressed:
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
        elif self.source_file_extension == '.gpx.gz': # TODO
            with gzip.open(self.source_file_path,'r') as decompressed:
                gpx = gpxpy.parse(decompressed)
            # TODO check if there are more than one track or segment.
            segment = gpx.tracks[0].segments[0]  # Assuming we know that there is only one track and one segment
            points_data = [self._get_gpx_point_data(point) for point in segment.points]
        self.id = self.get_hash()
        self.laps = pd.DataFrame(laps_data,
                                 columns=self.LAPS_COLUMN_NAMES)
        self.laps.set_index('number', inplace=True)
        self.laps = self.laps.assign(activity_id=self.id)
        self.points = pd.DataFrame(points_data,
                                   columns=self.POINTS_COLUMN_NAMES)
        self.points = self.points.assign(activity_id=self.id)  #add hash as id
        self.activity['avg_latitude'] = self.points.latitude.mean()
        self.activity['avg_longitude'] = self.points.longitude.mean()
        

        self.activity['total_distance'] = sum(self.laps['total_distance'])
        self.activity['start_time'] = min(self.laps['start_time'])
        self.activity['total_elapsed_time'] = \
                                    self.laps['total_elapsed_time'].sum()
        self.activity['source_file_path'] = self.source_file_path
        self.activity['source_file_name'] = self.source_file_name
        self.activity['activity_id'] = self.id
    
    def get_start_time(self):
        return(self.activity['start_time'].strftime('%Y-%m-%d %H:%M'))
    
    def get_sport(self):
        return(self.activity['sport'])
    
    def get_total_distance(self):
        return(h.pretty_length(meters=self.activity['total_distance']))
    
    def get_total_elapsed_time(self):
        return(h.pretty_duration(s=self.activity['total_elapsed_time'],
                                 light=True))
    
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
        self.pickles = {'laps': 'laps.pickle',
                        'points': 'points.pickle',
                        'activities': 'activities.pikle'}
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
            return(False)
        elif activity_id:
            logging.info('  activity_id: ' + activity_id)
            result = activity_id in self.activities.activity_id.values
            logging.info('activity_id present: ' + str(result))
            return(result)
        elif file_name:
            logging.info('  filename: ' + file_name)
            result = file_name in self.activities['source_file_name'].values
            logging.info('filename present: ' + str(result))
            return(result)
        else:
            logging.error('  no data to check!')
            return(False)

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
                    session_activity_df = session.get_summary()
                    self.activities = pd.concat([self.activities,
                                                 session_activity_df],
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
file_name = '1049737836.gpx.gz'
# file_name = 'Move_2014_04_04_18_20_11_Running.fit'
f = Path(os.path.join(folder_name, file_name))


a = Activity()
a.define_source_file(f)
a.create_from_file()
print(a.laps.T)
print(a.points.T)
print(a.get_sport())
print(a.get_total_elapsed_time())

# db = Activities()
# db.load_from_pickle()
# db.build_from_folder(folder_name, n=100)