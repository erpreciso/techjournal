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

folder_name = 'C:\\dev\\techjournal\\data\\pics'

from PIL import Image

size = (256, 256)

for infile in os.listdir(folder_name):
    outfile = os.path.splitext(infile)[0] + ".thumbnail"
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                print(infile, im.format, f"{im.size}x{im.mode}")
                im.thumbnail(size)
                im.save(outfile, "JPEG")
        except OSError:
            print("cannot create thumbnail for", infile)

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

# import geopandas

# f = '../data/planet_8.16,45.32_9.741,46.051.osm.geojson.xz'
# 