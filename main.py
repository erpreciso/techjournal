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

ACTIVITIES_PICKLE = 'activities.pkl'
ACTIVITIES_COLUMNS = ['When',
                      'What',
                      'Length',
                      'Duration',
                      'Timer time',
                      'Moving time',
                      'Start latitude',
                      'Start longitude',
                      'File name',
                      ]

if LOG_TO_FILE:
    logging.basicConfig(filename='log.log',
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)



def get_activity_from_file(file_name: str) -> pd.DataFrame:
    """Parse a fit file and get activity info.
    Returns a pd.DataFrame.
    """
    logging.info('working on file ' + os.path.basename(file_name))
    session_info = parser.get_session_info(file_name)
    # when = session_info['start_time'].strftime('%A %d %B %Y %H:%M')
    when = session_info['start_time'].strftime('%Y-%m-%d %H:%M')
    what = session_info['sport']
    length = h.pretty_length(meters=session_info['total_distance'])
    duration = h.pretty_duration(s=session_info['total_elapsed_time'],
                                 light=True)
    timer_time = h.pretty_duration(s=session_info['total_timer_time'],
                                   light=True)
    moving_time = h.pretty_duration(s=session_info['total_moving_time'],
                                    light=True)
    session = pd.DataFrame({'When': [when],
                            'What': [what],
                            'Length': [length],
                            'Duration': [duration],
                            'Timer time': [timer_time],
                            'Moving time': [moving_time],
                            'File name':[file_name],
                            })
    return(session)

def check_if_activity_is_already_parsed(start_timestamp):
    """Check cache if activity is already parsed."""
    pass

def save_activity(activity: pd.DataFrame) -> bool:
    db = retrieve_activities()
    concat = pd.concat([db, activity], ignore_index=True)
    concat.to_pickle(ACTIVITIES_PICKLE)
    return(True)

def retrieve_activities(reset=False) -> pd.DataFrame:
    """Return the activities database, creating one if not exist."""
    if reset:
        db = pd.DataFrame({}, columns=ACTIVITIES_COLUMNS)
        db.to_pickle(ACTIVITIES_PICKLE)
        return(db)
    try:
        return(pd.read_pickle(ACTIVITIES_PICKLE))
    except(FileNotFoundError):
        db = pd.DataFrame({}, columns=ACTIVITIES_COLUMNS)
        db.to_pickle(ACTIVITIES_PICKLE)
        return(db)


def parse_folder_of_activities(folder, n=3):
    """Iterate files in the folder, and create dataframe of results."""
    max_files, counter = n, 0
    directory = os.fsencode(folder)
    logging.info('working on folder ' + config.FOLDER_NAME)
    db = retrieve_activities()
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".fit") and counter < max_files:
            f = os.path.join(config.FOLDER_NAME, filename)
            if f not in db['File name'].values:
                session = get_activity_from_file(f)
                save_activity(session)
            counter += 1


def create_activities_dataframe(n=3, log_to_file=False):
    """Return dataframe of activities info."""

    df = pd.DataFrame(columns=['When', 'What'])
    max_files, counter = n, 0
    directory = os.fsencode(config.FOLDER_NAME)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".fit") and counter < max_files:
            logging.info('working on file ' + filename)
            f = os.path.join(config.FOLDER_NAME, filename)
            session_info = parser.get_session_info(f)
            # when = session_info['start_time'].strftime('%A %d %B %Y %H:%M')
            when = session_info['start_time'].strftime('%Y-%m-%d %H:%M')
            what = session_info['sport']
            length = h.pretty_length(meters=session_info['total_distance'])
            duration = h.pretty_duration(s=session_info['total_elapsed_time'],
                                         light=True)
            timer_time = h.pretty_duration(s=session_info['total_timer_time'],
                                           light=True)
            moving_time = h.pretty_duration(s=session_info['total_moving_time'],
                                            light=True)
            
            session = pd.DataFrame({'When': [when],
                                    'What': [what],
                                    'Length': [length],
                                    'Duration': [duration],
                                    'Timer time': [timer_time],
                                    'Moving time': [moving_time],
                                    })
            df = pd.concat([df, session], ignore_index=True)
            counter += 1
            continue
        else:
            continue
    return(df)

parse_folder_of_activities(config.FOLDER_NAME, n=3)
x = retrieve_activities()
print(x)

