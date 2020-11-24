from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig, OutputConfig
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

out_config = OutputConfig()  

class Plot2DVisVars(EnumEntity):
    TIME = "Time"
    ALT = "Altitude [km]"
    INC = "Inclination [deg]"
    TA = "True Anomaly [km]"
    RAAN = "RAAN [deg]"
    AOP = "AOP [deg]"
    ECC = "ECC"
    SPD = "Speed [km/s]"
    ECIX = "ECI X-position [km]"
    ECIY = "ECI Y-position [km]"
    ECIZ = "ECI Z-position [km]"
    VX = "ECI VX Velocity [km/s]"
    VY = "ECI VY Velocity [km/s]"
    VZ = "ECI VZ Velocity [km/s]"

    @classmethod
    def get_orbitpy_file_column_header(cls, var):
        if(var==cls.ECIX):
            return "X[km]"
        elif(var==cls.ECIY):
            return "Y[km]"
        elif(var==cls.ECIZ):
            return "Z[km]"
        elif(var==cls.VX):
            return "VX[km/s]"
        elif(var==cls.VY):
            return "VY[km/s]"
        elif(var==cls.VZ):
            return "VZ[km/s]"
        elif(var==cls.INC):
            return "INC[deg]"
        elif(var==cls.RAAN):
            return "RAAN[deg]"
        elif(var==cls.AOP):
            return "AOP[deg]"
        elif(var==cls.TA):
            return "TA[deg]"
        elif(var==cls.ECC):
            return "ECC"
        else:
            return False # could be a derived variable
    
    @classmethod
    def get_data_from_orbitpy_file(cls, sat_df, sat_id, var, step_size, epoch_JDUT1):
        ''' Get data frame the orbitpy resultant output files '''
        _header = Plot2DVisVars.get_orbitpy_file_column_header(var)     
        if(_header is not False):                     
            if _header == sat_df.index.name:
                data = sat_df.index
            else:
                data = sat_df[_header]
        else:
            # a derived variable
            if(var == cls.TIME):
                data = np.array(sat_df.index) * step_size # index = "TimeIndex"
                _header = 'Time[s]'
            elif(var == cls.ALT):
                data = np.array(sat_df["SMA[km]"]) - Constants.radiusOfEarthInKM
                _header = 'Alt[km]'

        return [str(sat_id)+'.'+_header, data]


