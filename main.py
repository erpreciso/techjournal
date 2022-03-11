# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 06:20:30 2022

@author: c740

TODO add cache for the db
TODO install geopandas and code location in another cache file
TODO use PIL to create thumbnails https://pillow.readthedocs.io/en/stable/handbook/tutorial.html#reading-and-writing-images
"""


import src.activity as activity
import src.render_track as track
import configs.config as config
import logging



from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return(render_template('base.html',
           links=config.LINKS))

@app.route('/activities', methods=['GET', 'POST'])
def activities_index():
    # TODO add an index on the left
    db = activity.Activities(reset=False)
    db.load_from_pickle()
    db.build_from_folder(config.FOLDER_NAME, n=10)
    db.activities['link'] = ['http://localhost:5000/' + str(i) for i in db.activities['activity_id']]
    df = db.activities[['link',
                  'sport',
                  'start_time',
                  'total_distance',
                  'total_elapsed_time',
                  'source_file_name',
                  'avg_latitude',
                  'avg_longitude']]
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            logging.info('Action 1')
            pass # do something
        elif  request.form.get('action2') == 'VALUE2':
            logging.info('Action 2')
            pass # do something else
        else:
            pass # unknown
    elif request.method == 'GET':
        return(render_template('activities_index.html',
                               table=df.to_html(render_links=True)))
    return(render_template('activities_index.html',
                           table=df.to_html(render_links=True)))

@app.route('/<int:track_id>')
def show_track(track_id):
    # create activity summary table
    logging.info('Building database')
    db = activity.Activities(reset=False)
    db.load_from_pickle()
    db.build_from_folder(config.FOLDER_NAME, n=10)
    logging.info('Creating activity points for trackID: ' + str(track_id))
    activity_points = db.points[db.points['activity_id'] == track_id]
    logging.info('Creating map for trackID: ' + str(track_id))
    activity_map = track.create_map_with_track(activity_points)
    map_html = 'maps/' + str(track_id) + '_map.html'
    activity_map.save('templates/' + map_html)
    return(render_template('activity.html',
                           map_template=map_html,
                           # table=df.to_html(render_links=True),
                           ))

if __name__ == '__main__':
    app.run(debug=True)