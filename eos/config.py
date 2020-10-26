from tkinter import ttk 
import tkinter as tk
from orbitpy.preprocess import OrbitParameters
import json

class GuiStyle():
    main_win_width = 900
    main_win_height = int(900*9/21)
    main_window_geom = "900x386" # 900 width, 21:9 aspect ratio
    child_window_geom = "500x500"
    
    def __init__(self):     
        gui_style = ttk.Style()
        gui_style.configure('My.TButton', foreground='#334353')
        gui_style.configure('helparea.TFrame', background='blue')
        gui_style.configure('messagearea.TFrame', background='white',  relief='sunken')
        gui_style.configure('statusbar.TFrame',background='yellow',  relief='sunken')  

class MissionConfig:
    """ Class which holds all the mission configuration parameters """
    def __init__(self, epoch=None, duration=None, satellite=None):
        self.epoch = epoch if epoch is not None else None
        self.duration = duration if duration is not None else None
        self.satellite = list(satellite) if satellite is not None else list()
    
    def update_epoch(self, epoch):
        self.epoch = epoch

    def update_duration(self, duration):
        self.duration = duration

    def add_satellite(self, sat):
        if isinstance(sat,list):
            self.satellite.extend(sat) 
        else:
            self.satellite.append(sat) 
    
    def to_dict(self):
        
        sat_dict = []
        for sat in self.satellite:
            sat_dict.append(sat.to_dict())

        miss_specs_dict = dict({"epoch":self.epoch,
                                "duration": self.duration,
                                "satellite": sat_dict}) 
        return miss_specs_dict
