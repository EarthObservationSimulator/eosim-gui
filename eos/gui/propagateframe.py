from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.public_library import Instrument
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util
import threading
import time
class PropagateFrame(ttk.Frame):

    BTNWIDTH = 15

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=10)
        self.columnconfigure(0,weight=1)
        

        # define propagation execution frame 
        pexec_frame = ttk.LabelFrame(self, text="Execute Propagation", labelanchor='n') 
        pexec_frame.grid(row=0, column=0, ipadx=10,  sticky='nswe')
        pexec_frame.columnconfigure(0,weight=1)
        pexec_frame.columnconfigure(1,weight=4)

        pexec_btn = ttk.Button(pexec_frame, text="Propagate", command=lambda:self.click_pexec_btn(prop_progress_bar))
        pexec_btn.grid(row=0, column=0, sticky='w', ipadx=10, ipady=10, padx=20)

        prop_progress_bar = ttk.Progressbar(pexec_frame, orient='horizontal', length=300, mode='indeterminate')
        prop_progress_bar.grid(row=0, column=1, padx=20, sticky='w')

        # define the visualization frame
        pvis_frame = ttk.Frame(self) 
        pvis_frame.grid(row=1, column=0, ipadx=10, ipady=10, sticky='nswe')
        pvis_frame.rowconfigure(0,weight=1)
        pvis_frame.columnconfigure(0,weight=1)
        pvis_frame.columnconfigure(1,weight=1)
        pvis_frame.columnconfigure(2,weight=1)

        # define the visualization child frames
        pvis_2d_frame = ttk.LabelFrame(pvis_frame, text="2D visualization", labelanchor='n')
        pvis_2d_frame.grid(row=0, column=0, ipadx=10, ipady=10, sticky='nswe')

        pvis_2dmap_frame = ttk.LabelFrame(pvis_frame, text="2D Map visualization", labelanchor='n')
        pvis_2dmap_frame.grid(row=0, column=1, ipadx=10, ipady=10, sticky='nswe')
        
        pvis_3dglobe_frame = ttk.LabelFrame(pvis_frame, text="3D Globe visualization", labelanchor='n')
        pvis_3dglobe_frame.grid(row=0, column=2, ipadx=10, ipady=10, sticky='nswe')

    def click_pexec_btn(self, prop_progress_bar):

        def real_click_pexec_btn():
            # Execute propagation
            user_dir = os.getcwd() + '/'
            usf = user_dir + 'MissionSpecs.json'
            try:
                with open(usf, 'r') as mission_specs_file:
                        miss_specs = util.FileUtilityFunctions.from_json(mission_specs_file)      
            except:
                raise Exception("Configuration not found.")

            prop_progress_bar.start(10)
            # Preprocess
            print(".......Preprocessing configuration .......")
            pi = preprocess.PreProcess(miss_specs, user_dir) # generates grid if-needed, calculates propagation 
                                                            # and coverage parameters, enumerates orbits, etc.
            prop_cov_param = pi.generate_prop_cov_param()   
            print(".......Done.......")

            # Run orbit propagation and coverage for each of the satellties (orbits) in the constellation
            for orb_indx in range(0,len(prop_cov_param)):
                pcp = prop_cov_param[orb_indx]
                opc = orbitpropcov.OrbitPropCov(pcp)
                print(".......Running Orbit Propagation and Coverage for satellite.......", pcp.sat_id)
                opc.run()        
                print(".......Done.......")

            prop_progress_bar.stop()

        threading.Thread(target=real_click_pexec_btn).start()
      
        

