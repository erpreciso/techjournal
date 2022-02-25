# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 08:42:11 2022

@author: c740

from: https://towardsdatascience.com/parsing-fitness-tracker-data-with-python-a59e7dc17418
"""
import sys
sys.path.append('../src')
import parse_fit

f = 'Move_2014_04_04_18_20_11_Running.fit'

laps, points = parse_fit.get_dataframes(f)


import folium
mymap = folium.Map(location=[points.latitude.mean(), points.longitude.mean()],
                   zoom_start=12,
                   tiles=None,
                   width='50%',
                   height='50%',)
folium.TileLayer('openstreetmap',
                 name='OpenStreet Map').add_to(mymap)
folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
                 attr="Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC",
                 name='Nat Geo Map').add_to(mymap)
folium.TileLayer('http://tile.stamen.com/terrain/{z}/{x}/{y}.jpg',
                 attr="terrain-bcg",
                 name='Terrain Map').add_to(mymap)

route = []
for idx, row in points.iterrows():
    route.append(tuple([row.latitude, row.longitude]))
print(route[1:10])

folium.PolyLine(route, color='red', weight=4.5, opacity=.5).add_to(mymap)


import webbrowser
mymap.save("mymap.html")
webbrowser.open("mymap.html")