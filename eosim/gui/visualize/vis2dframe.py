""" 
.. module:: vis2dframe

:synopsis: *Module to handle visualization with X-Y plots.*

The module contains the class ``Vis2DFrame`` to build the frame in which the user enters the plotting parameters. 
A time-interval of interest is to be specified, and the X, Y data corresponding to this time-interval shall be plotted. 
A single x-variable (belonging to a satellite) is selected (see the class ``Plot2DVisVars`` for list of possible variables).
Multiple y-variables may be selected to be plotted on the same figure. 

The module currently only allows plotting of satellite orbit-propagation parameters (and hence association of only the satellite 
(no need of sensor) with the variable is sufficient).

"""

from tkinter import ttk 
import tkinter as tk
import tkinter.filedialog, tkinter.messagebox
from eosim import config
import orbitpy, instrupy
import pandas as pd
import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import logging
logger = logging.getLogger(__name__)

class Plot2DVisVars(instrupy.util.EnumEntity):
    """ This class holds and handles the variables which can be plotted (either on x or y axis). 
        The class-variables are all the variables make up all the possible variables which can be plotted. 
        The class also includes two functions which aid in the retrieval of the variable-data from the OrbitPy datafiles.
    
    """
    TIME = "Time"
    ALT = "Altitude [km]"
    INC = "Inclination [deg]"
    TA = "True Anomaly [km]"
    RAAN = "RAAN [deg]"
    AOP = "AOP [deg]"
    ECC = "ECC"
    SPD = "ECI Speed [km/s]"
    ECIX = "ECI X-position [km]"
    ECIY = "ECI Y-position [km]"
    ECIZ = "ECI Z-position [km]"
    VX = "ECI X Velocity [km/s]"
    VY = "ECI Y Velocity [km/s]"
    VZ = "ECI Z Velocity [km/s]"
    LAT = "Latitude [deg]"
    LON = "Longitude [deg]"

    @classmethod
    def get_orbitpy_file_column_header(cls, var):
        """ Function returns the OrbitPy column header (label) corresponding to the input variable. 
            If not present, ``False`` is returned indicating a "derived" variable.
        """
        if(var==cls.ECIX):
            return "x [km]"
        elif(var==cls.ECIY):
            return "y [km]"
        elif(var==cls.ECIZ):
            return "z [km]"
        elif(var==cls.VX):
            return "vx [km/s]"
        elif(var==cls.VY):
            return "vy [km/s]"
        elif(var==cls.VZ):
            return "vz [km/s]"
        elif(var==cls.INC):
            return "inc [deg]"
        elif(var==cls.RAAN):
            return "raan [deg]"
        elif(var==cls.AOP):
            return "aop [deg]"
        elif(var==cls.TA):
            return "ta [deg]"
        elif(var==cls.ECC):
            return "ecc"
        else:
            return False # could be a derived variable
    
    @classmethod
    def get_data_from_orbitpy_file(cls, sat_df, sat_id, var, step_size, epoch_JDUT1):
        """ Extract the variable data from the input orbit-propagation data. 

            :param sat_df: Dataframe corresponding to the orbit-propagation data.
            :paramtype sat_df: :class:`pandas.DataFrame`

            :param sat_id: Satellite identifier.
            :paramtype sat_id: str or int

            :param var: Variable of interest to be plotted (on either the X or Y axis).
            :paramtype var: class-variable of the ``Plot2DVisVars`` class.

            :param step_size: step-size
            :paramtype step_size: float

            :param epoch_JDUT1: Epoch in Julian Date UT1 at which the input data is referenced.
            :paramtype epoch_JDUT1: float

            :return: Tuple containing the variable plot-name (label) and the corresponding data to be plotted. 
            :rtype: tuple

        """
        _header = Plot2DVisVars.get_orbitpy_file_column_header(var)     
        if(_header is not False):                     
            if _header == sat_df.index.name:
                data = sat_df.index
            else:
                data = sat_df[_header]
        else:
            # a derived variable
            if(var == cls.TIME):
                data = np.array(sat_df.index) * step_size # index = "time index"
                _header = 'time [s]'
            elif(var == cls.ALT):
                sat_dist = []
                sat_dist = np.array(sat_df["x [km]"])*np.array(sat_df["x [km]"]) + np.array(sat_df["y [km]"])*np.array(sat_df["y [km]"]) + np.array(sat_df["z [km]"])*np.array(sat_df["z [km]"])
                sat_dist = np.sqrt(sat_dist)
                data = np.array(sat_dist) - instrupy.util.Constants.radiusOfEarthInKM
                _header = 'alt [km]'
            elif(var==cls.SPD):
                data = np.array(sat_df["vx [km/s]"])*np.array(sat_df["vx [km/s]"]) + np.array(sat_df["vy [km/s]"])*np.array(sat_df["vy [km/s]"]) + np.array(sat_df["vz [km/s]"])*np.array(sat_df["vz [km/s]"])
                data = np.sqrt(data)
                _header = 'speed [km/s]'
            elif(var==cls.LAT):
                lat = np.zeros((len(sat_df["x [km]"]), 1)) # make empty result array
                sat_df_index = list(sat_df.index)
                sat_df_x = list(sat_df["x [km]"])
                sat_df_y = list(sat_df["y [km]"])
                sat_df_z = list(sat_df["z [km]"])
                for k in range(0,len(sat_df["x [km]"])):
                    time = epoch_JDUT1 + sat_df_index[k] * step_size * 1/86400 
                    [lat[k], _x, _y] = instrupy.util.GeoUtilityFunctions.eci2geo([sat_df_x[k], sat_df_y[k], sat_df_z[k]], time)
                data = lat
                _header = 'latitude [deg]'
            elif(var==cls.LON):
                lon = np.zeros((len(sat_df["x [km]"]), 1)) # make empty result array
                sat_df_index = list(sat_df.index)
                sat_df_x = list(sat_df["x [km]"])
                sat_df_y = list(sat_df["y [km]"])
                sat_df_z = list(sat_df["z [km]"])
                for k in range(0,len(sat_df["x [km]"])):
                    time = epoch_JDUT1 + sat_df_index[k] * step_size * 1/86400  
                    [lon[k], _x, _y] = instrupy.util.GeoUtilityFunctions.eci2geo([sat_df_x[k], sat_df_y[k], sat_df_z[k]], time)
                data = lon
                _header = 'longitude [deg]'
            
        return (str(sat_id)+'.'+_header, data)

