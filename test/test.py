# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 08:42:11 2022

@author: c740

TODO

add dependencies: https://stackoverflow.com/questions/62408719/download-dependencies-declared-in-pyproject-toml-using-pip
logging

WHERE DID I LEFT
read what is flask to embed multiple maps in a single html page


"""
import sys
import os
import webbrowser
import dominate
import dominate.tags as dom

sys.path.append('../src')
import parse_fit
import render_track

folder_name = 'C:\\dev\\techjournal\\data'
f = 'Move_2014_04_04_18_20_11_Running.fit'

def test_render_map(f):
    laps, points = parse_fit.get_dataframes(f)
    import webbrowser
    mymap = render_track.create_map_with_track(points)
    mymap.save("mymap.html")
    webbrowser.open("mymap.html")

# test_render_map(f)

# fileid, laps, points = parse_fit.get_dataframes(f)

# x = parse_fit.get_session_info(f)

laps, points = parse_fit.get_dataframes(f)
mymap = render_track.create_map_with_track(points)
# mymap.save("mymap.html")
# webbrowser.open("mymap.html")

doc = dominate.document(title='map-collection')

with doc.head:
    dom.link(rel='stylesheet', href='style.css')
    dom.script(type='text/javascript', src='script.js')

with doc:
    with dom.div(id='header').add(dom.ol()):
        for i in ['home', 'about', 'contact']:
            dom.li(dom.a(i.title(), href='/%s.html' % i))

    with dom.div():
        dom.attr(cls='body')
        dom.p('Lorem ipsum..')
    
    dom.div(mymap.render())


with open('doc.html', "w") as a_file:
   a_file.write(doc.render())
webbrowser.open('doc.html')


max_files, counter = 10, 0
directory = os.fsencode(folder_name)

for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".fit") and counter < max_files: 
         # print(os.path.join(folder_name, filename))
         counter += 1
         continue
     else:
         continue


