# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 12:13:18 2022

@author: c740
from: https://towardsdatascience.com/build-interactive-gps-activity-maps-from-gpx-files-using-folium-cf9eebba1fe7
"""


import folium
import pandas

def extract_list_of_tuples(points:pandas.DataFrame) -> list():
    route = []
    for idx, row in points.iterrows():
        route.append(tuple([row.latitude, row.longitude]))
    return(route)

def create_map_with_track(points:pandas.DataFrame) -> folium.Map():
    """Create a map and display the track from the dataframe.
    Args:
      points: A dataframe from a fit file.
    Returns:
      A folium map object.
    """
    mymap = folium.Map(location=[points.latitude.mean(),
                                 points.longitude.mean()],
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
    route = extract_list_of_tuples(points)
    folium.PolyLine(route,
                    color='red',
                    weight=4.5,
                    opacity=.5).add_to(mymap)
    return(mymap)
