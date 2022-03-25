# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 04:38:50 2022

@author: c740
"""

import tkinter as tk
from tkinter import ttk

from tkcalendar import Calendar

app_window = tk.Tk()
s = ttk.Style(app_window)
s.theme_use('clam')
app_window.title('Stefano TechJournal')
app_window.geometry('600x400+500+200')
app_window.attributes('-alpha',0.9)
app_window.iconbitmap('C:/dev/techjournal/static/icon.ico')


cal = Calendar(app_window,
               font="Arial 14", selectmode='day',
               cursor="hand1", year=2018, month=2, day=5)
cal.pack(fill="both", expand=True)
style = ttk.Style()
style.map("C.TButton",
    foreground=[('pressed', 'red'), ('active', 'blue')],
    background=[('pressed', '!disabled', 'black'), ('active', 'white')]
    )

ttk.Button(app_window,
              text="Exit",
              style="C.TButton",
              command=app_window.destroy).pack(padx=10, pady=10)
try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
finally:
    app_window.mainloop()



