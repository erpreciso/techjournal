# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 06:20:30 2022

@author: c740
"""

# import sys
import os
import pandas as pd
import logging

import src.parser as parser
import src.helpers as helper
import configs.config as config


def create_activities_dataframe(n=3, log_to_file=False):
    """Return dataframe of activities info."""
    if log_to_file:
        logging.basicConfig(filename='log.log',
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)
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
            length = helper.pretty_length(meters=session_info['total_distance'])
            duration = helper.pretty_duration(seconds=session_info['total_elapsed_time'], light=True)
            timer_time = helper.pretty_duration(seconds=session_info['total_timer_time'], light=True)
            moving_time = helper.pretty_duration(seconds=session_info['total_moving_time'], light=True)
            
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

print(create_activities_dataframe(n=30))