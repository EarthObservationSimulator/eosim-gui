from tkinter import ttk 
import tkinter as tk
import tkinter.filedialog, tkinter.messagebox
from eosim import config
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util
import instrupy
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
                sat_dist = []
                sat_dist = np.array(sat_df["X[km]"])*np.array(sat_df["X[km]"]) + np.array(sat_df["Y[km]"])*np.array(sat_df["Y[km]"]) + np.array(sat_df["Z[km]"])*np.array(sat_df["Z[km]"])
                sat_dist = np.sqrt(sat_dist)
                data = np.array(sat_dist) - instrupy.util.Constants.radiusOfEarthInKM
                _header = 'Alt[km]'
            elif(var==cls.SPD):
                data = np.array(sat_df["VX[km/s]"])*np.array(sat_df["VX[km/s]"]) + np.array(sat_df["VY[km/s]"])*np.array(sat_df["VY[km/s]"]) + np.array(sat_df["VZ[km/s]"])*np.array(sat_df["VZ[km/s]"])
                data = np.sqrt(data)
                _header = 'Speed[km/s]'
            elif(var==cls.LAT):
                lat = np.zeros((len(sat_df["X[km]"]), 1))
                for k in range(0,len(sat_df["X[km]"])):
                    [lat[k], _x, _y] = instrupy.util.MathUtilityFunctions.eci2geo([sat_df["X[km]"][k], sat_df["Y[km]"][k], sat_df["Z[km]"][k]], epoch_JDUT1)
                data = lat
                _header = 'Latitude[deg]'
            elif(var==cls.LON):
                lon = np.zeros((len(sat_df["X[km]"]), 1))
                for k in range(0,len(sat_df["X[km]"])):
                    [_x, lon[k], _y] = instrupy.util.MathUtilityFunctions.eci2geo([sat_df["X[km]"][k], sat_df["Y[km]"][k], sat_df["Z[km]"][k]], epoch_JDUT1)
                data = lon
                _header = 'Longitude[deg]'
            
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

class Vis2DFrame(ttk.Frame):

    def __init__(self, win, tab):
        
        self.two_dim_vis_plt_attr = TwoDimVisPlotAttibutes() # data structure storing the 2D plot attributes

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
        available_sats = config.out_config.get_satellite_ids()  # get all available sats for which outputs are available
 
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
            xvars_str = str(sats+'.'+xvars)
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
        available_sats = config.out_config.get_satellite_ids()  # get all available sats for which outputs are available
 
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
        """ Make X-Y scatter plots of the variables indicated in :code:`self.two_dim_vis_plt_attr` instance variable. 
        """
        
        self.update_time_interval_in_attributes_variable()

        [time_start_s, time_end_s] = self.two_dim_vis_plt_attr.get_time_interval()

        # get the x-axis data
        [x_sat_id, x_var] = self.two_dim_vis_plt_attr.get_x_variables()
        x_sat_state_fp = config.out_config.get_satellite_state_fp()[config.out_config.get_satellite_ids().index(x_sat_id)]
        x_sat_kepstate_fp = config.out_config.get_satellite_kepstate_fp()[config.out_config.get_satellite_ids().index(x_sat_id)]
        
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

        # get data only in the relevant time-interval
        x_sat_state_df = x_sat_state_df.iloc[time_start_index:time_end_index]
        x_sat_kepstate_df = x_sat_kepstate_df.iloc[time_start_index:time_end_index]
        x_sat_df = pd.concat([x_sat_state_df, x_sat_kepstate_df], axis=1)

        # make empty dataframe to store the plot related data
        # extract the time and x-var 
        plt_data = pd.DataFrame(index=x_sat_state_df.index)
        
        [_xvarname, _xdata] = Plot2DVisVars.get_data_from_orbitpy_file(sat_df=x_sat_df, sat_id=x_sat_id, var=x_var, step_size=step_size, epoch_JDUT1=epoch_JDUT1)
        plt_data[_xvarname] = _xdata  

        # iterate over the list of y-vars 
        [y_sat_id, y_var] = self.two_dim_vis_plt_attr.get_y_variables()
        num_y_vars = len(y_var)
        for k in range(0,num_y_vars): 
            # extract the y-variable data from of the particular satellite
            # cartesian eci state file
            y_sat_state_fp = config.out_config.get_satellite_state_fp()[config.out_config.get_satellite_ids().index(y_sat_id[k])]
            y_sat_state_df = pd.read_csv(y_sat_state_fp,skiprows = [0,1,2,3]) 
            y_sat_state_df.set_index('TimeIndex', inplace=True)
            y_sat_state_df = y_sat_state_df.iloc[time_start_index:time_end_index]
            # keplerian state file
            y_sat_kepstate_fp = config.out_config.get_satellite_kepstate_fp()[config.out_config.get_satellite_ids().index(y_sat_id[k])]
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
            
 