from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig, OutputConfig
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
import logging

logger = logging.getLogger(__name__)

out_config = OutputConfig()  

class TwoDimVisPlotAttibutes():
    def __init__(self, x_satellite=None, x_var=None, y_satellite=None, y_var=None):
        self.x_satellite = x_satellite if x_satellite is not None else None
        self.x_var = x_var if x_var is not None else None
        self.y_satellite = y_satellite if y_satellite is not None else list()
        self.y_var = y_var if y_var is not None else list()

    def update_x_variables(self, x_satellite, x_var):
        self.x_satellite = x_satellite
        self.x_var = x_var
    
    def update_y_variables(self, y_satellite, y_var):
        self.y_satellite.append(y_satellite)
        self.y_var.append(y_var)
    
    def get_y_variables(self):
        return [self.y_satellite, self.y_var]

two_dim_vis_plt_attr = TwoDimVisPlotAttibutes()

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
        pexec_frame.grid(row=0, column=0, ipadx=10, sticky='nswe')
        pexec_frame.columnconfigure(0,weight=1)
        pexec_frame.columnconfigure(1,weight=4)

        # define the visualization frame
        pvis_frame = ttk.Frame(self) 
        pvis_frame.grid(row=1, column=0, sticky='nswe')
        pvis_frame.rowconfigure(0,weight=1)
        pvis_frame.columnconfigure(0,weight=1)
        pvis_frame.columnconfigure(1,weight=1)
        pvis_frame.columnconfigure(2,weight=1)

        # define the visualization child frames
        # 2d plots frame
        pvis_2d_frame = ttk.LabelFrame(pvis_frame, text="2D Plot visualization", labelanchor='n')
        pvis_2d_frame.grid(row=0, column=0, sticky='nswe')        
        pvis_2d_frame.rowconfigure(0,weight=4)
        pvis_2d_frame.rowconfigure(1,weight=8)
        pvis_2d_frame.rowconfigure(2,weight=1)
        pvis_2d_frame.columnconfigure(0,weight=1)
        pvis_2d_frame.columnconfigure(1,weight=1)       

        pvis_2d_time_frame = ttk.Frame(pvis_2d_frame)
        pvis_2d_time_frame.grid(row=0, column=0, sticky='nswe', padx=(10,2), rowspan=2)
        pvis_2d_time_frame.rowconfigure(0,weight=1)
        pvis_2d_time_frame.rowconfigure(1,weight=1)
        pvis_2d_time_frame.rowconfigure(2,weight=1)
        pvis_2d_time_frame.rowconfigure(3,weight=1)
        pvis_2d_time_frame.rowconfigure(4,weight=1)

        pvis_2d_xaxis_frame = ttk.Frame(pvis_2d_frame)
        pvis_2d_xaxis_frame.grid(row=0, column=1, sticky='nswe')
        pvis_2d_xaxis_frame.rowconfigure(0,weight=1)
        pvis_2d_xaxis_frame.rowconfigure(1,weight=1)

        pvis_2d_yaxis_frame = ttk.Frame(pvis_2d_frame)
        pvis_2d_yaxis_frame.grid(row=1, column=1, sticky='nswe')
        pvis_2d_yaxis_frame.rowconfigure(0,weight=1)
        pvis_2d_yaxis_frame.rowconfigure(1,weight=1)

        pvis_2d_plot_frame = ttk.Frame(pvis_2d_frame)
        pvis_2d_plot_frame.grid(row=2, column=0, columnspan=2, sticky='nswe', pady=(10,2)) 
        pvis_2d_plot_frame.columnconfigure(0,weight=1)
        pvis_2d_plot_frame.columnconfigure(1,weight=1) 

        # map frame
        pvis_map_frame = ttk.LabelFrame(pvis_frame, text="Map visualization", labelanchor='n')
        pvis_map_frame.grid(row=0, column=1, sticky='nswe')
        
        # globe frame
        pvis_globe_frame = ttk.LabelFrame(pvis_frame, text="Globe visualization", labelanchor='n')
        pvis_globe_frame.grid(row=0, column=2, sticky='nswe')

        # define the widgets inside the frames        
        # exec frame
        pexec_btn = ttk.Button(pexec_frame, text="Propagate", command=lambda:self.click_pexec_btn(prop_progress_bar))
        pexec_btn.grid(row=0, column=0, sticky='w', padx=20)

        prop_progress_bar = ttk.Progressbar(pexec_frame, orient='horizontal', length=300, mode='indeterminate')
        prop_progress_bar.grid(row=0, column=1, padx=20, sticky='w')
        
        # 2D vis frame
        ttk.Label(pvis_2d_time_frame, text="Time (hh:mm:ss)", wraplength="75", justify='center').grid(row=0, column=0,ipady=5)
        ttk.Label(pvis_2d_time_frame, text="From").grid(row=1, column=0, sticky='s')
        time_from_entry = ttk.Entry(pvis_2d_time_frame, width=10)
        time_from_entry.grid(row=2, column=0, sticky='n')
        time_from_entry.insert(0,'00:00:00')
        time_from_entry.bind("<FocusIn>", lambda args: time_from_entry.delete('0', 'end'))
        
        ttk.Label(pvis_2d_time_frame, text="To").grid(row=3, column=0, sticky='s')
        time_to_entry = ttk.Entry(pvis_2d_time_frame, width=10)
        time_to_entry.grid(row=4, column=0, sticky='n')
        time_to_entry.insert(0,'10:00:00')
        time_to_entry.bind("<FocusIn>", lambda args: time_to_entry.delete('0', 'end'))

        pvis_2d_x_sel_var_btn = ttk.Button(pvis_2d_xaxis_frame, text="X.Var", command=self.click_2dvis_select_xvar_btn)
        pvis_2d_x_sel_var_btn.grid(row=0, column=0)
        self.pvis_2d_x_sel_var_disp = tk.Text(pvis_2d_xaxis_frame, state='disabled',height = 1, width = 3, background="light grey")
        self.pvis_2d_x_sel_var_disp.grid(row=1, column=0, sticky='nsew', padx=10)    

        pvis_2d_y_sel_var_btn = ttk.Button(pvis_2d_yaxis_frame, text="Y.Var(s)", command=self.click_2dvis_select_yvar_btn)
        pvis_2d_y_sel_var_btn.grid(row=0, column=0)
        self.pvis_2d_y_sel_var_disp = tk.Text(pvis_2d_yaxis_frame, state='disabled',height = 2, width = 3, background="light grey")
        self.pvis_2d_y_sel_var_disp.grid(row=1, column=0, sticky='nsew', padx=10) 
        
        plot_btn = ttk.Button(pvis_2d_plot_frame, text="Plot")
        plot_btn.grid(row=0, column=0)

        export_btn = ttk.Button(pvis_2d_plot_frame, text="Export")
        export_btn.grid(row=0, column=1)

        # map vis frame
        ttk.Label(pvis_map_frame, text="TBD").grid(row=0, column=0)
        ttk.Label(pvis_map_frame, text="Time Interval (from mission epoch)", wraplength=100).grid(row=0, column=0)

        # globe vis frame
        ttk.Label(pvis_globe_frame, text="TBD").grid(row=0, column=0)
        ttk.Label(pvis_globe_frame, text="Time Interval (from mission epoch)", wraplength=100).grid(row=0, column=0)        


    def click_2dvis_select_xvar_btn(self):
        # create window to ask which satellite 
        select_xvar_win = tk.Toplevel()
        select_xvar_win.rowconfigure(0,weight=1)
        select_xvar_win.rowconfigure(1,weight=1)
        select_xvar_win.columnconfigure(0,weight=1)
        select_xvar_win.columnconfigure(1,weight=1)

        select_sat_win_frame = ttk.LabelFrame(select_xvar_win, text='Select Satellite')
        select_sat_win_frame.grid(row=0, column=0, padx=10, pady=10) 

        select_var_frame = ttk.LabelFrame(select_xvar_win, text='Select Variable')
        select_var_frame.grid(row=0, column=1, padx=10, pady=10) 

        okcancel_frame = ttk.Label(select_xvar_win)
        okcancel_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10) 

        # place the widgets in the frame
        available_sats = out_config.get_satellites()  # get all available sats for which outputs are available
 
        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.grid(row=0, column=0)

        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.grid(row=0, column=0)

        VARS = [("Time", "Time"), ("Altitude [km]", "Alt"), ("Inclination [deg]", "Inc"), ("True Anomaly [deg]", "TA"), ("RAAN [deg]", "RAAN"),
                ("AOP [deg]", "AOP"), ("Speed [km/s]", "Spd"), ("ECI-X Position [km]", "eci_x"), ("ECI-Y Position [km]", "eci_y"), ("ECI-Z Position [km]", "eci_z"),
                ("ECI-VX Velocity [km/s]", "eci_vx"), ("ECI-VY Velocity [km/s]", "eci_vy"), ("ECI-VZ Velocity [km/s]", "eci_vz")]
        self._2dvis_xvar= tk.StringVar() # using self so that the variable is retained even after exit from the function, make sure variable name is unique
        j = 0
        k = 0
        for text, mode in VARS:
            var_rbtn = ttk.Radiobutton(select_var_frame, text=text, variable=self._2dvis_xvar, value=mode)
            var_rbtn.grid(row=j, column=k, sticky='w')
            j = j + 1
            if(j==5):
                j=0
                k=k+1

        def click_ok_btn():
            two_dim_vis_plt_attr.update_x_variables(sats_combo_box.get(), self._2dvis_xvar.get())
            self.pvis_2d_x_sel_var_disp.configure(state='normal')
            self.pvis_2d_x_sel_var_disp.delete(1.0,'end')
            self.pvis_2d_x_sel_var_disp.insert(1.0,str(sats_combo_box.get())+"."+ str(self._2dvis_xvar.get()))
            self.pvis_2d_x_sel_var_disp.configure(state='disabled')
            select_xvar_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=click_ok_btn, width=PropagateFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0, sticky ='e')
        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=select_xvar_win.destroy, width=PropagateFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1, sticky ='w') 

    def click_2dvis_select_yvar_btn(self):
        # create window to ask which satellite 
        select_yvar_win = tk.Toplevel()
        select_yvar_win.rowconfigure(0,weight=1)
        select_yvar_win.rowconfigure(1,weight=1)
        select_yvar_win.columnconfigure(0,weight=1)
        select_yvar_win.columnconfigure(1,weight=1)

        select_sat_win_frame = ttk.LabelFrame(select_yvar_win, text='Select Satellite')
        select_sat_win_frame.grid(row=0, column=0, padx=10, pady=10) 

        select_var_frame = ttk.LabelFrame(select_yvar_win, text='Select Variable')
        select_var_frame.grid(row=0, column=1, padx=10, pady=10) 

        okcancel_frame = ttk.Label(select_yvar_win)
        okcancel_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10) 

        # place the widgets in the frame
        available_sats = out_config.get_satellites()  # get all available sats for which outputs are available
 
        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.grid(row=0, column=0)

        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.grid(row=0, column=0)

        VARS = [("Time", "Time"), ("Altitude [km]", "Alt"), ("Inclination [deg]", "Inc"), ("True Anomaly [deg]", "TA"), ("RAAN [deg]", "RAAN"),
                ("AOP [deg]", "AOP"), ("Speed [km/s]", "Spd"), ("ECI-X Position [km]", "eci_x"), ("ECI-Y Position [km]", "eci_y"), ("ECI-Z Position [km]", "eci_z"),
                ("ECI-VX Velocity [km/s]", "eci_vx"), ("ECI-VY Velocity [km/s]", "eci_vy"), ("ECI-VZ Velocity [km/s]", "eci_vz")]
        self._2dvis_yvar= tk.StringVar() # using self so that the variable is retained even after exit from the function, make sure variable name is unique
        j = 0
        k = 0
        for text, mode in VARS:
            var_rbtn = ttk.Radiobutton(select_var_frame, text=text, variable=self._2dvis_yvar, value=mode)
            var_rbtn.grid(row=j, column=k, sticky='w')
            j = j + 1
            if(j==5):
                j=0
                k=k+1

        def click_ok_btn():
            two_dim_vis_plt_attr.update_y_variables(sats_combo_box.get(), self._2dvis_yvar.get())
            
        def click_exit_btn():
            self.pvis_2d_y_sel_var_disp.configure(state='normal')
            self.pvis_2d_y_sel_var_disp.delete(1.0,'end')
            [sats, yvars] = two_dim_vis_plt_attr.get_y_variables()
            yvars_str = [str(sats[k]+'.'+yvars[k]) for k in range(0,len(sats))]
            self.pvis_2d_y_sel_var_disp.insert(1.0,' '.join(yvars_str))
            self.pvis_2d_y_sel_var_disp.configure(state='disabled')
            select_yvar_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=click_ok_btn, width=PropagateFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0, sticky ='e')
        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=click_exit_btn, width=PropagateFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1, sticky ='w') 

    def click_2dvis_plot2d_btn(self):
        pass

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
                sat_kep_state_fp.append(pcp.sat_state_fl + 'Keplerian')
                print(".......Done.......")

            # save output configuration file (any previous configuration is re-written since propagation is the first step 
            # to any of the future calculations such as coverage or communications, etc)

            out_config.update_prop_out(prop_done=True, sat_id=sat_id, sat_eci_state_fp=sat_eci_state_fp, sat_kep_state_fp=sat_kep_state_fp) 
            with open('output.json', 'w', encoding='utf-8') as f:
                json.dump(out_config.to_dict(), f, ensure_ascii=False, indent=4)

            prop_progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_pexec_btn).start()

        

      
        

