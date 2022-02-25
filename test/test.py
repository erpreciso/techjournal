# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 08:42:11 2022

@author: c740

"""
import sys
sys.path.append('../src')
import parse_fit
import render_track


f = 'Move_2014_04_04_18_20_11_Running.fit'

def test_render_map(f):
    laps, points = parse_fit.get_dataframes(f)
    import webbrowser
    mymap = render_track.create_map_with_track(points)
    mymap.save("mymap.html")
    webbrowser.open("mymap.html")

# test_render_map(f)

# fileid, laps, points = parse_fit.get_dataframes(f)

print(parse_fit.get_session_info(f))


