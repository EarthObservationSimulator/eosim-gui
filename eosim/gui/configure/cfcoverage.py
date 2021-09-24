from tkinter import ttk 
import tkinter as tk
from eosim import config
import random
import tkinter.filedialog, tkinter.messagebox
import os
import eosim.gui.helpwindow as helpwindow
from collections import namedtuple
import logging

logger = logging.getLogger(__name__)

class GridInfoFrame(ttk.Frame):
    """ Class to handle the Grid-info frame, which is used by the GridPointsCoverageCalculatorFrame and PointingOptionsWithGridPointsCoverageCalculatorFrame."""
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        gridpnts_specs_frame = ttk.Frame(self) 
        gridpnts_specs_frame.grid(row=0, column=0, ipadx=5, ipady=5)
        
        gridpnts_add_by_region_frame = ttk.Frame(gridpnts_specs_frame)
        gridpnts_add_by_region_frame.grid(row=0, column=0)

        gridpnts_add_by_datafile_frame = ttk.Frame(gridpnts_specs_frame)
        gridpnts_add_by_datafile_frame.grid(row=1, column=0)

        # define the widgets inside the child frames

        # function to handle the radio-button clicks (to enable/ disable the auto-grid/ custom-grid frame selection)
        self._gridpnts_specs_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._gridpnts_specs_type.set("AutoGrid") # initialize
        def gridpnts_specs_rbtn_click():
            if self._gridpnts_specs_type.get() == "AutoGrid":
                # disable the frame containing the other option, except for the radio-button
                for child in gridpnts_add_by_datafile_frame.winfo_children():
                    child.configure(state='disable')
                gridpnts_specs_type_rbtn_2.configure(state='normal')
                # enable the frame containing the current option
                for child in gridpnts_add_by_region_frame.winfo_children():
                    child.configure(state='normal')
                
            elif self._gridpnts_specs_type.get() == "CustomGrid":
                # disable the frame containing the other option, except for the radio-button
                for child in gridpnts_add_by_region_frame.winfo_children():
                    child.configure(state='disable')   
                gridpnts_specs_type_rbtn_1.configure(state='normal')
                # enable the frame containing the current option
                for child in gridpnts_add_by_datafile_frame.winfo_children():
                    child.configure(state='normal')             

        # define the widgets in the gridpnts_add_by_region_frame
        gridpnts_specs_type_rbtn_1 = ttk.Radiobutton(gridpnts_add_by_region_frame, text="Auto Grid", command=gridpnts_specs_rbtn_click,
                                                        variable=self._gridpnts_specs_type, value="AutoGrid")
        gridpnts_specs_type_rbtn_1.grid(row=0, column=0, padx=10, pady=10)

        self.region_info = []
        def add_region():
            customGridRes = self.gridpnts_specs_gridres_entry.get()
            customGridRes = float(customGridRes) if customGridRes != "" else None
            self.region_info.append({'@type': 'autoGrid',
                                        '@id': float(gridpnts_specs_regid_entry.get()),                                              
                                        'latLower': float(gridpnts_specs_latlow_entry.get()), 
                                        'latUpper': float(gridpnts_specs_latup_entry.get()),                                              
                                        'lonLower': float(gridpnts_specs_lonlow_entry.get()),
                                        'lonUpper': float(gridpnts_specs_lonup_entry.get()),
                                        'gridRes': customGridRes})
            logger.warn("Region is only queued to be added. It shall be added when the 'OK' button is clicked.")
            if customGridRes is None:
                logger.warn("Grid resolution has not been specified. An appropriate grid-res according to the current list of satellites has been calculated and utilized. If no satellites, the assumed grid-res is 1 deg.")

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

        ttk.Label(gridpnts_add_by_region_frame, text="(Optional) Grid-resolution [deg]", wraplength=150).grid(row=6, column=0, sticky='w', padx=10, pady=10)
        self.gridpnts_specs_gridres_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
        self.gridpnts_specs_gridres_entry.grid(row=6, column=1, sticky='w')

        ttk.Label(gridpnts_add_by_region_frame, text="(Optional) Common grid-resolution factor", wraplength=150).grid(row=7, column=0, sticky='w', padx=10, pady=10)
        self.gridpnts_specs_gridresfac_entry = ttk.Entry(gridpnts_add_by_region_frame, width=10)
        self.gridpnts_specs_gridresfac_entry.grid(row=7, column=1, sticky='w')

        # define the widgets in the gridpnts_add_by_datafile_frame
        gridpnts_specs_type_rbtn_2 = ttk.Radiobutton(gridpnts_add_by_datafile_frame, text="Custom Grid", command=gridpnts_specs_rbtn_click,
                            variable=self._gridpnts_specs_type, value="CustomGrid")
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
        if(self._gridpnts_specs_type.get() == "AutoGrid"):                                        
            customGridResFactor = self.gridpnts_specs_gridresfac_entry.get()
            customGridResFactor = float(customGridResFactor) if customGridResFactor != "" else None
            return ("autoGrid", self.region_info, customGridResFactor)
        elif(self._gridpnts_specs_type.get() == "CustomGrid"):
            specs = {"grid": {"@type": "customGrid", "covGridFilePath": self.grid_data_fp}}
            return ("customGrid", specs)

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

        class GridPointsCoverageCalculatorFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)
                grid_point_cc_frame = ttk.Frame(self) 
                grid_point_cc_frame.grid(row=0, column=0, ipadx=5, ipady=5)

                # define the child frames
                grid_point_cc_info_frame = ttk.Frame(grid_point_cc_frame)
                grid_point_cc_info_frame.grid(row=0, column=0)

                ttk.Label(grid_point_cc_info_frame, text="In this coverage calculation, the access to a grid-point within the sensor FOV is evaluated. The grid-points are either auto-generated within the region-bounds (or) supplied by the user in a data-file.", wraplength=350).pack()  
                            
                self.grid_info_frame = GridInfoFrame(parent=grid_point_cc_frame, controller=self)
                self.grid_info_frame.grid(row=1, column=0, sticky="nsew")
                
            def get_specs(self):            
                # see the state of the radio-button and then return the appropriate data  
                grid_info_specs =   self.grid_info_frame.get_specs()
                grid_type = grid_info_specs[0]
                
                if(grid_type == "autoGrid"):  
                    grid_info =  grid_info_specs[1]
                    customGridResFactor =  grid_info_specs[2]                 
                    coverage_settings = {"coverageType": "GRID COVERAGE", "gridResFactor":customGridResFactor}
                    return (coverage_settings, grid_info)
                elif(grid_type == "customGrid"):
                    coverage_settings = {"coverageType": "GRID COVERAGE"}
                    grid_info =  grid_info_specs[1]
                    return (coverage_settings, grid_info)    
        class PointingOptionsCoverageCalculatorFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)         
                popts_specs_frame = ttk.Frame(self) 
                popts_specs_frame.grid(row=0, column=0, ipadx=5, ipady=5)  

                ttk.Label(popts_specs_frame, text="In this coverage calculation, the ground-position corresponding to the intersection of the pointing-axis (depending on the pointing-option) with the Earth surface. Pointing-options (orientations of the sensor in the nadir-pointing frame) are configured in the *sensor* panel.", wraplength=350).pack()  

            def get_specs(self):            
                return {"coverageType": "POINTING OPTIONS COVERAGE"}
        class PointingOptionsWithGridPointsCoverageCalculatorFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                popts_with_grid_cc_frame = ttk.Frame(self) 
                popts_with_grid_cc_frame.grid(row=0, column=0, ipadx=5, ipady=5)              

                # define the child frames
                popts_with_grid_cc_info_frame = ttk.Frame(popts_with_grid_cc_frame)
                popts_with_grid_cc_info_frame.grid(row=0, column=0)
                
                ttk.Label(popts_with_grid_cc_info_frame, text="This type of coverage calculation is similar to the *Grid Points* coverage calculation, except that it is carried out for each pointing-option. Pointing-options (orientations of the sensor in the nadir-pointing frame) are configured in the *sensor* panel.", wraplength=350).pack()  
                            
                self.grid_info_frame = GridInfoFrame(parent=popts_with_grid_cc_frame, controller=self)
                self.grid_info_frame.grid(row=1, column=0, sticky="nsew")
                
            def get_specs(self):            
                # see the state of the radio-button and then return the appropriate data  
                grid_info_specs =   self.grid_info_frame.get_specs()
                grid_type = grid_info_specs[0]
                
                if(grid_type == "autoGrid"):  
                    region_info =  grid_info_specs[1]
                    customGridResFactor =  grid_info_specs[2]                 
                    coverage_settings = {"coverageType": "POINTING OPTIONS WITH GRID COVERAGE", "gridResFactor":customGridResFactor}
                    return (coverage_settings, region_info)
                elif(grid_type == "customGrid"):
                    coverage_settings = {"coverageType": "POINTING OPTIONS WITH GRID COVERAGE"}
                    grid_info =  grid_info_specs[1]
                    return (coverage_settings, grid_info)   

        # define the widgets in the cov_type_frame
        # coverage types child frame
        COV_CALC_TYPES = [
            ("Grid Points", "GridPointsCoverageCalculatorFrame"),
            ("Pointing Options", "PointingOptionsCoverageCalculatorFrame"),
            ("Pointing Options With Grid Points", "PointingOptionsWithGridPointsCoverageCalculatorFrame")
        ]

        self._cov_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._cov_type.set("GridPointsCoverageCalculatorFrame") # initialize
        
        def cov_type_rbtn_click():
            if self._cov_type.get() == "GridPointsCoverageCalculatorFrame":
                frame = frames["GridPointsCoverageCalculatorFrame"]
            elif self._cov_type.get() == "PointingOptionsCoverageCalculatorFrame":
                frame = frames["PointingOptionsCoverageCalculatorFrame"]
            elif self._cov_type.get() == "PointingOptionsWithGridPointsCoverageCalculatorFrame":
                frame = frames["PointingOptionsWithGridPointsCoverageCalculatorFrame"]
            frame.tkraise()

        for text, mode in COV_CALC_TYPES:
            cov_type_rbtn = ttk.Radiobutton(cov_type_frame, text=text, command=cov_type_rbtn_click,
                            variable=self._cov_type, value=mode)
            cov_type_rbtn.pack(anchor='w', padx=5, pady=5)

        # define the widgets in the cov_specs_container
        frames = {}
        for F in (GridPointsCoverageCalculatorFrame, PointingOptionsCoverageCalculatorFrame, PointingOptionsWithGridPointsCoverageCalculatorFrame):
            page_name = F.__name__
            frame = F(parent=cov_specs_container, controller=self)
            frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = frames[self._cov_type.get()]
        frame.tkraise()    

        # define the widgets in the okcancel frame
        def ok_click():               
            if self._cov_type.get() == "GridPointsCoverageCalculatorFrame":
                specs = frames[self._cov_type.get()].get_specs()              
                config.mission_specs.update_coverage_settings_from_dict(specs[0]) # SETTINGS MUST BE UPDATED PRIOR TO ADDITION OF GRID!
                config.mission_specs.add_coverage_grid_from_dict(specs[1])
                logger.info("Coverage grid coverage calculation chosen with the input grid.")
                cov_win.destroy()
            if self._cov_type.get() == "PointingOptionsCoverageCalculatorFrame":
                specs = frames[self._cov_type.get()].get_specs()
                logger.info("Pointing options coverage calculation chosen.")
                config.mission_specs.update_coverage_settings_from_dict(specs[0])
                cov_win.destroy()  
            if self._cov_type.get() == "PointingOptionsWithGridPointsCoverageCalculatorFrame":
                specs = frames[self._cov_type.get()].get_specs()
                config.mission_specs.update_coverage_settings_from_dict(specs[0]) # SETTINGS MUST BE UPDATED PRIOR TO ADDITION OF GRID!
                config.mission_specs.add_coverage_grid_from_dict(specs[1])
                logger.info("Pointing options with grid coverage calculation chosen with the input grid.")
                cov_win.destroy()               
            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=cov_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)  