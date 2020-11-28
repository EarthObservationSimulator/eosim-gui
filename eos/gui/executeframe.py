from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
from eos import config
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.public_library import Instrument
from instrupy.util import *
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util
import threading
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc('font', family='sans-serif') 
matplotlib.rc('font', serif='Times New Roman') 
matplotlib.rc('text', usetex='false') 
matplotlib.rcParams.update({'font.size': 12})

import logging

logger = logging.getLogger(__name__)



class ExecuteFrame(ttk.Frame):

    BTNWIDTH = 15

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(4,weight=1)
        self.columnconfigure(0,weight=1)        

        # define propagation execution frame 
        pexec_frame = ttk.LabelFrame(self, text="Execute Propagation", labelanchor='n') 
        pexec_frame.grid(row=0, column=0, ipadx=10, sticky='nswe')
        pexec_frame.columnconfigure(0,weight=1)
        pexec_frame.columnconfigure(1,weight=4)       

        # define the widgets inside the frames        
        # exec frame
        pexec_btn = ttk.Button(pexec_frame, text="Propagate", command=lambda:self.click_pexec_btn(prop_progress_bar))
        pexec_btn.grid(row=0, column=0, sticky='w', padx=20)

        prop_progress_bar = ttk.Progressbar(pexec_frame, orient='horizontal', length=300, mode='indeterminate')
        prop_progress_bar.grid(row=0, column=1, padx=20, sticky='w')
        
             
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
            logger.info(".......Preprocessing configuration .......")
            pi = preprocess.PreProcess(miss_specs, user_dir) # generates grid if-needed, calculates propagation 
                                                             # and coverage parameters, enumerates orbits, etc.
            prop_cov_param = pi.generate_prop_cov_param()   
            print(".......Done.......")

            # Run orbit propagation for each of the satellties (orbits) in the constellation
            sat_id = [] # list of propagated satellites (ids)
            sat_eci_state_fp = [] # list of the eci-state files
            sat_kep_state_fp = [] # list of the Keplerian-state files
            for orb_indx in range(0,len(prop_cov_param)):
                pcp = prop_cov_param[orb_indx]
                pcp.cov_calcs_app = util.CoverageCalculationsApproach.SKIP # force skip of coverage calculations
                opc = orbitpropcov.OrbitPropCov(pcp)
                print(".......Running Orbit Propagation for satellite.......", pcp.sat_id)
                opc.run()
                sat_id.append(pcp.sat_id)
                sat_eci_state_fp.append(pcp.sat_state_fl)
                sat_kep_state_fp.append(pcp.sat_state_fl + '_Keplerian')
                print(".......Done.......")

            # save output configuration file (any previous configuration is re-written since propagation is the first step 
            # to any of the future calculations such as coverage or communications, etc)

            config.out_config.update_prop_out(prop_done=True, sat_id=sat_id, sat_eci_state_fp=sat_eci_state_fp, sat_kep_state_fp=sat_kep_state_fp) 
            with open('output.json', 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            prop_progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_pexec_btn).start()

        

      
        

