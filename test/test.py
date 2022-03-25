# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 08:42:11 2022

@author: c740

TODO

add dependencies: https://stackoverflow.com/questions/62408719/download-dependencies-declared-in-pyproject-toml-using-pip


"""
# import sys
# import os

# sys.path.append('../src')
# import src.parser as parser
# import render_track

# import calendar

# for name in calendar.month_name:
#     print(name)

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

# folder_name = 'C:\\dev\\techjournal\\data'
# file_name = '911320533.tcx'
# from pathlib import Path

# f = Path(os.path.join(folder_name, file_name))
# fp = tempfile.TemporaryFile()


# print(f.suffixes)


    
# fp.write(file_content)
# l, p = parser.get_tcx_dataframes(xml[10:])

# nsmap = {}
# for ns in doc.xpath('//namespace::*'):
#     if ns[0]: # Removes the None namespace, neither needed nor supported.
#         nsmap[ns[0]] = ns[1]
# doc.xpath('//prefix:element', namespaces=nsmap)

#%%

import tkinter as tk
from tkinter import ttk
import webbrowser

from tkcalendar import Calendar, DateEntry

def example1():
    def print_sel():
        print(cal.selection_get())

    top = tk.Toplevel(app_window)

    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=2018, month=2, day=5)
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="ok", command=print_sel).pack()

def example2():
    top = tk.Toplevel(app_window)

    ttk.Label(top, text='Choose date').pack(padx=10, pady=10)

    cal = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
    cal.pack(padx=10, pady=10)

def open_tab():
    url = 'https://www.ilpost.it/'
    webbrowser.open_new_tab(url)
    
    
    
app_window = tk.Tk()
s = ttk.Style(app_window)
s.theme_use('clam')
app_window.title('Stefano TechJournal')
app_window.geometry('600x400+500+200')
app_window.attributes('-alpha',0.8)
app_window.iconbitmap('C:/dev/techjournal/static/icon.ico')

message = tk.Label(app_window, text="Click!")

message.pack()

style = ttk.Style()
style.map("C.TButton",
    foreground=[('pressed', 'red'), ('active', 'blue')],
    background=[('pressed', '!disabled', 'black'), ('active', 'white')]
    )


ttk.Button(app_window, text='Calendar', command=example1).pack(padx=10, pady=10)
ttk.Button(app_window, text='DateEntry', command=example2).pack(padx=10, pady=10)
ttk.Button(app_window, text='Open ilPost', command=open_tab).pack(padx=10, pady=10)
ttk.Button(app_window,
              text="Exit",
              style="C.TButton",
              command=app_window.destroy).pack(padx=10, pady=10)
try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
finally:
    app_window.mainloop()
