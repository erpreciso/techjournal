# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 08:42:11 2022

@author: c740

TODO

add dependencies: https://stackoverflow.com/questions/62408719/download-dependencies-declared-in-pyproject-toml-using-pip


"""
import sys
import os

# sys.path.append('../src')
# import parse_fit
# import render_track

folder_name = 'C:\\dev\\techjournal\\data'
f = 'Move_2014_04_04_18_20_11_Running.fit'

# def test_render_map(f):
#     laps, points = parse_fit.get_dataframes(f)
#     import webbrowser
#     mymap = render_track.create_map_with_track(points)
#     mymap.save("mymap.html")
#     webbrowser.open("mymap.html")

# test_render_map(f)

# fileid, laps, points = parse_fit.get_dataframes(f)

# x = parse_fit.get_session_info(f)

# laps, points = parse_fit.get_dataframes(f)
# mymap = render_track.create_map_with_track(points)
# mymap.save("mymap.html")
# webbrowser.open("mymap.html")



# import src.activity as activity
# import configs.config as config

# db = activity.ActivityDatabase(reset=False)
# db.build_from_folder(config.FOLDER_NAME, n=5)

import geopandas

f = '../data/planet_8.16,45.32_9.741,46.051.osm.geojson.xz'
gdf = geopandas.read_file(f)

gdf