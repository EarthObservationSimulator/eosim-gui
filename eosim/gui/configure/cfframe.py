from tkinter import ttk 
import tkinter as tk
from eosim import config

from eosim.gui.configure.cfmission import CfMission
from eosim.gui.configure.cfsatellite import CfSatellite
from eosim.gui.configure.cfconstellation import CfConstellation
from eosim.gui.configure.cfsensor import CfSensor
from eosim.gui.configure.cfpropagate import CfPropagate
from eosim.gui.configure.cfintersatellitecomm import CfInterSatelliteComm
from eosim.gui.configure.cfcoverage import CfCoverage
from eosim.gui.configure.cfgroundstation import CfGroundStation

import json
import logging

logger = logging.getLogger(__name__)
    
class ConfigureFrame(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=4)
        self.rowconfigure(1,weight=4)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

        self.cfmission = CfMission()
        self.cfsatellite = CfSatellite()
        self.cfconstellation = CfConstellation()
        self.cfsensor = CfSensor()
        self.cfgroundstation = CfGroundStation()
        self.cfpropagate = CfPropagate()
        self.cfintersatellitecomm = CfInterSatelliteComm()
        self.cfcoverage = CfCoverage()

        # "Define Mission Frame" 
        miss_frame = ttk.LabelFrame(self, text="Define Mission", labelanchor='n') 
        miss_frame.grid(row=0, column=0, ipadx=20, ipady=20)
        miss_btn = ttk.Button(miss_frame, text="Mission", command=self.cfmission.click_mission_btn)
        miss_btn.pack(expand=True)

        # "Add Resource" frame
        resource_frame = ttk.LabelFrame(self, text="Add Resource", labelanchor='n') 
        resource_frame.grid(row=0, column=1, ipadx=20, ipady=20)
        resource_frame.rowconfigure(0,weight=1)
        resource_frame.rowconfigure(1,weight=1)
        resource_frame.columnconfigure(0,weight=1)
        resource_frame.columnconfigure(1,weight=1)
        sat_btn = ttk.Button(resource_frame, text="Satellite", command=self.cfsatellite.click_satellite_btn, width=15)
        sat_btn.grid(row=0, column=0)
        con_btn = ttk.Button(resource_frame, text="Constellation", command=self.cfconstellation.click_constellation_btn, width=15)
        con_btn.grid(row=0, column=1)
        sen_btn = ttk.Button(resource_frame, text="Sensor", command=self.cfsensor.click_sensor_btn, width=15)
        sen_btn.grid(row=1, column=0)
        gndstn_btn = ttk.Button(resource_frame, text="Ground Station", command=self.cfgroundstation.click_gs_btn, width=15)
        gndstn_btn.grid(row=1, column=1)

        #
        visual_frame = ttk.LabelFrame(self, text="Visualize", labelanchor='n') 
        visual_frame.grid(row=1, column=0, ipadx=20, ipady=20)
        visual_frame.rowconfigure(0,weight=1)
        visual_frame.columnconfigure(0,weight=1)
        vis_arch_btn = ttk.Button(visual_frame, text="Visualize Arch", command=self.click_visualize_btn, width=15)
        vis_arch_btn.grid(row=0, column=0)

        # "Settings" frame
        settings_frame = ttk.LabelFrame(self, text="Settings", labelanchor='n') 
        settings_frame.grid(row=1, column=1, ipadx=20, ipady=20)
        settings_frame.rowconfigure(0,weight=1)
        settings_frame.rowconfigure(1,weight=1)
        settings_frame.columnconfigure(0,weight=1)
        settings_frame.columnconfigure(1,weight=1)
        prp_set_btn = ttk.Button(settings_frame, text="Propagate", command=self.cfpropagate.click_propagate_settings_btn, width=15)
        prp_set_btn.grid(row=0, column=0)
        com_set_btn = ttk.Button(settings_frame, text="Inter-Sat Comm", command=self.cfintersatellitecomm.click_intersatcomm_settings_btn, width=15)
        com_set_btn.grid(row=0, column=1)
        cov_set_btn = ttk.Button(settings_frame, text="Coverage", command=self.cfcoverage.click_coverage_settings_btn, width=15)
        cov_set_btn.grid(row=1, column=0)

        #
        clr_sv_run_frame = ttk.Frame(self) 
        clr_sv_run_frame.grid(row=2, column=0, columnspan=2, ipadx=10, sticky = 'nsew')
        clr_sv_run_frame.columnconfigure(0,weight=1)
        clr_sv_run_frame.columnconfigure(1,weight=1)
        clr_sv_run_frame.columnconfigure(2,weight=1)
        clear_conf_btn = ttk.Button(clr_sv_run_frame, text="Clear Config", command=self.click_clear_config, width=25)
        clear_conf_btn.grid(row=0, column=0, ipadx=20, sticky='s')
        save_conf_btn = ttk.Button(clr_sv_run_frame, text="Save Config", command=self.click_save_config, width=25)
        save_conf_btn.grid(row=0, column=2, ipadx=20, sticky='s')


    def click_save_config(self):
        """ Save the mission configuration as a JSON file."""
        
        wdir = config.mission.settings.outDir
        if wdir is None:
            logger.info("Please select the workspace directory in the menubar by going to Sim->New.")
            return
        
        with open(wdir+'MissionSpecs.json', 'w', encoding='utf-8') as f:
            json.dump(config.mission.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info("Mission configuration Saved.")

        ''' REV_TEST
        logger.info(".......Preprocessing configuration .......")
        user_dir = config.out_config.get_user_dir()
        pi = preprocess.PreProcess(config.miss_specs.to_dict(), user_dir) # generates grid if-needed, calculates propagation 
                                                         # and coverage parameters, enumerates orbits, etc.
        prop_cov_param = pi.generate_prop_cov_param() 

        # store data for later use during execution, visualization
        pickle.dump(prop_cov_param, open(user_dir+"prop_cov_param.p", "wb"))

        pickle.dump(pi, open(user_dir+"preprocess_data.p", "wb"))

        with open(user_dir+"comm_param.p", "wb") as f:
            pickle.dump(pi.comm_dir, f)
            pickle.dump(pi.gnd_stn_fl, f)
            pickle.dump(pi.ground_stn_info, f)
        with open(user_dir+'MissionSpecs.json', 'w', encoding='utf-8') as f:
            json.dump(config.miss_specs.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info("Configuration Saved.")
        '''
    
    def click_clear_config(self):
        """ Clear the mission configuration (both in the local variable and in the MissionSpecs file written in the workspace directory).
            Only the working directory information is retained. 
        """
        wdir = config.mission.settings.outDir
        config.mission.clear()
        config.mission.settings.outDir = wdir # retain the working directory
        with open(wdir+'MissionSpecs.json', 'w', encoding='utf-8') as f:
            json.dump(config.mission.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info("Configuration cleared.")
    
    def click_visualize_btn(self):
        """ This function simply diplays the mission configuration in json format in the pop-up window."""
        vis_win = tk.Toplevel()
        ttk.Label(vis_win, text=(config.mission.to_dict()), wraplength=150).pack(padx=5, pady=5)

    