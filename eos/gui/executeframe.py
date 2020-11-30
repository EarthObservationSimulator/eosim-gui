from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig, OutputConfig
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
import pickle
import copy
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
        self.columnconfigure(0,weight=1)      
        self.columnconfigure(1,weight=1)    

        # define propagation execution frame 
        pexec_frame = ttk.LabelFrame(self, text="Execute Orbit Propagation", labelanchor='n') 
        pexec_frame.grid(row=0, column=0, ipadx=10, sticky='nswe')
        pexec_frame.columnconfigure(0,weight=1)
        pexec_frame.rowconfigure(0,weight=1)
        pexec_frame.rowconfigure(1,weight=1)

        covexec_frame = ttk.LabelFrame(self, text="Execute Coverage Calculations", labelanchor='n') 
        covexec_frame.grid(row=0, column=1, ipadx=10, sticky='nswe')
        covexec_frame.columnconfigure(0,weight=1)
        covexec_frame.rowconfigure(0,weight=1)
        covexec_frame.rowconfigure(1,weight=1) 

        gndconexec_frame = ttk.LabelFrame(self, text="Execute Ground Station Contact Finder", labelanchor='n') 
        gndconexec_frame.grid(row=1, column=0, ipadx=10, sticky='nswe')
        gndconexec_frame.columnconfigure(0,weight=1)
        gndconexec_frame.rowconfigure(0,weight=1)
        gndconexec_frame.rowconfigure(1,weight=1) 

        sat2satconexec_frame = ttk.LabelFrame(self, text="Execute Satellite-to-Satellite Contact Finder", labelanchor='n') 
        sat2satconexec_frame.grid(row=1, column=1, ipadx=10, sticky='nswe')
        sat2satconexec_frame.columnconfigure(0,weight=1)
        sat2satconexec_frame.rowconfigure(0,weight=1)
        sat2satconexec_frame.rowconfigure(1,weight=1)       

        # define the widgets inside the frames        
        pexec_btn = ttk.Button(pexec_frame, text="Orbit Propagator", width=30, command=lambda:self.click_pexec_btn(prop_progress_bar), style='Execute.TButton')
        pexec_btn.grid(row=0, column=0, padx=20, ipady=5, pady=5, sticky='s')
        prop_progress_bar = ttk.Progressbar(pexec_frame, orient='horizontal', length=300, mode='indeterminate')
        prop_progress_bar.grid(row=1, column=0, padx=20, sticky='n')
        
        covexec_btn = ttk.Button(covexec_frame, text="Coverage Calculator", width=30, command=lambda:self.click_covexec_btn(covexec_progress_bar))
        covexec_btn.grid(row=0, column=0, padx=20, ipady=5, pady=5, sticky='s')
        covexec_progress_bar = ttk.Progressbar(covexec_frame, orient='horizontal', length=300, mode='indeterminate')
        covexec_progress_bar.grid(row=1, column=0, padx=20, sticky='n')

        gndconexec_btn = ttk.Button(gndconexec_frame, text="Ground-Station Contact Finder", width=30, command=lambda:self.click_pexec_btn(prop_progress_bar))
        gndconexec_btn.grid(row=0, column=0, padx=20, ipady=5, pady=5, sticky='s')
        gndconexec_progress_bar = ttk.Progressbar(gndconexec_frame, orient='horizontal', length=300, mode='indeterminate')
        gndconexec_progress_bar.grid(row=1, column=0, padx=20, sticky='n')

        sat2satconexec_btn = ttk.Button(sat2satconexec_frame, text="Sat-to-Sat Contact Finder", width=30, command=lambda:self.click_pexec_btn(prop_progress_bar))
        sat2satconexec_btn.grid(row=0, column=0, padx=20, ipady=5, pady=5, sticky='s')
        sat2satconexec_progress_bar = ttk.Progressbar(sat2satconexec_frame, orient='horizontal', length=300, mode='indeterminate')
        sat2satconexec_progress_bar.grid(row=1, column=0, padx=20, sticky='n')
             
    def click_pexec_btn(self, progress_bar):

        def real_click_pexec_btn():
            # Execute propagation
            user_dir = os.getcwd() + '/'
            usf = user_dir + 'MissionSpecs.json'
            try:
                with open(usf, 'r') as mission_specs_file:
                        miss_specs = util.FileUtilityFunctions.from_json(mission_specs_file)      
            except:
                raise Exception("Configuration not found.")

            progress_bar.start(10)
            # read in the preprocessed propagation and coverage parameters
            prop_cov_param = pickle.load(open( "prop_cov_param.p", "rb"))

            # Run orbit propagation for each of the satellties (orbits) in the constellation
            sat_id = [] # list of propagated satellites (ids)
            sat_eci_state_fp = [] # list of the eci-state files
            sat_kep_state_fp = [] # list of the Keplerian-state files
            for orb_indx in range(0,len(prop_cov_param)):
                pcp = copy.deepcopy(prop_cov_param[orb_indx])
                pcp.cov_calcs_app = util.CoverageCalculationsApproach.SKIP # force skip of coverage calculations
                opc = orbitpropcov.OrbitPropCov(pcp)
                logger.info(".......Running Orbit Propagation for satellite " + str(pcp.sat_id))
                opc.run()
                sat_id.append(pcp.sat_id)
                sat_eci_state_fp.append(pcp.sat_state_fl)
                sat_kep_state_fp.append(pcp.sat_state_fl + '_Keplerian')
                logger.info(".......Done.......")

            # save output configuration file (any previous configuration is re-written since propagation is the first step 
            # to any of the future calculations such as coverage or communications, etc)
            pickle.dump( prop_cov_param, open( "prop_cov_param.p", "wb" ) )
            config.out_config.update_prop_out(sat_id=sat_id, sat_eci_state_fp=sat_eci_state_fp, sat_kep_state_fp=sat_kep_state_fp) 
            with open('output.json', 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_pexec_btn).start()

    def click_covexec_btn(self, progress_bar):

        def real_click_covexec_btn():
            # Execute coverage calculations
            user_dir = os.getcwd() + '/'
            usf = user_dir + 'MissionSpecs.json'
            try:
                with open(usf, 'r') as mission_specs_file:
                        miss_specs = util.FileUtilityFunctions.from_json(mission_specs_file)      
            except:
                raise Exception("Mission Configuration not found.")
            
            progress_bar.start(10)
            # read in the preprocessed propagation and coverage parameters
            prop_cov_param = pickle.load( open( "prop_cov_param.p", "rb" ) )   

            # Run coverage for each of the satellties (orbits) in the constellation
            sat_id = [] # list of satellites (ids) for which coverage is calculated
            sat_acc_fl = [] # list of the access files

            for orb_indx in range(0,len(prop_cov_param)):
                pcp = copy.deepcopy(prop_cov_param[orb_indx])
                pcp.do_prop = False # force skip of propagation calculations
                print(pcp.do_cov)
                opc = orbitpropcov.OrbitPropCov(pcp)
                print(".......Running Coverage calculations for satellite.......", pcp.sat_id)
                opc.run()
                sat_id.append(pcp.sat_id)
                sat_acc_fl.append(pcp.sat_acc_fl)
                print(".......Done.......")

            # update output configuration file            
            ocf = user_dir + 'Output.json'
            try:
                with open(ocf, 'r') as output_config_file:
                        _out_config = util.FileUtilityFunctions.from_json(output_config_file)  
                config.out_config = OutputConfig.from_dict(_out_config)    
            except:
                raise Exception("Output Configuration not found.")
            
            config.out_config.update_cov_out(sat_id=sat_id, sat_acc_fl=sat_acc_fl)
            with open('output.json', 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_covexec_btn).start()

      
        

