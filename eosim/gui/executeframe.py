from tkinter import ttk 
import tkinter as tk
from eosim.config import GuiStyle, MissionConfig, OutputConfig
from eosim import config
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.util import *
import os
import shutil
import sys
import csv
import glob
#from orbitpy import orbitpropcov, communications, obsdatametrics, util REV_TEST
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
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)      
        self.columnconfigure(1,weight=1)    
        self.columnconfigure(2,weight=1) 

        # define propagation execution frame 
        pexec_frame = ttk.Frame(self) 
        pexec_frame.grid(row=0, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        pexec_frame.columnconfigure(0,weight=1)
        pexec_frame.rowconfigure(0,weight=1)

        covexec_frame = ttk.Frame(self) 
        covexec_frame.grid(row=0, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        covexec_frame.columnconfigure(0,weight=1)
        covexec_frame.rowconfigure(0,weight=1)

        gndconexec_frame = ttk.Frame(self) 
        gndconexec_frame.grid(row=0, column=2, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        gndconexec_frame.columnconfigure(0,weight=1)
        gndconexec_frame.rowconfigure(0,weight=1)

        sat2satconexec_frame = ttk.Frame(self) 
        sat2satconexec_frame.grid(row=1, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        sat2satconexec_frame.columnconfigure(0,weight=1)
        sat2satconexec_frame.rowconfigure(0,weight=1)

        obsmetcalcsexec_frame = ttk.Frame(self) 
        obsmetcalcsexec_frame.grid(row=1, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        obsmetcalcsexec_frame.columnconfigure(0,weight=1)
        obsmetcalcsexec_frame.rowconfigure(0,weight=1)

        progressbar_frame = ttk.Frame(self) 
        progressbar_frame.grid(row=2, column=0, columnspan=3, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        progressbar_frame.columnconfigure(0,weight=1)
        progressbar_frame.rowconfigure(0,weight=1)

        # define the widgets inside the frames 
        progress_bar = ttk.Progressbar(progressbar_frame, orient='horizontal', length=300, mode='indeterminate')
        progress_bar.grid(row=0, column=0,  padx=20, sticky='n')

        pexec_btn = tk.Button(pexec_frame, text="Orbit Propagator", width=40, wraplength=100, command=lambda:self.click_pexec_btn(progress_bar))
        pexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')
        
        
        covexec_btn = tk.Button(covexec_frame, text="Coverage Calculator", width=40, wraplength=100, command=lambda:self.click_covexec_btn(progress_bar))
        covexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


        gndconexec_btn = tk.Button(gndconexec_frame, text="Ground-Station Contact Finder", width=40, wraplength=100, command=lambda:self.click_gndconexec_btn(progress_bar))
        gndconexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


        sat2satconexec_btn = tk.Button(sat2satconexec_frame, text="Sat-to-Sat Contact Finder", width=40, wraplength=100, command=lambda:self.click_sat2satconexec_btn(progress_bar))
        sat2satconexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


        obsmetcalcexec_btn = tk.Button(obsmetcalcsexec_frame, text="Obs-metrics Calculator", width=40, wraplength=100, command=lambda:self.click_obsmetcalcexec_btn(progress_bar))
        obsmetcalcexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')

    def click_gndconexec_btn(self, progress_bar):
        
        def real_click_gndconexec_btn():
            # Execute ground-station contact finder
            user_dir = config.out_config.get_user_dir()
           
            # Gather the required inputs
            with open(user_dir+ 'comm_param.p', 'rb') as f:
                comm_dir = pickle.load(f)
                gnd_stn_fl = pickle.load(f)
                ground_stn_info = pickle.load(f)

            prop_cov_param = pickle.load( open(user_dir+ "prop_cov_param.p", "rb" ) )              
                   
            sat_ids = [] # list of satellites (ids) 
            sat_dirs = [] # list of directories where the ground station output is written
            sat_state_fls = [] # list of the state files
            for _indx in range(0,len(prop_cov_param)):
                pcp = copy.deepcopy(prop_cov_param[_indx]) 
                sat_ids.append(pcp.sat_id)               
                sat_state_fls.append(pcp.sat_state_fl)
                _dir = "/".join([str(x) for x in pcp.sat_state_fl.split("/")[0:-1]])+'/'
                sat_dirs.append(_dir)
            
            ocf = user_dir + 'output.json'
            try:
                with open(ocf, 'r') as output_config_file:
                        _out_config = util.FileUtilityFunctions.from_json(output_config_file)  
                config.out_config = OutputConfig.from_dict(_out_config)    
            except:
                raise Exception("Output Configuration not found.")

            progress_bar.start(10)            

            if gnd_stn_fl is None and ground_stn_info is None:
                logger.info("No ground-stations are specified")
            else:
                logger.info(".......Computing satellite-to-ground-station contact periods.......")      
                # compute for 1 satellite at a time to keep track of which satellites (ids) the resulting files belong to
                for k in range(0,len(sat_ids)):
                    gnd_stn_comm = communications.GroundStationComm(sat_dirs=sat_dirs[k], sat_state_fls=sat_state_fls[k], gnd_stn_fl=gnd_stn_fl, ground_stn_info=ground_stn_info)
                    [gnd_stn_i, gndstncomm_concise_fls, gndstncomm_detailed_fls] = gnd_stn_comm.compute_all_contacts() 
                     # update output configuration file 
                    config.out_config.update_ground_stns_comm(sat_id=sat_ids[k], gnd_stn_id = gnd_stn_i, gndstncomm_concise_fls=gndstncomm_concise_fls, gndstncomm_detailed_fls=gndstncomm_detailed_fls)
                
                logger.info(".......DONE.......") 

            with open(ocf, 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()
            

        # execute propagation
        threading.Thread(target=real_click_gndconexec_btn).start()

    def click_sat2satconexec_btn(self, progress_bar):

        def real_click_sat2satconexec_btn():
            # Execute sat-to-sat contact finder
            user_dir = config.out_config.get_user_dir()
           
            # Gather the required inputs
            with open(user_dir+ 'preprocess_data.p', 'rb') as f:
                pi = pickle.load(f)

            with open(user_dir+ 'comm_param.p', 'rb') as f:
                comm_dir = pickle.load(f)
                gnd_stn_fl = pickle.load(f)
                ground_stn_info = pickle.load(f)

            prop_cov_param = pickle.load( open(user_dir+ "prop_cov_param.p", "rb" ) )              
                   
            sat_ids = [] # list of satellites (ids) 
            sat_dirs = [] # list of directories where the ground station output is written
            sat_state_fls = [] # list of the state files
            for _indx in range(0,len(prop_cov_param)):
                pcp = copy.deepcopy(prop_cov_param[_indx]) 
                sat_ids.append(pcp.sat_id)               
                sat_state_fls.append(pcp.sat_state_fl)
                _dir = "/".join([str(x) for x in pcp.sat_state_fl.split("/")[0:-1]])+'/'
                sat_dirs.append(_dir)
            
            ocf = user_dir + 'output.json'
            try:
                with open(ocf, 'r') as output_config_file:
                        _out_config = util.FileUtilityFunctions.from_json(output_config_file)  
                config.out_config = OutputConfig.from_dict(_out_config)    
            except:
                raise Exception("Output Configuration not found.")

            logger.info(".......Computing satellite-to-satellite contact periods.......") 
            progress_bar.start(10)            

            opaque_atmos_height_km = pi.opaque_atmos_height_km
            logger.info("Considering opaque atmospheric height to be : " + str(opaque_atmos_height_km) + "km") 
            inter_sat_comm = communications.InterSatelliteComm(sat_ids, sat_state_fls, comm_dir, opaque_atmos_height_km)
            [sat1_ids, sat2_ids, intersatcomm_concise_fls, intersatcomm_detailed_fls] = inter_sat_comm.compute_all_contacts()
            config.out_config.update_intersatcomm(sat1_ids=sat1_ids, sat2_ids=sat2_ids, intersatcomm_concise_fls=intersatcomm_concise_fls, intersatcomm_detailed_fls=intersatcomm_detailed_fls)
            logger.info(".......DONE.......") 

            with open(ocf, 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()
        # execute propagation
        threading.Thread(target=real_click_sat2satconexec_btn).start()

    def click_obsmetcalcexec_btn(self, progress_bar):

        def real_click_obsmetcalcexec_btn():
            # Execute observation metrics calculations
            user_dir = config.out_config.get_user_dir()
            usf = user_dir + 'MissionSpecs.json'
            try:
                with open(usf, 'r') as mission_specs_file:
                        miss_specs = util.FileUtilityFunctions.from_json(mission_specs_file)      
            except:
                raise Exception("Mission Configuration not found.")
            
            progress_bar.start(10)

            # read in the preprocessed data
            with open(user_dir+ 'preprocess_data.p', 'rb') as f:
                pi = pickle.load(f)

            if "instrument" in miss_specs:
                instru_specs = miss_specs['instrument']
            elif "satellite" in miss_specs:
                instru_specs = []
                for sat in miss_specs["satellite"]:
                    if("instrument" in sat):
                        instru_specs.extend(sat["instrument"])

            if(instru_specs is not None):
                logger.info("Started computation of observation metrics")
                obs = obsdatametrics.ObsDataMetrics(pi.sats)
                [sat_id, ssid, obsMetrics_fl] = obs.compute_all_obs_metrics()   
                logger.info("Computed observation metrics")   
            else:
                logger.info("No instruments present, skinng computation of observation metrics")  
                pass

            # update output configuration file            
            ocf = user_dir + 'output.json'
            try:
                with open(ocf, 'r') as output_config_file:
                        _out_config = util.FileUtilityFunctions.from_json(output_config_file)  
                config.out_config = OutputConfig.from_dict(_out_config)    
            except:
                raise Exception("Output Configuration not found.")
            
            config.out_config.update_calc_obsmetrics(sat_id=sat_id, ssid=ssid, obsMetrics_fl=obsMetrics_fl)
            with open(ocf, 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_obsmetcalcexec_btn).start() 
             
    def click_pexec_btn(self, progress_bar):

        def real_click_pexec_btn():
            # Execute propagation
            user_dir = config.out_config.get_user_dir()
            usf = user_dir + 'MissionSpecs.json'
            try:
                with open(usf, 'r') as mission_specs_file:
                        miss_specs = util.FileUtilityFunctions.from_json(mission_specs_file)      
            except:
                raise Exception("Configuration not found.")

            progress_bar.start(10)
            # read in the preprocessed propagation and coverage parameters
            prop_cov_param = pickle.load(open(user_dir+"prop_cov_param.p", "rb"))

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
            config.out_config.update_prop_out(sat_id=sat_id, sat_eci_state_fp=sat_eci_state_fp, sat_kep_state_fp=sat_kep_state_fp) 
            with open(user_dir + 'output.json', 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_pexec_btn).start()

    def click_covexec_btn(self, progress_bar):

        def real_click_covexec_btn():
            # Execute coverage calculations
            user_dir = config.out_config.get_user_dir()
            usf = user_dir + 'MissionSpecs.json'
            try:
                with open(usf, 'r') as mission_specs_file:
                        miss_specs = util.FileUtilityFunctions.from_json(mission_specs_file)      
            except:
                raise Exception("Mission Configuration not found.")
            
            progress_bar.start(10)
            # read in the preprocessed propagation and coverage parameters
            prop_cov_param = pickle.load( open(user_dir+ "prop_cov_param.p", "rb" ) )   

            # Run coverage for each of the satellties (orbits) in the constellation
            sat_id = [] # list of satellites (ids) for which coverage is calculated
            sat_acc_fl = [] # list of the access files

            for orb_indx in range(0,len(prop_cov_param)):
                pcp = copy.deepcopy(prop_cov_param[orb_indx])
                pcp.do_prop = False # force skip of propagation calculations
                opc = orbitpropcov.OrbitPropCov(pcp)
                logger.info(".......Running Coverage calculations for satellite " + str(pcp.sat_id) + "....")
                opc.run()
                sat_id.append(pcp.sat_id)
                sat_acc_fl.append(pcp.sat_acc_fl)
                logger.info(".......Done.......")

            # update output configuration file            
            ocf = user_dir + 'output.json'
            try:
                with open(ocf, 'r') as output_config_file:
                        _out_config = util.FileUtilityFunctions.from_json(output_config_file)  
                config.out_config = OutputConfig.from_dict(_out_config)    
            except:
                raise Exception("Output Configuration not found.")
            
            config.out_config.update_cov_out(sat_id=sat_id, sat_acc_fl=sat_acc_fl)
            with open(ocf, 'w', encoding='utf-8') as f:
                json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_covexec_btn).start()

      
        

