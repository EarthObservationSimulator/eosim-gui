from tkinter import ttk 
import tkinter as tk
from eosim.config import GuiStyle, MissionConfig
import eosim.gui.helpwindow as helpwindow
from eosim import config
import instrupy
import pandas as pd
import numpy as np
import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import logging

logger = logging.getLogger(__name__)

class PlotMapVars(instrupy.util.EnumEntity):
    TIME = "Time"
    ALT = "Altitude [km]"
    INC = "Inclination [deg]"
    TA = "True Anomaly [km]"
    RAAN = "RAAN [deg]"
    AOP = "AOP [deg]"
    ECC = "ECC"
    SPD = "ECI Speed [km/s]"

    @classmethod
    def get_orbitpy_file_column_header(cls, var):
        if(var==cls.INC):
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
        _header = PlotMapVars.get_orbitpy_file_column_header(var)     
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
                data = np.array(sat_df["SMA[km]"]) - instrupy.util.Constants.radiusOfEarthInKM
                _header = 'Alt[km]'
            elif(var==cls.SPD):
                data = np.array(sat_df["VX[km/s]"])*np.array(sat_df["VX[km/s]"]) + np.array(sat_df["VY[km/s]"])*np.array(sat_df["VY[km/s]"]) + np.array(sat_df["VZ[km/s]"])*np.array(sat_df["VZ[km/s]"])
                data = np.sqrt(data)
                _header = 'Speed[km/s]'

        return [str(sat_id)+'.'+_header, data]

class MapVisPlotAttibutes():
        def __init__(self, proj=None, sat_id=None, var=None, time_start=None, time_end=None):
            self.sat_id = sat_id if sat_id is not None else list()
            self.var = var if var is not None else list()
            self.proj = proj if proj is not None else None
            self.time_start = time_start if time_start is not None else None
            self.time_end = time_end if time_end is not None else None
        
        def update_variables(self, sat_id, var):
            self.sat_id.append(sat_id)
            self.var.append(var)
        
        def update_projection(self, proj):
            self.proj = proj

        def reset_variables(self):
            self.sat_id =  list()
            self.var = list()

        def update_time_interval(self, time_start, time_end):
            self.time_start = time_start
            self.time_end = time_end

        def get_projection(self):
            return self.proj
        
        def get_variables(self):
            return [self.sat_id, self.var]

        def get_time_interval(self):
            return [self.time_start, self.time_end]

