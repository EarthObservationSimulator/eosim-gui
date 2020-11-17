from tkinter import ttk 
import tkinter as tk
from orbitpy.preprocess import OrbitParameters
from instrupy.public_library import Instrument
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
    def __init__(self, epoch=None, duration=None, satellite=None, sensor=None, sat_to_sensor_map=None, prop=None, cov_grid=None):
        self.epoch = epoch if epoch is not None else None
        self.duration = duration if duration is not None else None
        self.satellite = list(satellite) if satellite is not None else list() # satellite is the same as orbit
        self.sensor = list(sensor) if sensor is not None else list()
        self.sat_to_sensor_map = list(sat_to_sensor_map) if sat_to_sensor_map is not None else list()
        self.prop = prop if prop is not None else None
        self.cov_grid =  cov_grid if cov_grid is not None else None
    
    def update_epoch(self, epoch):
        self.epoch = epoch

    def update_duration(self, duration):
        self.duration = duration

    def add_satellite(self, sat):
        if isinstance(sat,list):
            self.satellite.extend(sat) 
        else:
            self.satellite.append(sat) 
    
    def add_propagator(self, prop):
        self.prop = prop

    def add_sensor(self, sensor, sensor_to_sat):
        """ Add sensor to the given list of satellites.

            :param sensor: Sensor 
            :paramtype sensor: :class:`instrupy.`

            :param sensor_to_sat: Unique IDs of satellites to which the sensor is to be attached. 
            :paramtype sensor_to_sat: list

        """
        if isinstance(sensor,list):
            self.sensor.extend(sensor) 
        else:
            self.sensor.append(sensor) 
        
        sensor_id = sensor.get_id() # get the unique instrument id
        self.sat_to_sensor_map.append((sensor_id, sensor_to_sat)) # tuple of sensor-id and list of satetllites to which the sensor is attached

    def get_satellite_kepl_specs(self):
        # parse out the satellite ids (orbit ids)
        orb_specs = []
        if(len(self.satellite) == 0):
            return False
        for _sat in self.satellite:
            orb_specs.append([_sat._id, _sat.sma, _sat.ecc, _sat.inc, _sat.raan, _sat.aop, _sat.ta])        
        return orb_specs 

    def add_coverage_grid(self, data):
        self.cov_grid = data

    def to_dict(self):
        """ Format the MissionConfig object into a dictionary (so it may later be exported as JSON file)."""
        sat_dict = []
        for sat in self.satellite:
            sat_sensor = [] # list of sensors in the satellite
            for k in range(0, len(self.sensor)): 
                if sat._id in self.sat_to_sensor_map[k][1]:
                    sat_sensor.append(self.sensor[k])
            t = [x.to_dict() for x in sat_sensor]
            flat_list = [item for sublist in t for item in sublist]
            sat_dict.append({"orbit":sat.to_dict(), "instrument": flat_list}) 

        miss_specs_dict = dict({"epoch":self.epoch,
                                "duration": self.duration,
                                "satellite": sat_dict,
                                "propagator": self.prop,
                                "grid": self.cov_grid
                               }) 
        return miss_specs_dict
