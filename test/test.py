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
# import src.parser as parser
# import render_track


#%% Images


# from PIL import Image

# size = (256, 256)

# for infile in os.listdir(folder_name):
#     outfile = os.path.splitext(infile)[0] + ".thumbnail"
#     if infile != outfile:
#         try:
#             with Image.open(infile) as im:
#                 pass
#                 # print(infile, im.format, f"{im.size}x{im.mode}")
#                 # im.thumbnail(size)
#                 # im.save(outfile, "JPEG")
#         except OSError:
#             pass
#             # print("cannot create thumbnail for", infile)
#%%

folder_name = 'C:\\dev\\techjournal\\data'
file_name = '911320533.tcx'
from pathlib import Path

f = Path(os.path.join(folder_name, file_name))
# fp = tempfile.TemporaryFile()


print(f.suffixes)


    
# fp.write(file_content)
# l, p = parser.get_tcx_dataframes(xml[10:])

# nsmap = {}
# for ns in doc.xpath('//namespace::*'):
#     if ns[0]: # Removes the None namespace, neither needed nor supported.
#         nsmap[ns[0]] = ns[1]
# doc.xpath('//prefix:element', namespaces=nsmap)