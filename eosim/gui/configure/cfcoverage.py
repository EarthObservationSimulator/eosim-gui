from tkinter import ttk 
import tkinter as tk
from eosim.config import GuiStyle, MissionConfig
from eosim import config
from eosim.gui.configure import cfmission
import orbitpy
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
import os
import eosim.gui.helpwindow as helpwindow
import pickle
import logging

logger = logging.getLogger(__name__)

class CfCoverage():
    def click_coverage_settings_btn(self):      

        # create and configure child window, parent frame
        cov_win = tk.Toplevel()
        cov_win.rowconfigure(0,weight=1)
        cov_win.rowconfigure(1,weight=1)
        cov_win.rowconfigure(2,weight=1)
        cov_win.columnconfigure(0,weight=1)

        cov_win_frame = ttk.Frame(cov_win)
        cov_win_frame.grid(row=0, column=0, padx=5, pady=5)

        # define all child frames
        cov_type_frame = ttk.LabelFrame(cov_win_frame, text="Coverage Calculator Type")
        cov_type_frame.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        # grid configure
        cov_specs_container = ttk.LabelFrame(cov_win_frame, text="Specifications")
        cov_specs_container.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)
        cov_specs_container.columnconfigure(0,weight=1)
        cov_specs_container.rowconfigure(0,weight=1)

        # okcancel frame
        okcancel_frame = ttk.Label(cov_win_frame)
        okcancel_frame.grid(row=2, column=0, sticky='nswe', padx=5, pady=5)
        okcancel_frame.columnconfigure(0,weight=1)
        okcancel_frame.rowconfigure(0,weight=1)

        class GridPointsCoverageCalculator(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)
                gridpnts_specs_frame = ttk.Frame(self) 
                gridpnts_specs_frame.grid(row=0, column=0, ipadx=5, ipady=5)

                gridpnts_add_by_region_frame = ttk.Frame(gridpnts_specs_frame)
                gridpnts_add_by_region_frame.grid(row=0, column=0)

                gridpnts_add_by_datafile_frame = ttk.Frame(gridpnts_specs_frame)
                gridpnts_add_by_datafile_frame.grid(row=1, column=0)

                # define the widgets inside the child frames
                self._gridpnts_specs_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
                self._gridpnts_specs_type.set("LatLonBounds") # initialize
                def gridpnts_specs_rbtn_click():
                    if self._gridpnts_specs_type.get() == "LatLonBounds":
                        # disable the frame containing the other option, except for the radio-button
                        for child in gridpnts_add_by_datafile_frame.winfo_children():
                            child.configure(state='disable')
                        gridpnts_specs_type_rbtn_2.configure(state='normal')
                        # enable the frame containing the current option
                        for child in gridpnts_add_by_region_frame.winfo_children():
                            child.configure(state='normal')
                        
                    elif self._gridpnts_specs_type.get() == "DataFile":
                        # disable the frame containing the other option, except for the radio-button
                        for child in gridpnts_add_by_region_frame.winfo_children():
                            child.configure(state='disable')   
                        gridpnts_specs_type_rbtn_1.configure(state='normal')
                        # enable the frame containing the current option
                        for child in gridpnts_add_by_datafile_frame.winfo_children():
                            child.configure(state='normal')             

                gridpnts_specs_type_rbtn_1 = ttk.Radiobutton(gridpnts_add_by_region_frame, text="Lat/Lon bounds", command=gridpnts_specs_rbtn_click,
                                                             variable=self._gridpnts_specs_type, value="LatLonBounds")
                gridpnts_specs_type_rbtn_1.grid(row=0, column=0, padx=10, pady=10)

                self.region_info = []
                def add_region():
                    self.region_info.append({'@id': float(gridpnts_specs_regid_entry.get()), 
                                             'latLower': float(gridpnts_specs_latlow_entry.get()), 
                                             'latUpper': float(gridpnts_specs_latup_entry.get()),                                              
                                             'lonLower': float(gridpnts_specs_lonlow_entry.get()),
                                             'lonUpper': float(gridpnts_specs_lonup_entry.get())})


                ttk.Button(gridpnts_add_by_region_frame, text="Add region", command=add_region).grid(row=0, column=1, padx=10, pady=10)
                
                ttk.Label(gridpnts_add_by_region_frame, text="Region ID").grid(row=1, column=0, sticky='w', padx=10, pady=10)
                gridpnts_specs_regid_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                gridpnts_specs_regid_entry.insert(0,random.randint(0,100))
                gridpnts_specs_regid_entry.bind("<FocusIn>", lambda args: gridpnts_specs_regid_entry.delete('0', 'end'))
                gridpnts_specs_regid_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(gridpnts_add_by_region_frame, text="Lat lower [deg]").grid(row=2, column=0, sticky='w', padx=10, pady=10)
                gridpnts_specs_latlow_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                gridpnts_specs_latlow_entry.insert(0,-10)
                gridpnts_specs_latlow_entry.bind("<FocusIn>", lambda args: gridpnts_specs_latlow_entry.delete('0', 'end'))
                gridpnts_specs_latlow_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(gridpnts_add_by_region_frame, text="Lat upper [deg]").grid(row=3, column=0, sticky='w', padx=10, pady=10)
                gridpnts_specs_latup_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                gridpnts_specs_latup_entry.insert(0,20)
                gridpnts_specs_latup_entry.bind("<FocusIn>", lambda args: gridpnts_specs_latup_entry.delete('0', 'end'))
                gridpnts_specs_latup_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(gridpnts_add_by_region_frame, text="Lon lower [deg]").grid(row=4, column=0, sticky='w', padx=10, pady=10)
                gridpnts_specs_lonlow_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                gridpnts_specs_lonlow_entry.insert(0,-110)
                gridpnts_specs_lonlow_entry.bind("<FocusIn>", lambda args: gridpnts_specs_lonlow_entry.delete('0', 'end'))
                gridpnts_specs_lonlow_entry.grid(row=4, column=1, sticky='w')

                ttk.Label(gridpnts_add_by_region_frame, text="Lon upper [deg]").grid(row=5, column=0, sticky='w', padx=10, pady=10)
                gridpnts_specs_lonup_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                gridpnts_specs_lonup_entry.insert(0,-10)
                gridpnts_specs_lonup_entry.bind("<FocusIn>", lambda args: gridpnts_specs_lonup_entry.delete('0', 'end'))
                gridpnts_specs_lonup_entry.grid(row=5, column=1, sticky='w')

                ttk.Label(gridpnts_add_by_region_frame, text="(Optional) Common grid-resolution [deg]", wraplength=150).grid(row=6, column=0, sticky='w', padx=10, pady=10)
                self.gridpnts_specs_gridres_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                self.gridpnts_specs_gridres_entry.grid(row=6, column=1, sticky='w')

                ttk.Label(gridpnts_add_by_region_frame, text="(Optional) Common grid-resolution factor", wraplength=150).grid(row=7, column=0, sticky='w', padx=10, pady=10)
                self.gridpnts_specs_gridresfac_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
                self.gridpnts_specs_gridresfac_entry.grid(row=7, column=1, sticky='w')

                gridpnts_specs_type_rbtn_2 = ttk.Radiobutton(gridpnts_add_by_datafile_frame, text="Data file", command=gridpnts_specs_rbtn_click,
                                    variable=self._gridpnts_specs_type, value="DataFile")
                gridpnts_specs_type_rbtn_2.grid(row=0, column=0, padx=10, pady=5)

                def click_grid_data_file_path_btn():
                    self.grid_data_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the grid-point data file:", filetypes=(("All files","*.*"), ("csv files","*.csv")))  
                    grid_data_fp_entry.configure(state='normal')
                    grid_data_fp_entry.delete(0,'end')
                    grid_data_fp_entry.insert(0,self.grid_data_fp)
                    grid_data_fp_entry.configure(state='disabled')                    

                ttk.Button(gridpnts_add_by_datafile_frame, text="Select Path", command=click_grid_data_file_path_btn, state='disabled').grid(row=0, column=1, sticky='w', padx=10, pady=10)
                grid_data_fp_entry=tk.Entry(gridpnts_add_by_datafile_frame, state='disabled')
                grid_data_fp_entry.grid(row=1,column=0, padx=10, pady=10, columnspan=2, sticky='ew')             
            
            def get_specs(self):            
                # see the state of the radio-button and then return the appropriate data    
                if(self._gridpnts_specs_type.get() == "LatLonBounds"):
                    customGridRes = self.gridpnts_specs_gridres_entry.get()
                    customGridRes = float(customGridRes) if customGridRes != "" else None                    
                    customGridResFactor = self.gridpnts_specs_gridresfac_entry.get()
                    customGridResFactor = float(customGridResFactor) if customGridResFactor != "" else None
                    return {"@type": "autoGrid", "regions":self.region_info, "customGridRes": customGridRes, "customGridResFactor":customGridResFactor}
                elif(self._gridpnts_specs_type.get() == "DataFile"):
                    return {"@type": "customGrid", "covGridFilePath": self.grid_data_fp}     

        class PointingOptionsCoverageCalculator(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)         
                popts_specs_frame = ttk.Frame(self) 
                popts_specs_frame.grid(row=0, column=0, ipadx=5, ipady=5)    

                def click_popts_data_file_path_btn():
                    self.popts_data_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the pointing-options data file:", filetypes=(("All files","*.*"), ("csv files","*.csv")))  
                    popts_data_fp_entry.configure(state='normal')
                    popts_data_fp_entry.delete(0,'end')
                    popts_data_fp_entry.insert(0,self.popts_data_fp)
                    popts_data_fp_entry.configure(state='disabled')

                ttk.Button(popts_specs_frame, text="Select Data File", command=click_popts_data_file_path_btn).grid(row=0, column=0, padx=10, pady=5, columnspan=2)
                popts_data_fp_entry=tk.Entry(popts_specs_frame, state='disabled')
                popts_data_fp_entry.grid(row=1,column=0, padx=10, pady=5, sticky='ew', columnspan=2)

                # display available sensors
                ttk.Label(popts_specs_frame, text="Select the sensors associated with this pointing-data file", wraplength=200).grid(row=2, column=0, columnspan=2, sticky='w',  padx=10, pady=(20, 5))
                sensor_tree_scroll = ttk.Scrollbar(popts_specs_frame)
                sensor_tree_scroll.grid(row=3, column=1, sticky='nsw', pady=10)
                self.sensor_tree = ttk.Treeview(popts_specs_frame, yscrollcommand=sensor_tree_scroll.set)
                self.sensor_tree.grid(row=3, column=0, sticky='e', padx=10, pady=10)
                sensor_tree_scroll.config(command=self.sensor_tree.yview)

                self.sensor_tree['columns'] = ("ID", "Type", "Sats")
                self.sensor_tree.column('#0', width=0, stretch="no")
                self.sensor_tree.column("ID", width = 50)  
                self.sensor_tree.column("Type", width = 50)            
                self.sensor_tree.column("Sats", width = 100)             

                self.sensor_tree.heading("#0", text="", anchor="w")
                self.sensor_tree.heading("ID", text="ID", anchor="w")
                self.sensor_tree.heading("Type", text="Type", anchor="w")
                self.sensor_tree.heading("Sats", text="Satellite(s)", anchor="w")

                sen_specs = config.miss_specs.get_sensor_specs()  # get all available sensors in the configuration                 
                if sen_specs is not False:
                    for k in range(0,len(sen_specs)):
                        self.sensor_tree.insert(parent='', index='end', iid=sen_specs[k][0], text="", values=(sen_specs[k][0], sen_specs[k][1], sen_specs[k][2][1]))

            def get_specs(self):            
                return {"instrumentID": ','.join(map(str, self.sensor_tree.selection())), "referenceFrame": "NadirRefFrame", "pntOptsFilePath":self.popts_data_fp}

        class PointingOptionsWithGridPointsCoverageCalculator(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                popts_with_grid_specs_frame = ttk.Frame(self) 
                popts_with_grid_specs_frame.grid(row=0, column=0, ipadx=5, ipady=5)
                ttk.Label(popts_with_grid_specs_frame, text="Under development").pack()          

        frames = {}
        for F in (GridPointsCoverageCalculator, PointingOptionsCoverageCalculator, PointingOptionsWithGridPointsCoverageCalculator):
            page_name = F.__name__
            frame = F(parent=cov_specs_container, controller=self)
            frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # define the widgets inside the child frames
        
        # coverage types child frame
        COV_CALC_TYPES = [
            ("Grid Points", "GridPointsCoverageCalculator"),
            ("Pointing Options", "PointingOptionsCoverageCalculator"),
            ("Pointing Options With Grid Points", "PointingOptionsWithGridPointsCoverageCalculator")
        ]

        self._cov_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._cov_type.set("GridPointsCoverageCalculator") # initialize

        def cov_type_rbtn_click():
            if self._cov_type.get() == "GridPointsCoverageCalculator":
                frame = frames["GridPointsCoverageCalculator"]
            elif self._cov_type.get() == "PointingOptionsCoverageCalculator":
                frame = frames["PointingOptionsCoverageCalculator"]
            elif self._cov_type.get() == "PointingOptionsWithGridPointsCoverageCalculator":
                frame = frames["PointingOptionsWithGridPointsCoverageCalculator"]
            frame.tkraise()

        for text, mode in COV_CALC_TYPES:
            cov_type_rbtn = ttk.Radiobutton(cov_type_frame, text=text, command=cov_type_rbtn_click,
                            variable=self._cov_type, value=mode)
            cov_type_rbtn.pack(anchor='w', padx=5, pady=5)

        frame = frames[self._cov_type.get()]
        frame.tkraise()    

        # okcancel frame
        def ok_click():               
            if self._cov_type.get() == "GridPointsCoverageCalculator":
                specs = frames[self._cov_type.get()].get_specs()
                config.miss_specs.add_coverage_grid(specs)
                logger.info("Coverage grid added.")
                cov_win.destroy()
            if self._cov_type.get() == "PointingOptionsCoverageCalculator":
                specs = frames[self._cov_type.get()].get_specs()
                config.miss_specs.add_pointing_options(specs) 
                logger.info("Pointings Options added.")
                cov_win.destroy()
            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=cov_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)  