class VisMapFrame(ttk.Frame):    

    def __init__(self, win, tab):
        
        class Mercator(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                mercator_proj_frame = ttk.Frame(self) 
                mercator_proj_frame.grid(row=0, column=0, ipadx=5, ipady=5)
                mercator_proj_frame.bind('<Enter>',lambda event, widget_id="mercator_proj": helpwindow.update_help_window(event, widget_id))

                ttk.Label(mercator_proj_frame, text="Central Longitude [deg]", wraplength=150).grid(row=0, column=0, padx=10, sticky='w')
                self.central_longitude_entry = ttk.Entry(mercator_proj_frame, width=10)
                self.central_longitude_entry.insert(0,0)
                self.central_longitude_entry.bind("<FocusIn>", lambda args: self.central_longitude_entry.delete('0', 'end'))
                self.central_longitude_entry.grid(row=0, column=1, sticky='w')

                ttk.Label(mercator_proj_frame, text="Minimum Latitude [deg]", wraplength=150).grid(row=1, column=0, padx=10, sticky='w')
                self.min_latitude_entry = ttk.Entry(mercator_proj_frame, width=10)
                self.min_latitude_entry.insert(0,-80)
                self.min_latitude_entry.bind("<FocusIn>", lambda args: self.min_latitude_entry.delete('0', 'end'))
                self.min_latitude_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(mercator_proj_frame, text="Maximum Latitude [deg]", wraplength=150).grid(row=2, column=0, padx=10, sticky='w')
                self.max_latitude_entry = ttk.Entry(mercator_proj_frame, width=10)
                self.max_latitude_entry.insert(0,84)
                self.max_latitude_entry.bind("<FocusIn>", lambda args: self.max_latitude_entry.delete('0', 'end'))
                self.max_latitude_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(mercator_proj_frame, text="Latitude True Scale [deg]", wraplength=150).grid(row=3, column=0, padx=10, sticky='w')
                self.lat_true_scale_entry = ttk.Entry(mercator_proj_frame, width=10)
                self.lat_true_scale_entry.insert(0,0)
                self.lat_true_scale_entry.bind("<FocusIn>", lambda args: self.lat_true_scale_entry.delete('0', 'end'))
                self.lat_true_scale_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(mercator_proj_frame, text="False Easting [m]", wraplength=150).grid(row=4, column=0, padx=10, sticky='w')
                self.false_easting_entry = ttk.Entry(mercator_proj_frame, width=10)
                self.false_easting_entry.insert(0,0)
                self.false_easting_entry.bind("<FocusIn>", lambda args: self.false_easting_entry.delete('0', 'end'))
                self.false_easting_entry.grid(row=4, column=1, sticky='w')

                ttk.Label(mercator_proj_frame, text="False Northing [m]", wraplength=150).grid(row=5, column=0, padx=10, sticky='w')
                self.false_northing_entry = ttk.Entry(mercator_proj_frame, width=10)
                self.false_northing_entry.insert(0,0)
                self.false_northing_entry.bind("<FocusIn>", lambda args: self.false_northing_entry.delete('0', 'end'))
                self.false_northing_entry.grid(row=5, column=1, sticky='w')

            def get_specs(self):
                return ccrs.Mercator(central_longitude=float(self.central_longitude_entry.get()), 
                                     min_latitude=float(self.min_latitude_entry.get()), 
                                     max_latitude=float(self.max_latitude_entry.get()), 
                                     latitude_true_scale=float(self.lat_true_scale_entry.get()), 
                                     false_easting=float(self.false_easting_entry.get()), 
                                     false_northing=float(self.false_northing_entry.get()))

        class EquidistantConic(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                equidistconic_proj_frame = ttk.Frame(self) 
                equidistconic_proj_frame.grid(row=0, column=0, ipadx=5, ipady=5)
                
                ttk.Label(equidistconic_proj_frame, text="Central Longitude [deg]", wraplength=150).grid(row=0, column=0, padx=10, sticky='w')
                self.central_longitude_entry = ttk.Entry(equidistconic_proj_frame, width=10)
                self.central_longitude_entry.insert(0,0)
                self.central_longitude_entry.bind("<FocusIn>", lambda args: self.central_longitude_entry.delete('0', 'end'))
                self.central_longitude_entry.grid(row=0, column=1, sticky='w')

                ttk.Label(equidistconic_proj_frame, text="Central Latitude [deg]", wraplength=150).grid(row=1, column=0, padx=10, sticky='w')
                self.central_latitude_entry = ttk.Entry(equidistconic_proj_frame, width=10)
                self.central_latitude_entry.insert(0,0)
                self.central_latitude_entry.bind("<FocusIn>", lambda args: self.central_latitude_entry.delete('0', 'end'))
                self.central_latitude_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(equidistconic_proj_frame, text="False Easting [m]", wraplength=150).grid(row=2, column=0, padx=10, sticky='w')
                self.false_easting_entry = ttk.Entry(equidistconic_proj_frame, width=10)
                self.false_easting_entry.insert(0,0)
                self.false_easting_entry.bind("<FocusIn>", lambda args: self.false_easting_entry.delete('0', 'end'))
                self.false_easting_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(equidistconic_proj_frame, text="False Northing [m]", wraplength=150).grid(row=3, column=0, padx=10, sticky='w')
                self.false_northing_entry = ttk.Entry(equidistconic_proj_frame, width=10)
                self.false_northing_entry.insert(0,0)
                self.false_northing_entry.bind("<FocusIn>", lambda args: self.false_northing_entry.delete('0', 'end'))
                self.false_northing_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(equidistconic_proj_frame, text="Standard Parallel(s) [deg]", wraplength=150).grid(row=4, column=0, padx=10, sticky='w')
                self.standard_parallels_entry = ttk.Entry(equidistconic_proj_frame, width=10)
                self.standard_parallels_entry.insert(0,"20,50")
                self.standard_parallels_entry.bind("<FocusIn>", lambda args: self.standard_parallels_entry.delete('0', 'end'))
                self.standard_parallels_entry.grid(row=4, column=1, sticky='w')
            
            def get_specs(self):
                return ccrs.EquidistantConic(central_longitude=float(self.central_longitude_entry.get()), 
                                             central_latitude=float(self.central_latitude_entry.get()), 
                                             false_easting=float(self.false_easting_entry.get()), 
                                             false_northing=float(self.false_northing_entry.get()),
                                             standard_parallels=tuple(map(float, self.standard_parallels_entry.get().split(','))))

        class LambertConformal(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                lambertconformal_proj_frame = ttk.Frame(self) 
                lambertconformal_proj_frame.grid(row=0, column=0, ipadx=5, ipady=5)

                ttk.Label(lambertconformal_proj_frame, text="Central Longitude [deg]", wraplength=150).grid(row=0, column=0, padx=10, sticky='w')
                self.central_longitude_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
                self.central_longitude_entry.insert(0,-96)
                self.central_longitude_entry.bind("<FocusIn>", lambda args: self.central_longitude_entry.delete('0', 'end'))
                self.central_longitude_entry.grid(row=0, column=1, sticky='w')

                ttk.Label(lambertconformal_proj_frame, text="Central Latitude [deg]", wraplength=150).grid(row=1, column=0, padx=10, sticky='w')
                self.central_latitude_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
                self.central_latitude_entry.insert(0,39)
                self.central_latitude_entry.bind("<FocusIn>", lambda args: self.central_latitude_entry.delete('0', 'end'))
                self.central_latitude_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(lambertconformal_proj_frame, text="False Easting [m]", wraplength=150).grid(row=2, column=0, padx=10, sticky='w')
                self.false_easting_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
                self.false_easting_entry.insert(0,0)
                self.false_easting_entry.bind("<FocusIn>", lambda args: self.false_easting_entry.delete('0', 'end'))
                self.false_easting_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(lambertconformal_proj_frame, text="False Northing [m]", wraplength=150).grid(row=3, column=0, padx=10, sticky='w')
                self.false_northing_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
                self.false_northing_entry.insert(0,0)
                self.false_northing_entry.bind("<FocusIn>", lambda args: self.false_northing_entry.delete('0', 'end'))
                self.false_northing_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(lambertconformal_proj_frame, text="Standard Parallel(s) [deg]", wraplength=150).grid(row=4, column=0, padx=10, sticky='w')
                self.standard_parallels_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
                self.standard_parallels_entry.insert(0,"33,45")
                self.standard_parallels_entry.bind("<FocusIn>", lambda args: self.standard_parallels_entry.delete('0', 'end'))
                self.standard_parallels_entry.grid(row=4, column=1, sticky='w')

                ttk.Label(lambertconformal_proj_frame, text="Cutoff [deg]", wraplength=150).grid(row=5, column=0, padx=10, sticky='w')
                self.cutoff_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
                self.cutoff_entry.insert(0,-30)
                self.cutoff_entry.bind("<FocusIn>", lambda args: self.cutoff_entry.delete('0', 'end'))
                self.cutoff_entry.grid(row=5, column=1, sticky='w')

            def get_specs(self):
                return ccrs.LambertConformal(central_longitude=float(self.central_longitude_entry.get()), 
                                             central_latitude=float(self.central_latitude_entry.get()), 
                                             false_easting=float(self.false_easting_entry.get()), 
                                             false_northing=float(self.false_northing_entry.get()),
                                             standard_parallels=tuple(map(float, self.standard_parallels_entry.get().split(','))),
                                             cutoff=float(self.cutoff_entry.get()))

        class Robinson(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                f = ttk.Frame(self) 
                f.grid(row=0, column=0, ipadx=5, ipady=5)
                ttk.Label(f, text="Robinson Under development").pack() 
        
        class LambertAzimuthalEqualArea(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                f = ttk.Frame(self) 
                f.grid(row=0, column=0, ipadx=5, ipady=5)
                ttk.Label(f, text="LambertAzimuthalEqualArea Under development").pack() 

        class Gnomonic(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                f = ttk.Frame(self) 
                f.grid(row=0, column=0, ipadx=5, ipady=5)
                ttk.Label(f, text="Gnomonic Under development").pack() 

        self.vis_map_attr = MapVisPlotAttibutes() # data structure storing the mapping attributes

        # map plots frame
        vis_map_frame = ttk.Frame(tab)
        vis_map_frame.pack(expand = True, fill ="both", padx=10, pady=10)
        vis_map_frame.rowconfigure(0,weight=1)
        vis_map_frame.rowconfigure(1,weight=1)
        vis_map_frame.columnconfigure(0,weight=1)
        vis_map_frame.columnconfigure(1,weight=1)  
        vis_map_frame.columnconfigure(2,weight=1)             

        vis_map_time_frame = ttk.LabelFrame(vis_map_frame, text='Set Time Interval', labelanchor='n')
        vis_map_time_frame.grid(row=0, column=0, sticky='nswe', padx=(10,0))
        vis_map_time_frame.rowconfigure(0,weight=1)
        vis_map_time_frame.rowconfigure(1,weight=1)
        vis_map_time_frame.rowconfigure(2,weight=1)
        vis_map_time_frame.columnconfigure(0,weight=1)
        vis_map_time_frame.columnconfigure(1,weight=1)

        vis_map_proj_frame = ttk.LabelFrame(vis_map_frame, text='Set Map Projection', labelanchor='n')
        vis_map_proj_frame.grid(row=0, column=1, sticky='nswe')
        vis_map_proj_frame.columnconfigure(0,weight=1)
        vis_map_proj_frame.rowconfigure(0,weight=1)
        vis_map_proj_frame.rowconfigure(1,weight=1)

        vis_map_proj_type_frame = ttk.Frame(vis_map_proj_frame)
        vis_map_proj_type_frame.grid(row=0, column=0)       
        proj_specs_container = ttk.Frame(vis_map_proj_frame)
        proj_specs_container.grid(row=1, column=0, sticky='nswe')
        proj_specs_container.columnconfigure(0,weight=1)
        proj_specs_container.rowconfigure(0,weight=1)

        proj_specs_container_frames = {}
        for F in (Mercator, EquidistantConic, LambertConformal,Robinson,LambertAzimuthalEqualArea,Gnomonic):
            page_name = F.__name__
            self._prj_typ_frame = F(parent=proj_specs_container, controller=self)
            proj_specs_container_frames[page_name] = self._prj_typ_frame
            self._prj_typ_frame.grid(row=0, column=0, sticky="nsew")
        self._prj_typ_frame = proj_specs_container_frames['Mercator'] # default projection type
        self._prj_typ_frame.tkraise()

        vis_map_var_frame = ttk.LabelFrame(vis_map_frame, text='Set Variable(s)', labelanchor='n')
        vis_map_var_frame.grid(row=0, column=2, sticky='nswe')
        vis_map_var_frame.columnconfigure(0,weight=1)
        vis_map_var_frame.rowconfigure(0,weight=1)
        vis_map_var_frame.rowconfigure(1,weight=1)

        vis_map_plot_frame = ttk.Frame(vis_map_frame)
        vis_map_plot_frame.grid(row=1, column=0, columnspan=3, sticky='nswe', pady=(10,2)) 
        vis_map_plot_frame.columnconfigure(0,weight=1)
        vis_map_plot_frame.columnconfigure(1,weight=1) 
        vis_map_plot_frame.rowconfigure(0,weight=1)

        # time interval frame
        ttk.Label(vis_map_time_frame, text="Time (hh:mm:ss) from mission-epoch", wraplength="110", justify='center').grid(row=0, column=0,columnspan=2,ipady=5)
        ttk.Label(vis_map_time_frame, text="From").grid(row=1, column=0, sticky='ne')

        self.vis_map_time_from_entry = ttk.Entry(vis_map_time_frame, width=10, takefocus = False)
        self.vis_map_time_from_entry.grid(row=1, column=1, sticky='nw', padx=10)
        self.vis_map_time_from_entry.insert(0,'00:00:00')
        self.vis_map_time_from_entry.bind("<FocusIn>", lambda args: self.vis_map_time_from_entry.delete('0', 'end'))
        
        ttk.Label(vis_map_time_frame, text="To").grid(row=2, column=0, sticky='ne')
        self.vis_map_time_to_entry = ttk.Entry(vis_map_time_frame, width=10, takefocus = False)
        self.vis_map_time_to_entry.grid(row=2, column=1, sticky='nw', padx=10)
        self.vis_map_time_to_entry.insert(0,'10:00:00')
        self.vis_map_time_to_entry.bind("<FocusIn>", lambda args: self.vis_map_time_to_entry.delete('0', 'end'))

        # projection  
        PROJ_TYPES = ['Mercator', 'EquidistantConic', 'LambertConformal', 'Robinson', 'LambertAzimuthalEqualArea', 'Gnomonic']   
             
        self._proj_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._proj_type.set("Mercator") # initialize

        def proj_type_combobox_change(event=None):
            if self._proj_type.get() == "Mercator":
                self._prj_typ_frame = proj_specs_container_frames['Mercator']
            elif self._proj_type.get() == "EquidistantConic":
                self._prj_typ_frame = proj_specs_container_frames['EquidistantConic']
            elif self._proj_type.get() == "LambertConformal":
                self._prj_typ_frame = proj_specs_container_frames['LambertConformal']
            elif self._proj_type.get() == "Robinson":
                self._prj_typ_frame = proj_specs_container_frames['Robinson']
            elif self._proj_type.get() == "LambertAzimuthalEqualArea":
                self._prj_typ_frame = proj_specs_container_frames['LambertAzimuthalEqualArea']
            elif self._proj_type.get() == "Gnomonic":
                self._prj_typ_frame = proj_specs_container_frames['Gnomonic']
            self._prj_typ_frame.tkraise()

        projtype_combo_box = ttk.Combobox(vis_map_proj_type_frame, 
                                        values=PROJ_TYPES, textvariable = self._proj_type, width=25)
        projtype_combo_box.current(0)
        projtype_combo_box.grid(row=0, column=0)
        projtype_combo_box.bind("<<ComboboxSelected>>", proj_type_combobox_change)

        vis_map_var_sel_btn = ttk.Button(vis_map_var_frame, text="Var(s)", command=self.click_select_var_btn)
        vis_map_var_sel_btn.grid(row=0, column=0)
        self.vis_map_var_sel_disp = tk.Text(vis_map_var_frame, state='disabled',height = 2, width = 3, background="light grey")
        self.vis_map_var_sel_disp.grid(row=1, column=0, sticky='nsew', padx=20, pady=20) 
        
        # plot frame
        plot_btn = ttk.Button(vis_map_plot_frame, text="Plot", command=self.click_plot_btn)
        plot_btn.grid(row=0, column=0, sticky='e', padx=20)

    def click_select_var_btn(self):
        # reset any previously configured variables
        self.vis_map_attr.reset_variables()
        
        # create window to ask which satellite 
        select_var_win = tk.Toplevel()
        select_var_win.rowconfigure(0,weight=1)
        select_var_win.rowconfigure(1,weight=1)
        select_var_win.columnconfigure(0,weight=1)
        select_var_win.columnconfigure(1,weight=1)

        select_sat_win_frame = ttk.LabelFrame(select_var_win, text='Select Satellite')
        select_sat_win_frame.grid(row=0, column=0, padx=10, pady=10) 

        select_var_frame = ttk.LabelFrame(select_var_win, text='Select Variable')
        select_var_frame.grid(row=0, column=1, padx=10, pady=10) 

        okcancel_frame = ttk.Label(select_var_win)
        okcancel_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10) 

        # place the widgets in the frame
        available_sats = config.out_config.get_satellite_ids()  # get all available sats for which outputs are available
 
        sats_combo_box = ttk.Combobox(select_sat_win_frame, 
                                        values=available_sats)
        sats_combo_box.current(0)
        sats_combo_box.grid(row=0, column=0)

        self._vis_map_var= tk.StringVar() # using self so that the variable is retained even after exit from the function, make sure variable name is unique
        j = 0
        k = 0
        for _var in list(PlotMapVars):
            var_rbtn = ttk.Radiobutton(select_var_frame, text=_var, variable=self._vis_map_var, value=_var)
            var_rbtn.grid(row=j, column=k, sticky='w')
            j = j + 1
            if(j==5):
                j=0
                k=k+1

        def click_ok_btn():
            self.vis_map_attr.update_variables(sats_combo_box.get(), self._vis_map_var.get())
            
        def click_exit_btn():
            self.vis_map_var_sel_disp.configure(state='normal')
            self.vis_map_var_sel_disp.delete(1.0,'end')
            [sats, vars] = self.vis_map_attr.get_variables()
            vars_str = [str(sats[k]+'.'+vars[k]) for k in range(0,len(sats))]
            self.vis_map_var_sel_disp.insert(1.0,' '.join(vars_str))
            self.vis_map_var_sel_disp.configure(state='disabled')
            select_var_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=click_ok_btn, width=15)
        ok_btn.grid(row=0, column=0, sticky ='e')
        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=click_exit_btn, width=15)
        cancel_btn.grid(row=0, column=1, sticky ='w') 

    def update_time_interval_in_attributes_variable(self):
        # read the plotting time interval 
        time_start = str(self.vis_map_time_from_entry.get()).split(":") # split and reverse list
        time_start.reverse()
        # convert to seconds
        x = 0
        for k in range(0,len(time_start)):
            x = x + float(time_start[k]) * (60**k)
        time_start_s = x

        time_end = str(self.vis_map_time_to_entry.get()).split(":") # split and reverse list
        time_end.reverse()
        # convert to seconds
        x = 0
        for k in range(0,len(time_end)):
            x = x + float(time_end[k]) * (60**k)
        time_end_s = x
        
        self.vis_map_attr.update_time_interval(time_start_s, time_end_s)

    def update_projection_in_attributes_variable(self):
        proj = self._prj_typ_frame.get_specs()
        self.vis_map_attr.update_projection(proj)

    def click_plot_btn(self):
        """ Make projected plots of the variables indicated in :code:`self.vis_map_attr` instance variable. 
        """
        self.update_time_interval_in_attributes_variable()
        self.update_projection_in_attributes_variable()

        [time_start_s, time_end_s] = self.vis_map_attr.get_time_interval()
        proj = self.vis_map_attr.get_projection()

        # get the variable data
        [sat_id, var] = self.vis_map_attr.get_variables()

        # get the epoch and time-step from the file belonging to the first vraible (common among all variables)
        sat_state_fp = config.out_config.get_satellite_state_fp()[config.out_config.get_satellite_ids().index(sat_id[0])]
        
        # read the epoch and time-step size and fix the start and stop indices
        epoch_JDUT1 = pd.read_csv(sat_state_fp, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[2])

        step_size = pd.read_csv(sat_state_fp, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        step_size = float(step_size[0][0].split()[4])

        logger.debug("epoch_JDUT1 is " + str(epoch_JDUT1))
        logger.debug("step_size is " + str(step_size))

        time_start_index = int(time_start_s/step_size)
        time_end_index = int(time_end_s/step_size)

        sat_state_df = pd.read_csv(sat_state_fp,skiprows = [0,1,2,3]) 
        sat_state_df.set_index('TimeIndex', inplace=True)

        min_time_index = min(sat_state_df.index)
        max_time_index = max(sat_state_df.index)
        if(time_start_index < min_time_index or time_start_index > max_time_index or 
           time_end_index < min_time_index or time_end_index > max_time_index or
           time_start_index > time_end_index):
            logger.info("Please enter valid time-interval.")
            return

        sat_state_df = sat_state_df.iloc[time_start_index:time_end_index]
        plt_data = pd.DataFrame(index=sat_state_df.index)
        # iterate over the list of vars 
        num_vars = len(var)
        varname = []
        for k in range(0,num_vars): 
            # extract the y-variable data from of the particular satellite
            # cartesian eci state file
            _sat_state_fp = config.out_config.get_satellite_state_fp()[config.out_config.get_satellite_ids().index(sat_id[k])]
            _sat_state_df = pd.read_csv(_sat_state_fp,skiprows = [0,1,2,3]) 
            _sat_state_df.set_index('TimeIndex', inplace=True)
            _sat_state_df = _sat_state_df.iloc[time_start_index:time_end_index]
            # keplerian state file
            _sat_kepstate_fp = config.out_config.get_satellite_kepstate_fp()[config.out_config.get_satellite_ids().index(sat_id[k])]
            _sat_kepstate_df = pd.read_csv(_sat_kepstate_fp,skiprows = [0,1,2,3]) 
            _sat_kepstate_df.set_index('TimeIndex', inplace=True)
            _sat_kepstate_df = _sat_kepstate_df.iloc[time_start_index:time_end_index]
            
            _sat_df = pd.concat([_sat_state_df, _sat_kepstate_df], axis=1)

            # get the (lat, lon) coords 
            _lat = np.zeros((len(_sat_df["X[km]"]), 1))
            _lon = np.zeros((len(_sat_df["X[km]"]), 1))
            for m in range(0,len(_sat_df["X[km]"])):
                [_lat[m], _lon[m], _y] = instrupy.util.MathUtilityFunctions.eci2geo([_sat_df["X[km]"][m], _sat_df["Y[km]"][m], _sat_df["Z[km]"][m]], epoch_JDUT1)
          
            # add new column with the data
            [_varname, _data] = PlotMapVars.get_data_from_orbitpy_file(sat_df=_sat_df, sat_id=sat_id[k], var=var[k], step_size=step_size, epoch_JDUT1=epoch_JDUT1)
            varname.append(_varname)
            plt_data[_varname+'lat[deg]'] = _lat
            plt_data[_varname+'lon[deg]'] = _lon
            plt_data[_varname] = _data
        
        # make the plot
        fig_win = tk.Toplevel()
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(1,1,1,projection=proj) 
        ax.stock_img()        
        for k in range(0,num_vars):            
            s = ax.scatter(plt_data.loc[:,varname[k]+'lon[deg]'] , plt_data.loc[:,varname[k]+'lat[deg]'], c=plt_data.loc[:,varname[k]], transform=ccrs.PlateCarree()) # TODO: Verify the use of the 'transform' parameter https://scitools.org.uk/cartopy/docs/latest/tutorials/understanding_transform.html,
                                                                                                   #       https://stackoverflow.com/questions/42237802/plotting-projected-data-in-other-projectons-using-cartopy
            cb = fig.colorbar(s)
            cb.set_label(varname[k])
        ax.coastlines()
        
        #cbar.set_clim(-.5, .5) # set limits of color map
                
        canvas = FigureCanvasTkAgg(fig, master=fig_win)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, fig_win)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

            
        