class TwoDimVisPlotAttibutes():
    def __init__(self, x_sat_id=None, x_var=None, y_sat_id=None, y_var=None, time_start=None, time_end=None):
        self.x_sat_id = x_sat_id if x_sat_id is not None else None
        self.x_var = x_var if x_var is not None else None
        self.y_sat_id = y_sat_id if y_sat_id is not None else list()
        self.y_var = y_var if y_var is not None else list()
        self.time_start = time_start if time_start is not None else None
        self.time_end = time_end if time_end is not None else None

    def update_x_variables(self, x_sat_id, x_var):
        self.x_sat_id = x_sat_id
        self.x_var = x_var
    
    def update_y_variables(self, y_sat_id, y_var):
        self.y_sat_id.append(y_sat_id)
        self.y_var.append(y_var)
    
    def reset_y_variables(self):
        self.y_sat_id =  list()
        self.y_var = list()

    def update_time_interval(self, time_start, time_end):
        self.time_start = time_start
        self.time_end = time_end
    
    def get_x_variables(self):
        return [self.x_sat_id, self.x_var]

    def get_y_variables(self):
        return [self.y_sat_id, self.y_var]
    
    def get_time_interval(self):
        return [self.time_start, self.time_end]

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

        self.pvis_2d_time_from_entry = ttk.Entry(pvis_2d_time_frame, width=10)
        self.pvis_2d_time_from_entry.grid(row=2, column=0, sticky='n')
        self.pvis_2d_time_from_entry.insert(0,'00:00:00')
        self.pvis_2d_time_from_entry.bind("<FocusIn>", lambda args: self.pvis_2d_time_from_entry.delete('0', 'end'))
        
        ttk.Label(pvis_2d_time_frame, text="To").grid(row=3, column=0, sticky='s')
        self.pvis_2d_time_to_entry = ttk.Entry(pvis_2d_time_frame, width=10)
        self.pvis_2d_time_to_entry.grid(row=4, column=0, sticky='n')
        self.pvis_2d_time_to_entry.insert(0,'10:00:00')
        self.pvis_2d_time_to_entry.bind("<FocusIn>", lambda args: self.pvis_2d_time_to_entry.delete('0', 'end'))

        pvis_2d_x_sel_var_btn = ttk.Button(pvis_2d_xaxis_frame, text="X.Var", command=self.click_2dvis_select_xvar_btn)
        pvis_2d_x_sel_var_btn.grid(row=0, column=0)
        self.pvis_2d_x_sel_var_disp = tk.Text(pvis_2d_xaxis_frame, state='disabled',height = 1, width = 3, background="light grey")
        self.pvis_2d_x_sel_var_disp.grid(row=1, column=0, sticky='nsew', padx=10)    

        pvis_2d_y_sel_var_btn = ttk.Button(pvis_2d_yaxis_frame, text="Y.Var(s)", command=self.click_2dvis_select_yvar_btn)
        pvis_2d_y_sel_var_btn.grid(row=0, column=0)
        self.pvis_2d_y_sel_var_disp = tk.Text(pvis_2d_yaxis_frame, state='disabled',height = 2, width = 3, background="light grey")
        self.pvis_2d_y_sel_var_disp.grid(row=1, column=0, sticky='nsew', padx=10) 
        
        plot_btn = ttk.Button(pvis_2d_plot_frame, text="Plot", command=lambda: self.click_2dvis_plot2d_btn(plot=True))
        plot_btn.grid(row=0, column=0)

        export_btn = ttk.Button(pvis_2d_plot_frame, text="Export", command=lambda: self.click_2dvis_plot2d_btn(export=True))
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
        available_sats = out_config.get_satellite_ids()  # get all available sats for which outputs are available
 
        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.grid(row=0, column=0)

        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.current(0)
        sats_combo_box.grid(row=0, column=0)

        self._2dvis_xvar= tk.StringVar() # using self so that the variable is retained even after exit from the function, make sure variable name is unique
        j = 0
        k = 0
        for _var in list(Plot2DVisVars):
            var_rbtn = ttk.Radiobutton(select_var_frame, text=_var, variable=self._2dvis_xvar, value=_var)
            var_rbtn.grid(row=j, column=k, sticky='w')
            j = j + 1
            if(j==5):
                j=0
                k=k+1

        def click_ok_btn():
            two_dim_vis_plt_attr.update_x_variables(sats_combo_box.get(), self._2dvis_xvar.get())
            [sats, xvars] = two_dim_vis_plt_attr.get_x_variables()
            xvars_str = str(sats+'.'+xvars)
            self.pvis_2d_x_sel_var_disp.configure(state='normal')
            self.pvis_2d_x_sel_var_disp.delete(1.0,'end')
            self.pvis_2d_x_sel_var_disp.insert(1.0, xvars_str)
            self.pvis_2d_x_sel_var_disp.configure(state='disabled')
            select_xvar_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=click_ok_btn, width=PropagateFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0, sticky ='e')
        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=select_xvar_win.destroy, width=PropagateFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1, sticky ='w') 

    def click_2dvis_select_yvar_btn(self):

        # reset any previously configured y-variables
        two_dim_vis_plt_attr.reset_y_variables()
        
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
        available_sats = out_config.get_satellite_ids()  # get all available sats for which outputs are available
 
        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.grid(row=0, column=0)

        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.current(0)
        sats_combo_box.grid(row=0, column=0)

        self._2dvis_yvar= tk.StringVar() # using self so that the variable is retained even after exit from the function, make sure variable name is unique
        j = 0
        k = 0
        for _var in list(Plot2DVisVars):
            var_rbtn = ttk.Radiobutton(select_var_frame, text=_var, variable=self._2dvis_yvar, value=_var)
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

    def click_2dvis_plot2d_btn(self, export=False, plot=False):
        """ Make X-Y scatter plots of the variables indicated in :code:`two_dim_vis_plt_attr` global variable. 
        """
        # read the plotting time interval 
        time_start = str(self.pvis_2d_time_from_entry.get()).split(":") # split and reverse list
        time_start.reverse()
        # convert to seconds
        x = 0
        for k in range(0,len(time_start)):
            x = x + float(time_start[k]) * (60**k)
        time_start_s = x

        time_end = str(self.pvis_2d_time_to_entry.get()).split(":") # split and reverse list
        time_end.reverse()
        # convert to seconds
        x = 0
        for k in range(0,len(time_end)):
            x = x + float(time_end[k]) * (60**k)
        time_end_s = x

        two_dim_vis_plt_attr.update_time_interval(time_start_s, time_end_s)

        # get the x-axis data
        [x_sat_id, x_var] = two_dim_vis_plt_attr.get_x_variables()
        x_sat_state_fp = out_config.get_satellite_state_fp()[out_config.get_satellite_ids().index(x_sat_id)]
        x_sat_kepstate_fp = out_config.get_satellite_kepstate_fp()[out_config.get_satellite_ids().index(x_sat_id)]
        
        # read the epoch and time-step size and fix the start and stop indices
        epoch_JDUT1 = pd.read_csv(x_sat_state_fp, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[2])

        step_size = pd.read_csv(x_sat_state_fp, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        step_size = float(step_size[0][0].split()[4])

        logger.debug("epoch_JDUT1 is " + str(epoch_JDUT1))
        logger.debug("step_size is " + str(step_size))

        time_start_index = int(time_start_s/step_size)
        time_end_index = int(time_end_s/step_size)

        # check if the time interval is within bounds
        # Carteisan ECI state file
        x_sat_state_df = pd.read_csv(x_sat_state_fp,skiprows = [0,1,2,3]) 
        x_sat_state_df.set_index('TimeIndex', inplace=True)
        # Keplerian state file
        x_sat_kepstate_df = pd.read_csv(x_sat_kepstate_fp,skiprows = [0,1,2,3]) 
        x_sat_kepstate_df.set_index('TimeIndex', inplace=True)
        
        min_time_index = min(x_sat_state_df.index)
        max_time_index = max(x_sat_state_df.index)
        if(time_start_index < min_time_index or time_start_index > max_time_index or 
           time_end_index < min_time_index or time_end_index > max_time_index or
           time_start_index > time_end_index):
            logger.info("Please enter valid time-interval.")
            return

        # get data only inthe relevant time-interval
        x_sat_state_df = x_sat_state_df.iloc[time_start_index:time_end_index]
        x_sat_kepstate_df = x_sat_kepstate_df.iloc[time_start_index:time_end_index]
        x_sat_df = pd.concat([x_sat_state_df, x_sat_kepstate_df], axis=1)

        # make empty dataframe to store the plot related data
        # extract the time and x-var 
        plt_data = pd.DataFrame(index=x_sat_state_df.index)
        
        [_xvarname, _xdata] = Plot2DVisVars.get_data_from_orbitpy_file(sat_df=x_sat_df, sat_id=x_sat_id, var=x_var, step_size=step_size, epoch_JDUT1=epoch_JDUT1)
        plt_data[_xvarname] = _xdata  

        # iterate over the list of y-vars 
        [y_sat_id, y_var] = two_dim_vis_plt_attr.get_y_variables()
        num_y_vars = len(y_var)
        for k in range(0,num_y_vars): 
            # extract the y-variable data from of the particular satellite
            # cartesian eci state file
            y_sat_state_fp = out_config.get_satellite_state_fp()[out_config.get_satellite_ids().index(y_sat_id[k])]
            y_sat_state_df = pd.read_csv(y_sat_state_fp,skiprows = [0,1,2,3]) 
            y_sat_state_df.set_index('TimeIndex', inplace=True)
            y_sat_state_df = y_sat_state_df.iloc[time_start_index:time_end_index]
            # keplerian state file
            y_sat_kepstate_fp = out_config.get_satellite_kepstate_fp()[out_config.get_satellite_ids().index(y_sat_id[k])]
            y_sat_kepstate_df = pd.read_csv(y_sat_kepstate_fp,skiprows = [0,1,2,3]) 
            y_sat_kepstate_df.set_index('TimeIndex', inplace=True)
            y_sat_kepstate_df = y_sat_kepstate_df.iloc[time_start_index:time_end_index]
            
            y_sat_df = pd.concat([y_sat_state_df, y_sat_kepstate_df], axis=1)

            # add new column with the y-data
            [_yvarname, _ydata] = Plot2DVisVars.get_data_from_orbitpy_file(sat_df=y_sat_df, sat_id=y_sat_id[k], var=y_var[k], step_size=step_size, epoch_JDUT1=epoch_JDUT1)
            plt_data[_yvarname] = _ydata          
        
        if(export is True):
            vis2d_data_fp = tkinter.filedialog.asksaveasfile()
            plt_data.to_csv(vis2d_data_fp)
            
        if(plot is True):
            plt.figure()
            _lgnd=[]
            for k in range(0,num_y_vars):
                plt.scatter(plt_data.iloc[:,0],plt_data.iloc[:,k+1])
                _lgnd.append(plt_data.columns[k+1])  # pylint: disable=E1136  # pylint/issues/3139
                '''plt_data.plot.scatter(x=0,
                        y=1+k,
                        c='DarkBlue')
                '''
            plt.xlabel(plt_data.columns[0])  # pylint: disable=E1136  # pylint/issues/3139
            plt.ylabel('Y-axis')
            plt.legend(_lgnd)
            plt.show()
              
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

            out_config.update_prop_out(prop_done=True, sat_id=sat_id, sat_eci_state_fp=sat_eci_state_fp, sat_kep_state_fp=sat_kep_state_fp) 
            with open('output.json', 'w', encoding='utf-8') as f:
                json.dump(out_config.to_dict(), f, ensure_ascii=False, indent=4)

            prop_progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_pexec_btn).start()

        

      
        