class TwoDimVisPlotAttributes():
    """ Container class to hold and handle the plot attributes which are specified by the user.
    """
    def __init__(self, x_sat_id=None, x_var=None, y_sat_id=None, y_var=None, time_start=None, time_end=None):
        self.x_sat_id = x_sat_id if x_sat_id is not None else None # x-variable satellite-identifier
        self.x_var = x_var if x_var is not None else None # x-variable
        self.y_sat_id = y_sat_id if y_sat_id is not None else list() # y-variable satellite-identifier. Is a list to accommodate multiple plots over the same x-axis.
        self.y_var = y_var if y_var is not None else list() # y-variable. Is a list to accommodate multiple plots over the same x-axis.
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

class Vis2DFrame(ttk.Frame):
    """ Primary class to create the frame and the widgets."""
    def __init__(self, win, tab):
        
        self.two_dim_vis_plt_attr = TwoDimVisPlotAttributes() # instance variable storing the 2D plot attributes

        # 2d plots frame
        vis_2d_frame = ttk.Frame(tab)
        vis_2d_frame.pack(expand = True, fill ="both", padx=10, pady=10)
        vis_2d_frame.rowconfigure(0,weight=1)
        vis_2d_frame.rowconfigure(1,weight=1)
        vis_2d_frame.columnconfigure(0,weight=1)
        vis_2d_frame.columnconfigure(1,weight=1)             

        vis_2d_time_frame = ttk.LabelFrame(vis_2d_frame, text='Set Time Interval', labelanchor='n')
        vis_2d_time_frame.grid(row=0, column=0, sticky='nswe', rowspan=2, padx=(40,0))
        vis_2d_time_frame.rowconfigure(0,weight=1)
        vis_2d_time_frame.rowconfigure(1,weight=1)
        vis_2d_time_frame.rowconfigure(2,weight=1)
        vis_2d_time_frame.columnconfigure(0,weight=1)
        vis_2d_time_frame.columnconfigure(1,weight=1)

        vis_2d_xaxis_frame = ttk.LabelFrame(vis_2d_frame, text='Set X-variable', labelanchor='n')
        vis_2d_xaxis_frame.grid(row=0, column=1, sticky='nswe')
        vis_2d_xaxis_frame.columnconfigure(0,weight=1)
        vis_2d_xaxis_frame.columnconfigure(1,weight=1)
        vis_2d_xaxis_frame.rowconfigure(0,weight=1)

        vis_2d_yaxis_frame = ttk.LabelFrame(vis_2d_frame, text='Set Y-variable(s)', labelanchor='n')
        vis_2d_yaxis_frame.grid(row=1, column=1, sticky='nswe')
        vis_2d_yaxis_frame.columnconfigure(0,weight=1)
        vis_2d_yaxis_frame.columnconfigure(1,weight=1)
        vis_2d_yaxis_frame.rowconfigure(0,weight=1)

        vis_2d_plot_frame = ttk.Frame(vis_2d_frame)
        vis_2d_plot_frame.grid(row=2, column=0, columnspan=2, sticky='nswe', pady=(10,2)) 
        vis_2d_plot_frame.columnconfigure(0,weight=1)
        vis_2d_plot_frame.columnconfigure(1,weight=1) 
        vis_2d_plot_frame.rowconfigure(0,weight=1)

        # 2D vis frame
        ttk.Label(vis_2d_time_frame, text="Time (hh:mm:ss) from mission-epoch", wraplength="110", justify='center').grid(row=0, column=0,columnspan=2,ipady=5)
        
        ttk.Label(vis_2d_time_frame, text="From").grid(row=1, column=0, sticky='ne')
        self.vis_2d_time_from_entry = ttk.Entry(vis_2d_time_frame, width=10, takefocus = False)
        self.vis_2d_time_from_entry.grid(row=1, column=1, sticky='nw', padx=10)
        self.vis_2d_time_from_entry.insert(0,'00:00:00')
        self.vis_2d_time_from_entry.bind("<FocusIn>", lambda args: self.vis_2d_time_from_entry.delete('0', 'end'))
        
        ttk.Label(vis_2d_time_frame, text="To").grid(row=2, column=0, sticky='ne')
        self.vis_2d_time_to_entry = ttk.Entry(vis_2d_time_frame, width=10, takefocus = False)
        self.vis_2d_time_to_entry.grid(row=2, column=1, sticky='nw', padx=10)
        self.vis_2d_time_to_entry.insert(0,'10:00:00')
        self.vis_2d_time_to_entry.bind("<FocusIn>", lambda args: self.vis_2d_time_to_entry.delete('0', 'end'))

        vis_2d_x_sel_var_btn = ttk.Button(vis_2d_xaxis_frame, text="X.Var", command=self.click_select_xvar_btn)
        vis_2d_x_sel_var_btn.grid(row=0, column=0)
        self.vis_2d_x_sel_var_disp = tk.Text(vis_2d_xaxis_frame, state='disabled',height = 1, width = 3, background="light grey")
        self.vis_2d_x_sel_var_disp.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)    

        vis_2d_y_sel_var_btn = ttk.Button(vis_2d_yaxis_frame, text="Y.Var(s)", command=self.click_select_yvar_btn)
        vis_2d_y_sel_var_btn.grid(row=0, column=0)
        self.vis_2d_y_sel_var_disp = tk.Text(vis_2d_yaxis_frame, state='disabled',height = 2, width = 3, background="light grey")
        self.vis_2d_y_sel_var_disp.grid(row=0, column=1, sticky='nsew', padx=20, pady=20) 
        
        plot_btn = ttk.Button(vis_2d_plot_frame, text="Plot", command=lambda: self.click_plot_btn(plot=True))
        plot_btn.grid(row=0, column=0, sticky='e', padx=20)

        export_btn = ttk.Button(vis_2d_plot_frame, text="Export", command=lambda: self.click_plot_btn(export=True))
        export_btn.grid(row=0, column=1, sticky='w', padx=20)

    def click_select_xvar_btn(self):
        """ Create window to ask what should be the x-variable. Only 1 x-variable selection per plot is allowed (for obvious reasons)."""
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
        available_sats = [x._id for x in config.mission.spacecraft]# get all available satellite-ids for which outputs are available
 
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
            self.two_dim_vis_plt_attr.update_x_variables(sats_combo_box.get(), self._2dvis_xvar.get())
            [sats, xvars] = self.two_dim_vis_plt_attr.get_x_variables()
            # write the selected variable in the display window for user
            xvars_str = str(sats + '.' + xvars)
            self.vis_2d_x_sel_var_disp.configure(state='normal')
            self.vis_2d_x_sel_var_disp.delete(1.0,'end')
            self.vis_2d_x_sel_var_disp.insert(1.0, xvars_str)
            self.vis_2d_x_sel_var_disp.configure(state='disabled')
            select_xvar_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=click_ok_btn, width=15)
        ok_btn.grid(row=0, column=0, sticky ='e')
        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=select_xvar_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1, sticky ='w') 

    def click_select_yvar_btn(self):
        """ Create window to ask what should be the y-variable(s). Multiple variables can be configured."""

        # reset any previously configured y-variables
        self.two_dim_vis_plt_attr.reset_y_variables()
        
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
        available_sats = [x._id for x in config.mission.spacecraft]# get all available satellite-ids for which outputs are available
 
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
            self.two_dim_vis_plt_attr.update_y_variables(sats_combo_box.get(), self._2dvis_yvar.get())
            
        def click_exit_btn():
            self.vis_2d_y_sel_var_disp.configure(state='normal')
            self.vis_2d_y_sel_var_disp.delete(1.0,'end')
            # write the selected variable in the display window for user
            [sats, yvars] = self.two_dim_vis_plt_attr.get_y_variables()
            yvars_str = [str(sats[k]+'.'+yvars[k]) for k in range(0,len(sats))]
            self.vis_2d_y_sel_var_disp.insert(1.0,' '.join(yvars_str))
            self.vis_2d_y_sel_var_disp.configure(state='disabled')
            select_yvar_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=click_ok_btn, width=15)
        ok_btn.grid(row=0, column=0, sticky ='e')
        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=click_exit_btn, width=15)
        cancel_btn.grid(row=0, column=1, sticky ='w') 

    def update_time_interval_in_attributes_variable(self):
        """ Update the time-interval of interest from the user-input."""
        # read the plotting time interval 
        time_start = str(self.vis_2d_time_from_entry.get()).split(":") # split and reverse list
        time_start.reverse()
        # convert to seconds
        x = 0
        for k in range(0,len(time_start)):
            x = x + float(time_start[k]) * (60**k)
        time_start_s = x

        time_end = str(self.vis_2d_time_to_entry.get()).split(":") # split and reverse list
        time_end.reverse()
        # convert to seconds
        x = 0
        for k in range(0,len(time_end)):
            x = x + float(time_end[k]) * (60**k)
        time_end_s = x

        self.two_dim_vis_plt_attr.update_time_interval(time_start_s, time_end_s)
        
    def click_plot_btn(self, export=False, plot=False):
        """ Make X-Y scatter plots of the variables indicated in :code:`two_dim_vis_plt_attr` instance variable. 
        """
        # get the time-interval of interest
        self.update_time_interval_in_attributes_variable()
        [time_start_s, time_end_s] = self.two_dim_vis_plt_attr.get_time_interval()

        # get the x-axis data
        [x_sat_id, x_var] = self.two_dim_vis_plt_attr.get_x_variables()

        # search for the orbit-propagation data corresponding to the satellite with identifier = x_sat_id
        x_sat_prop_out_info = orbitpy.util.OutputInfoUtility.locate_output_info_object_in_list(out_info_list=config.mission.outputInfo,
                                                                         out_info_type=orbitpy.util.OutputInfoUtility.OutputInfoType.PropagatorOutputInfo,
                                                                         spacecraft_id=x_sat_id
                                                                        )
        x_sat_state_fp = x_sat_prop_out_info.stateCartFile
        x_sat_kepstate_fp = x_sat_prop_out_info.stateKeplerianFile
        
        # read the epoch and time-step size and fix the start and stop indices
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(x_sat_state_fp)

        logger.debug("epoch_JDUT1 is " + str(epoch_JDUT1))
        logger.debug("step_size is " + str(step_size))

        time_start_index = int(time_start_s/step_size)
        time_end_index = int(time_end_s/step_size)
        
        # Get the orbit-propagation data.
        # Cartesian ECI state file
        x_sat_state_df = pd.read_csv(x_sat_state_fp,skiprows = [0,1,2,3]) 
        x_sat_state_df.set_index('time index', inplace=True)
        # Keplerian state file
        x_sat_kepstate_df = pd.read_csv(x_sat_kepstate_fp,skiprows = [0,1,2,3]) 
        x_sat_kepstate_df.set_index('time index', inplace=True)

        # check if the user-specified time interval is within bounds
        min_time_index = min(x_sat_state_df.index)
        max_time_index = max(x_sat_state_df.index)
        if(time_start_index < min_time_index or time_start_index > max_time_index or 
           time_end_index < min_time_index or time_end_index > max_time_index or
           time_start_index > time_end_index):
            logger.info("Please enter valid time-interval.")
            return

        # get data only in the relevant time-interval
        x_sat_state_df = x_sat_state_df.iloc[time_start_index:time_end_index]
        x_sat_kepstate_df = x_sat_kepstate_df.iloc[time_start_index:time_end_index]
        x_sat_df = pd.concat([x_sat_state_df, x_sat_kepstate_df], axis=1)

        # make empty dataframe to store the plot related data
        plt_data = pd.DataFrame(index=x_sat_state_df.index)
        # extract the x-variable from the orbit-propagation data
        (_xvarname, _xdata) = Plot2DVisVars.get_data_from_orbitpy_file(sat_df=x_sat_df, sat_id=x_sat_id, var=x_var, step_size=step_size, epoch_JDUT1=epoch_JDUT1)
        plt_data[_xvarname] = _xdata  

        # iterate over the list of y-vars 
        [y_sat_id, y_var] = self.two_dim_vis_plt_attr.get_y_variables()
        num_y_vars = len(y_var)
        for k in range(0,num_y_vars): 
            # extract the y-variable data from of the particular satellite
            # search for the orbit-propagation data corresponding to the satellite with identifier = y_sat_id[k]
            y_sat_prop_out_info = orbitpy.util.OutputInfoUtility.locate_output_info_object_in_list(out_info_list=config.mission.outputInfo,
                                                                            out_info_type=orbitpy.util.OutputInfoUtility.OutputInfoType.PropagatorOutputInfo,
                                                                            spacecraft_id=y_sat_id[k]
                                                                            )
            y_sat_state_fp = y_sat_prop_out_info.stateCartFile
            y_sat_kepstate_fp = y_sat_prop_out_info.stateKeplerianFile

            # load the cartesian eci state data, get data only in the relevant time-interval
            y_sat_state_df = pd.read_csv(y_sat_state_fp, skiprows = [0,1,2,3]) 
            y_sat_state_df.set_index('time index', inplace=True)
            y_sat_state_df = y_sat_state_df.iloc[time_start_index:time_end_index]
            # load the keplerian state data, get data only in the relevant time-interval
            y_sat_kepstate_df = pd.read_csv(y_sat_kepstate_fp, skiprows = [0,1,2,3]) 
            y_sat_kepstate_df.set_index('time index', inplace=True)
            y_sat_kepstate_df = y_sat_kepstate_df.iloc[time_start_index:time_end_index]
            
            y_sat_df = pd.concat([y_sat_state_df, y_sat_kepstate_df], axis=1)

            # add new column with the y-data
            (_yvarname, _ydata) = Plot2DVisVars.get_data_from_orbitpy_file(sat_df=y_sat_df, sat_id=y_sat_id[k], var=y_var[k], step_size=step_size, epoch_JDUT1=epoch_JDUT1)
            plt_data[_yvarname] = _ydata          
        
        if(export is True):
            vis2d_data_fp = tkinter.filedialog.asksaveasfile()
            plt_data.to_csv(vis2d_data_fp)
            
        if(plot is True):
            fig_win = tk.Toplevel()
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            _lgnd=[]
            for k in range(0,num_y_vars):
                ax.scatter(plt_data.iloc[:,0],plt_data.iloc[:,k+1])
                _lgnd.append(plt_data.columns[k+1])  # pylint: disable=E1136  # pylint/issues/3139
            ax.set_xlabel(plt_data.columns[0])  # pylint: disable=E1136  # pylint/issues/3139
            ax.set_ylabel('Y-axis')
            ax.legend(_lgnd)
            
            canvas = FigureCanvasTkAgg(fig, master=fig_win)  # A tk.DrawingArea.
            canvas.draw()
            canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, fig_win)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
            
 