from tkinter import ttk 
import tkinter as tk
from eosim.config import GuiStyle, MissionConfig
from eosim import config
from eosim.gui.configure import cfmission
import orbitpy
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
import os
import eosim.gui.helpwindow as helpwindow
import pickle
import logging

logger = logging.getLogger(__name__)

class CfConstellation():
    def click_constellation_btn(self):      

        # create and configure child window, parent frame
        constl_win = tk.Toplevel()
        constl_win.rowconfigure(0,weight=1)
        constl_win.columnconfigure(0,weight=1)

        constl_win_frame =ttk.Frame(constl_win)
        constl_win_frame.grid(row=0, column=0, padx=10, pady=10)
        constl_win_frame.rowconfigure(0,weight=1) # constellation type
        constl_win_frame.rowconfigure(1,weight=1) # constellation specs
        constl_win_frame.rowconfigure(2,weight=1) # okcancel
        constl_win_frame.columnconfigure(0,weight=1)

        # define all child frames
        constl_type_frame = ttk.LabelFrame(constl_win_frame, text="Constellation type")
        constl_type_frame.grid(row=0, column=0, sticky='nswe', padx=20, pady=20)
        constl_type_frame.columnconfigure(0,weight=1)
        constl_type_frame.rowconfigure(0,weight=1)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        # grid configure
        constl_specs_container = ttk.LabelFrame(constl_win_frame, text="Specifications", width=250, height=370)
        constl_specs_container.grid_propagate(0)
        constl_specs_container.grid(row=1, column=0, sticky='nswe', padx=20, pady=20)
        constl_specs_container.columnconfigure(0,weight=1)
        constl_specs_container.rowconfigure(0,weight=1)

        # okcancel frame
        okcancel_frame = ttk.Label(constl_win_frame)
        okcancel_frame.grid(row=2, column=0, sticky='nswe', padx=20, pady=20)
        okcancel_frame.columnconfigure(0,weight=1)
        okcancel_frame.rowconfigure(0,weight=1)

        class HomogenousWalkerFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)
                hwd_specs_frame = ttk.Frame(self) 
                hwd_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)

                # define the widgets inside the child frames
                ttk.Label(hwd_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                self.uid_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.uid_entry.insert(0,"G_"+str(random.randint(0,1000))+"_")
                self.uid_entry.bind("<FocusIn>", lambda args: self.uid_entry.delete('0', 'end'))
                self.uid_entry.grid(row=0, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="# Satellites", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                self.nsats_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.nsats_entry.insert(0,6)
                self.nsats_entry.bind("<FocusIn>", lambda args: self.nsats_entry.delete('0', 'end'))
                self.nsats_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="# Orbital planes", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
                self.nplanes_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.nplanes_entry.insert(0,3)
                self.nplanes_entry.bind("<FocusIn>", lambda args: self.nplanes_entry.delete('0', 'end'))
                self.nplanes_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="Relative spacing", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
                self.rspc_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.rspc_entry.insert(0,1)
                self.rspc_entry.bind("<FocusIn>", lambda args: self.rspc_entry.delete('0', 'end'))
                self.rspc_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="Inclination [deg]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
                self.inc_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.inc_entry.insert(0,67)
                self.inc_entry.bind("<FocusIn>", lambda args: self.inc_entry.delete('0', 'end'))
                self.inc_entry.grid(row=4, column=1, sticky='w')
                
                ttk.Label(hwd_specs_frame, text="Altitude [km]", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
                self.alt_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.alt_entry.insert(0,350)
                self.alt_entry.bind("<FocusIn>", lambda args: self.alt_entry.delete('0', 'end'))
                self.alt_entry.grid(row=5, column=1, sticky='w')

                tk.Label(hwd_specs_frame, text="Eccentricity", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
                self.ecc_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.ecc_entry.insert(0,0)
                self.ecc_entry.bind("<FocusIn>", lambda args: self.ecc_entry.delete('0', 'end'))
                self.ecc_entry.grid(row=6, column=1, sticky='w')

                tk.Label(hwd_specs_frame, text="AOP [deg]", wraplength=150).grid(row=7, column=0, padx=10, pady=10, sticky='w')
                self.aop_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.aop_entry.insert(0,250)
                self.aop_entry.bind("<FocusIn>", lambda args: self.aop_entry.delete('0', 'end'))
                self.aop_entry.grid(row=7, column=1, sticky='w')
            
            def get_specs(self):
                return [self.uid_entry.get(), self.nsats_entry.get(), self.nplanes_entry.get(), self.rspc_entry.get(), self.alt_entry.get(), 
                        self.ecc_entry.get(), self.inc_entry.get(), self.aop_entry.get()]               

        class HeterogenousWalkerFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)         
                hetw_specs_frame = ttk.Frame(self) 
                hetw_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)    
                ttk.Label(hetw_specs_frame, text="Under development").pack()    
        
        class TrainConstlFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                trainc_specs_frame = ttk.Frame(self) 
                trainc_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)
                ttk.Label(trainc_specs_frame, text="Under development").pack()          

        frames = {}
        for F in (HomogenousWalkerFrame, HeterogenousWalkerFrame, TrainConstlFrame):
            page_name = F.__name__
            frame = F(parent=constl_specs_container, controller=self)
            frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # define the widgets inside the child frames
        
        # constellation types child frame
        MODES = [
            ("Homogenous Walker Delta", "HomogenousWalkerFrame"),
            ("Heterogenous Walker", "HeterogenousWalkerFrame"),
            ("Train", "TrainConstlFrame")
        ]

        self._constl_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._constl_type.set("HomogenousWalkerFrame") # initialize

        def constl_type_rbtn_click():
            if self._constl_type.get() == "HomogenousWalkerFrame":
                frame = frames["HomogenousWalkerFrame"]
            elif self._constl_type.get() == "HeterogenousWalkerFrame":
                frame = frames["HeterogenousWalkerFrame"]
            elif self._constl_type.get() == "TrainConstlFrame":
                frame = frames["TrainConstlFrame"]

            frame.tkraise()

        for text, mode in MODES:
            constl_type_rbtn = ttk.Radiobutton(constl_type_frame, text=text, command=constl_type_rbtn_click,
                            variable=self._constl_type, value=mode)
            constl_type_rbtn.pack(anchor='w', padx=20, pady=20)

        frame = frames[self._constl_type.get()]
        frame.tkraise()    

        # okcancel frame
        def ok_click():               
            ''' REV_TEST
            if self._constl_type.get() == "HomogenousWalkerFrame":
                specs = frames[self._constl_type.get()].get_specs()
                data = {}
                data['@id'] = specs[0]
                data['numberSatellites'] = specs[1]
                data['numberPlanes'] = specs[2]
                data['relativeSpacing'] = specs[3]
                data['alt'] = specs[4]
                data['ecc'] = specs[5]
                data['inc'] = specs[6]
                data['aop'] = specs[7]                

                sats = PreProcess.walker_orbits(data)                        
                config.miss_specs.add_satellite(sats)
            '''
            
        ok_btn = ttk.Button(okcancel_frame, text="Add", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=constl_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)