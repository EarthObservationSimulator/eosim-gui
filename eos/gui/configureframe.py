from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
from orbitpy.preprocess import OrbitParameters, PreProcess
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.public_library import Instrument
import os
import eos.gui.helpwindow as helpwindow
import pickle
from orbitpy import preprocess
import logging

logger = logging.getLogger(__name__)

miss_specs = MissionConfig()     
class ConfigureFrame(ttk.Frame):

    BTNWIDTH = 15

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=4)
        self.rowconfigure(1,weight=4)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

        # "Define Mission Frame" 
        miss_frame = ttk.LabelFrame(self, text="Define Mission", labelanchor='n') 
        miss_frame.grid(row=0, column=0, ipadx=20, ipady=20)
        miss_btn = ttk.Button(miss_frame, text="Mission", command=self.click_mission_btn)
        miss_btn.pack(expand=True)

        # "Add Resource" frame
        resource_frame = ttk.LabelFrame(self, text="Add Resource", labelanchor='n') 
        resource_frame.grid(row=0, column=1, ipadx=20, ipady=20)
        resource_frame.rowconfigure(0,weight=1)
        resource_frame.rowconfigure(1,weight=1)
        resource_frame.columnconfigure(0,weight=1)
        resource_frame.columnconfigure(1,weight=1)
        sat_btn = ttk.Button(resource_frame, text="Satellite", command=self.click_satellite_btn, width=ConfigureFrame.BTNWIDTH)
        sat_btn.grid(row=0, column=0)
        con_btn = ttk.Button(resource_frame, text="Constellation", command=self.click_constellation_btn, width=ConfigureFrame.BTNWIDTH)
        con_btn.grid(row=0, column=1)
        sen_btn = ttk.Button(resource_frame, text="Sensor", command=self.click_sensor_btn, width=ConfigureFrame.BTNWIDTH)
        sen_btn.grid(row=1, column=0)
        gndstn_btn = ttk.Button(resource_frame, text="Ground Station", command=self.click_gs_btn, width=ConfigureFrame.BTNWIDTH)
        gndstn_btn.grid(row=1, column=1)

        #
        visual_frame = ttk.LabelFrame(self, text="Visualize", labelanchor='n') 
        visual_frame.grid(row=1, column=0, ipadx=20, ipady=20)
        visual_frame.rowconfigure(0,weight=1)
        visual_frame.columnconfigure(0,weight=1)
        vis_arch_btn = ttk.Button(visual_frame, text="Visualize Arch", command=self.click_visualize_btn, width=ConfigureFrame.BTNWIDTH)
        vis_arch_btn.grid(row=0, column=0)

        # "Settings" frame
        settings_frame = ttk.LabelFrame(self, text="Settings", labelanchor='n') 
        settings_frame.grid(row=1, column=1, ipadx=20, ipady=20)
        settings_frame.rowconfigure(0,weight=1)
        settings_frame.rowconfigure(1,weight=1)
        settings_frame.columnconfigure(0,weight=1)
        settings_frame.columnconfigure(1,weight=1)
        prp_set_btn = ttk.Button(settings_frame, text="Propagate", command=self.click_propagate_settings_btn, width=ConfigureFrame.BTNWIDTH)
        prp_set_btn.grid(row=0, column=0)
        com_set_btn = ttk.Button(settings_frame, text="Comm", width=ConfigureFrame.BTNWIDTH)
        com_set_btn.grid(row=0, column=1)
        cov_set_btn = ttk.Button(settings_frame, text="Coverage", command=self.click_coverage_settings_btn, width=ConfigureFrame.BTNWIDTH)
        cov_set_btn.grid(row=1, column=0)
        obs_syn_btn = ttk.Button(settings_frame, text="TBD", width=ConfigureFrame.BTNWIDTH)
        obs_syn_btn.grid(row=1, column=1)

        #
        clr_sv_run_frame = ttk.Frame(self) 
        clr_sv_run_frame.grid(row=2, column=0, columnspan=2, ipadx=10, sticky = 'nsew')
        clr_sv_run_frame.columnconfigure(0,weight=1)
        clr_sv_run_frame.columnconfigure(1,weight=1)
        clr_sv_run_frame.columnconfigure(2,weight=1)
        clear_conf_btn = ttk.Button(clr_sv_run_frame, text="Clear Config", command=self.click_clear_config, width=ConfigureFrame.BTNWIDTH)
        clear_conf_btn.grid(row=0, column=0, ipadx=20, sticky='s')
        save_conf_btn = ttk.Button(clr_sv_run_frame, text="Save Config", command=self.click_save_config, width=ConfigureFrame.BTNWIDTH)
        save_conf_btn.grid(row=0, column=1, ipadx=20, sticky='s')
        run_all_btn = ttk.Button(clr_sv_run_frame, text="Run All", width=ConfigureFrame.BTNWIDTH)
        run_all_btn.grid(row=0, column=2,ipadx=20, sticky='s')

    def click_save_config(self):

        logger.info(".......Preprocessing configuration .......")
        user_dir = os.getcwd() + '/'
        pi = preprocess.PreProcess(miss_specs.to_dict(), user_dir) # generates grid if-needed, calculates propagation 
                                                         # and coverage parameters, enumerates orbits, etc.
        prop_cov_param = pi.generate_prop_cov_param() 
        pickle.dump(prop_cov_param, open("prop_cov_param.p", "wb"))

        with open('MissionSpecs.json', 'w', encoding='utf-8') as f:
            json.dump(miss_specs.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info("Configuration Saved.")
    
    def click_clear_config(self):
        ''' Clear the configuration (both in the local variable and in the MissionSpecs file) '''
        miss_specs.clear()
        with open('MissionSpecs.json', 'w', encoding='utf-8') as f:
            json.dump(miss_specs.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info("Configuration cleared.")

    def click_mission_btn(self):      

        # create and configure child window, parent frame
        miss_win = tk.Toplevel()

        miss_win.rowconfigure(0,weight=1)
        miss_win.rowconfigure(1,weight=1)
        miss_win.rowconfigure(2,weight=1)
        miss_win.columnconfigure(0,weight=1)

        miss_win_frame =ttk.LabelFrame(miss_win, text="Mission Parameters")
        miss_win_frame.grid(row=0, column=0, padx=10, pady=10)

        # define all child frames 
        epoch_frame = ttk.Frame(miss_win_frame)
        epoch_frame.grid(row=0, column=0)
        epoch_frame.columnconfigure(0,weight=1)
        epoch_frame.columnconfigure(1,weight=1)

        epoch_entry_frame = ttk.Frame(epoch_frame)
        epoch_entry_frame.grid(row=0, column=1, sticky='w')
        epoch_entry_frame.rowconfigure(0,weight=1)
        epoch_entry_frame.rowconfigure(1,weight=1)
        epoch_entry_frame.rowconfigure(2,weight=1)
        epoch_entry_frame.rowconfigure(3,weight=1)
        epoch_entry_frame.rowconfigure(4,weight=1)
        epoch_entry_frame.rowconfigure(5,weight=1)

        duration_frame = ttk.Frame(miss_win_frame)
        duration_frame.grid(row=1, column=0)
        
        okcancel_frame = ttk.Frame(miss_win_frame)
        okcancel_frame.grid(row=2, column=0)        

        # define the widgets inside all the child frames        
        ttk.Label(epoch_frame, text="Mission Epoch [UTC Greogorian]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')

        epoch_year_entry = ttk.Entry(epoch_entry_frame, width=6)
        epoch_year_entry.grid(row=0, column=0, padx=2, pady=2)
        epoch_year_entry.insert(0,2020)
        epoch_year_entry.bind("<FocusIn>", lambda args: epoch_year_entry.delete('0', 'end'))
        ttk.Label(epoch_entry_frame, text="Year").grid(row=0, column=1, sticky='w')

        epoch_month_entry = ttk.Entry(epoch_entry_frame, width=6)
        epoch_month_entry.grid(row=1, column=0, padx=2, pady=2)
        epoch_month_entry.insert(0,1)
        epoch_month_entry.bind("<FocusIn>", lambda args: epoch_month_entry.delete('0', 'end'))
        ttk.Label(epoch_entry_frame, text="Month").grid(row=1, column=1, sticky='w')

        epoch_day_entry = ttk.Entry(epoch_entry_frame, width=6)
        epoch_day_entry.grid(row=2, column=0, padx=2, pady=2)
        epoch_day_entry.insert(0,1)
        epoch_day_entry.bind("<FocusIn>", lambda args: epoch_day_entry.delete('0', 'end'))
        ttk.Label(epoch_entry_frame, text="Day").grid(row=2, column=1, sticky='w')

        epoch_hour_entry = ttk.Entry(epoch_entry_frame, width=6)
        epoch_hour_entry.grid(row=3, column=0, padx=2, pady=2)
        epoch_hour_entry.insert(0,12)
        epoch_hour_entry.bind("<FocusIn>", lambda args: epoch_hour_entry.delete('0', 'end'))
        ttk.Label(epoch_entry_frame, text="Hour").grid(row=3, column=1, sticky='w')

        epoch_min_entry = ttk.Entry(epoch_entry_frame, width=6)
        epoch_min_entry.grid(row=4, column=0, padx=2, pady=2)
        epoch_min_entry.insert(0,0)
        epoch_min_entry.bind("<FocusIn>", lambda args: epoch_min_entry.delete('0', 'end'))
        ttk.Label(epoch_entry_frame, text="Minute").grid(row=4, column=1, sticky='w')

        epoch_sec_entry = ttk.Entry(epoch_entry_frame, width=6)
        epoch_sec_entry.grid(row=5, column=0, padx=2, pady=2)
        epoch_sec_entry.insert(0,0)
        epoch_sec_entry.bind("<FocusIn>", lambda args: epoch_sec_entry.delete('0', 'end'))
        ttk.Label(epoch_entry_frame, text="Second").grid(row=5, column=1, sticky='w')

        # duration frame
        ttk.Label(duration_frame, text="Mission Duration [Days]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        duration_entry = ttk.Entry(duration_frame, width=6)
        duration_entry.insert(0,2.5)
        duration_entry.bind("<FocusIn>", lambda args: duration_entry.delete('0', 'end'))
        duration_entry.grid(row=0, column=1, sticky='w')

        # okcancel frame
        def ok_click():
            miss_specs.update_epoch(str(epoch_year_entry.get()) + ',' + str(epoch_month_entry.get()) + ',' + str(epoch_day_entry.get()) + ',' + str(epoch_hour_entry.get()) + ',' + str(epoch_min_entry.get()) + ',' + str(epoch_sec_entry.get()))
            miss_specs.update_duration(duration_entry.get())
            miss_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="OK", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Cancel", command=miss_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)

    def click_satellite_btn(self):      

        # create and configure child window, parent frame
        sat_win = tk.Toplevel()

        sat_win.rowconfigure(0,weight=1)
        sat_win.rowconfigure(1,weight=1)
        sat_win.columnconfigure(0,weight=1)

        sat_win_frame =ttk.LabelFrame(sat_win, text="Add Satellite")
        sat_win_frame.grid(row=0, column=0, padx=10, pady=10)

        # define all child frames
        sat_kep_specs_frame = ttk.Frame(sat_win_frame)
        sat_kep_specs_frame.grid(row=0, column=0)
        sat_kep_specs_frame.columnconfigure(0,weight=1)
        sat_kep_specs_frame.columnconfigure(1,weight=1)
        sat_kep_specs_frame.rowconfigure(0,weight=1)
        sat_kep_specs_frame.rowconfigure(1,weight=1)
        sat_kep_specs_frame.rowconfigure(2,weight=1)
        sat_kep_specs_frame.rowconfigure(3,weight=1)
        sat_kep_specs_frame.rowconfigure(4,weight=1)
        sat_kep_specs_frame.rowconfigure(5,weight=1) 
        sat_kep_specs_frame.rowconfigure(6,weight=1)

        okcancel_frame = ttk.Frame(sat_win_frame)
        okcancel_frame.grid(row=1, column=0)  

        # define the widgets inside the child frames
        ttk.Label(sat_kep_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        uid_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        uid_entry.insert(0,random.randint(0,1000))
        uid_entry.bind("<FocusIn>", lambda args: uid_entry.delete('0', 'end'))
        uid_entry.grid(row=0, column=1, sticky='w')

        ttk.Label(sat_kep_specs_frame, text="Altitude [km]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        sma_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        sma_entry.insert(0,500)
        sma_entry.bind("<FocusIn>", lambda args: sma_entry.delete('0', 'end'))
        sma_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(sat_kep_specs_frame, text="Eccentricity", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        ecc_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        ecc_entry.insert(0,0.001)
        ecc_entry.bind("<FocusIn>", lambda args: ecc_entry.delete('0', 'end'))
        ecc_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(sat_kep_specs_frame, text="Inclination [deg]", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        inc_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        inc_entry.insert(0,45)
        inc_entry.bind("<FocusIn>", lambda args: inc_entry.delete('0', 'end'))
        inc_entry.grid(row=3, column=1, sticky='w')
        
        ttk.Label(sat_kep_specs_frame, text="RAAN [deg]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        raan_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        raan_entry.insert(0,270)
        raan_entry.bind("<FocusIn>", lambda args: raan_entry.delete('0', 'end'))
        raan_entry.grid(row=4, column=1, sticky='w')

        tk.Label(sat_kep_specs_frame, text="AOP[deg]", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        aop_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        aop_entry.insert(0,270)
        aop_entry.bind("<FocusIn>", lambda args: aop_entry.delete('0', 'end'))
        aop_entry.grid(row=5, column=1, sticky='w')

        tk.Label(sat_kep_specs_frame, text="TA [deg]", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
        ta_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        ta_entry.insert(0,10)
        ta_entry.bind("<FocusIn>", lambda args: ta_entry.delete('0', 'end'))
        ta_entry.grid(row=6, column=1, sticky='w')

        # okcancel frame
        def ok_click():            
            satellite = OrbitParameters(_id=uid_entry.get(), sma=float(sma_entry.get())+orbitpy.util.Constants.radiusOfEarthInKM, ecc=ecc_entry.get(), 
                            inc=inc_entry.get(), raan=raan_entry.get(), aop=aop_entry.get(), ta=ta_entry.get())
            miss_specs.add_satellite(satellite)
            

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=sat_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)

    def click_constellation_btn(self):      

        # create and configure child window, parent frame
        constl_win = tk.Toplevel()
        constl_win.rowconfigure(0,weight=1)
        constl_win.columnconfigure(0,weight=1)

        constl_win_frame =ttk.Frame(constl_win)
        constl_win_frame.grid(row=0, column=0, padx=10, pady=10)
        constl_win_frame.rowconfigure(0,weight=1) # constellation type
        constl_win_frame.rowconfigure(1,weight=1) # constellation specs
        constl_win_frame.rowconfigure(2,weight=1) # okcancel
        constl_win_frame.columnconfigure(0,weight=1)

        # define all child frames
        constl_type_frame = ttk.LabelFrame(constl_win_frame, text="Constellation type")
        constl_type_frame.grid(row=0, column=0, sticky='nswe', padx=20, pady=20)
        constl_type_frame.columnconfigure(0,weight=1)
        constl_type_frame.rowconfigure(0,weight=1)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        # grid configure
        constl_specs_container = ttk.LabelFrame(constl_win_frame, text="Specifications", width=250, height=370)
        constl_specs_container.grid_propagate(0)
        constl_specs_container.grid(row=1, column=0, sticky='nswe', padx=20, pady=20)
        constl_specs_container.columnconfigure(0,weight=1)
        constl_specs_container.rowconfigure(0,weight=1)

        # okcancel frame
        okcancel_frame = ttk.Label(constl_win_frame)
        okcancel_frame.grid(row=2, column=0, sticky='nswe', padx=20, pady=20)
        okcancel_frame.columnconfigure(0,weight=1)
        okcancel_frame.rowconfigure(0,weight=1)

        class HomogenousWalkerFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)
                hwd_specs_frame = ttk.Frame(self) 
                hwd_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)

                # define the widgets inside the child frames
                ttk.Label(hwd_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                self.uid_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.uid_entry.insert(0,"G_"+str(random.randint(0,1000))+"_")
                self.uid_entry.bind("<FocusIn>", lambda args: self.uid_entry.delete('0', 'end'))
                self.uid_entry.grid(row=0, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="# Satellites", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                self.nsats_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.nsats_entry.insert(0,6)
                self.nsats_entry.bind("<FocusIn>", lambda args: self.nsats_entry.delete('0', 'end'))
                self.nsats_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="# Orbital planes", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
                self.nplanes_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.nplanes_entry.insert(0,3)
                self.nplanes_entry.bind("<FocusIn>", lambda args: self.nplanes_entry.delete('0', 'end'))
                self.nplanes_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="Relative spacing", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
                self.rspc_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.rspc_entry.insert(0,1)
                self.rspc_entry.bind("<FocusIn>", lambda args: self.rspc_entry.delete('0', 'end'))
                self.rspc_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="Inclination [deg]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
                self.inc_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.inc_entry.insert(0,67)
                self.inc_entry.bind("<FocusIn>", lambda args: self.inc_entry.delete('0', 'end'))
                self.inc_entry.grid(row=4, column=1, sticky='w')
                
                ttk.Label(hwd_specs_frame, text="Altitude [km]", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
                self.alt_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.alt_entry.insert(0,350)
                self.alt_entry.bind("<FocusIn>", lambda args: self.alt_entry.delete('0', 'end'))
                self.alt_entry.grid(row=5, column=1, sticky='w')

                tk.Label(hwd_specs_frame, text="Eccentricity", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
                self.ecc_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.ecc_entry.insert(0,0)
                self.ecc_entry.bind("<FocusIn>", lambda args: self.ecc_entry.delete('0', 'end'))
                self.ecc_entry.grid(row=6, column=1, sticky='w')

                tk.Label(hwd_specs_frame, text="AOP [deg]", wraplength=150).grid(row=7, column=0, padx=10, pady=10, sticky='w')
                self.aop_entry = ttk.Entry(hwd_specs_frame, width=10)
                self.aop_entry.insert(0,250)
                self.aop_entry.bind("<FocusIn>", lambda args: self.aop_entry.delete('0', 'end'))
                self.aop_entry.grid(row=7, column=1, sticky='w')
            
            def get_specs(self):
                return [self.uid_entry.get(), self.nsats_entry.get(), self.nplanes_entry.get(), self.rspc_entry.get(), self.alt_entry.get(), 
                        self.ecc_entry.get(), self.inc_entry.get(), self.aop_entry.get()]               

        class HeterogenousWalkerFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)         
                hetw_specs_frame = ttk.Frame(self) 
                hetw_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)    
                ttk.Label(hetw_specs_frame, text="Under development").pack()    
        
        class TrainConstlFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                trainc_specs_frame = ttk.Frame(self) 
                trainc_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)
                ttk.Label(trainc_specs_frame, text="Under development").pack()          

        frames = {}
        for F in (HomogenousWalkerFrame, HeterogenousWalkerFrame, TrainConstlFrame):
            page_name = F.__name__
            frame = F(parent=constl_specs_container, controller=self)
            frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # define the widgets inside the child frames
        
        # constellation types child frame
        MODES = [
            ("Homogenous Walker Delta", "HomogenousWalkerFrame"),
            ("Heterogenous Walker", "HeterogenousWalkerFrame"),
            ("Train", "TrainConstlFrame")
        ]

        self._constl_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._constl_type.set("HomogenousWalkerFrame") # initialize

        def constl_type_rbtn_click():
            if self._constl_type.get() == "HomogenousWalkerFrame":
                frame = frames["HomogenousWalkerFrame"]
            elif self._constl_type.get() == "HeterogenousWalkerFrame":
                frame = frames["HeterogenousWalkerFrame"]
            elif self._constl_type.get() == "TrainConstlFrame":
                frame = frames["TrainConstlFrame"]

            frame.tkraise()

        for text, mode in MODES:
            constl_type_rbtn = ttk.Radiobutton(constl_type_frame, text=text, command=constl_type_rbtn_click,
                            variable=self._constl_type, value=mode)
            constl_type_rbtn.pack(anchor='w', padx=20, pady=20)

        frame = frames[self._constl_type.get()]
        frame.tkraise()    

        # okcancel frame
        def ok_click():               
            if self._constl_type.get() == "HomogenousWalkerFrame":
                specs = frames[self._constl_type.get()].get_specs()
                data = {}
                data['@id'] = specs[0]
                data['numberSatellites'] = specs[1]
                data['numberPlanes'] = specs[2]
                data['relativeSpacing'] = specs[3]
                data['alt'] = specs[4]
                data['ecc'] = specs[5]
                data['inc'] = specs[6]
                data['aop'] = specs[7]                

                sats = PreProcess.walker_orbits(data)                        
                miss_specs.add_satellite(sats)
            
        ok_btn = ttk.Button(okcancel_frame, text="Add", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=constl_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)  

    def click_sensor_btn(self):      
        
        def basic_sensor_input_config(win, tab):
            # parent frame
            specs_frame = ttk.Frame(tab)
            specs_frame.grid(row=0, column=0, padx=10, pady=10)
            specs_frame.rowconfigure(0,weight=1)
            specs_frame.rowconfigure(1,weight=1)
            specs_frame.columnconfigure(0,weight=1)
            specs_frame.columnconfigure(1,weight=1)
            specs_frame.columnconfigure(2,weight=1)
            specs_frame.columnconfigure(3,weight=1)

            # define all child frames

            # other specs frame
            other_specs_frame = ttk.LabelFrame(specs_frame) # specifications other then FOV, maneuver, orientation frame
            other_specs_frame.grid(row=0, column=0, padx=10, pady=10)
            other_specs_frame.bind('<Enter>',lambda event, widget_id="basicsensor": helpwindow.update_help_window(event, widget_id))
            
            # fov specs frame
            fov_specs_frame = ttk.LabelFrame(specs_frame, text="Field-Of-View") # field-of-view (FOV) specifications frame            
            fov_specs_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n') 
            fov_specs_frame.bind('<Enter>',lambda event, widget_id="basicsensor_fovspecs": helpwindow.update_help_window(event, widget_id)) 

            fov_type_frame = ttk.Frame(fov_specs_frame)
            fov_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
            fov_type_frame.columnconfigure(0,weight=1)
            fov_type_frame.rowconfigure(0,weight=1)

            fov_specs_container = ttk.Frame(fov_specs_frame)
            fov_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
            fov_specs_container.columnconfigure(0,weight=1)
            fov_specs_container.rowconfigure(0,weight=1)

            # orientation frame
            orien_frame = ttk.LabelFrame(specs_frame, text="Orientation") # sensor orientation frame
            orien_frame.grid(row=0, column=2, padx=10, pady=10, sticky='n')

            orien_type_frame = ttk.Frame(orien_frame)
            orien_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
            orien_type_frame.columnconfigure(0,weight=1)
            orien_type_frame.rowconfigure(0,weight=1)

            orien_specs_container = ttk.Frame(orien_frame)
            orien_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
            orien_specs_container.columnconfigure(0,weight=1)
            orien_specs_container.rowconfigure(0,weight=1)

            # manuver frame
            maneuver_frame = ttk.LabelFrame(specs_frame, text="Manuever") # manuver specs frame
            maneuver_frame.grid(row=0, column=3, padx=10, pady=10, sticky='n')
            maneuver_frame.bind('<Enter>',lambda event, widget_id="maneuver": helpwindow.update_help_window(event, widget_id))

            maneuver_type_frame = ttk.Frame(maneuver_frame)
            maneuver_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
            maneuver_type_frame.columnconfigure(0,weight=1)
            maneuver_type_frame.rowconfigure(0,weight=1)

            maneuver_specs_container = ttk.Frame(maneuver_frame)
            maneuver_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
            maneuver_specs_container.columnconfigure(0,weight=1)
            maneuver_specs_container.rowconfigure(0,weight=1)
            

            # ok cancel frame
            okcancel_frame = ttk.Frame(specs_frame)
            okcancel_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10) 

            # define the widgets in other_specs_frame
            ttk.Label(other_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
            uid_entry = ttk.Entry(other_specs_frame, width=10)
            uid_entry.insert(0,'sen'+str(random.randint(0,100)))
            uid_entry.bind("<FocusIn>", lambda args: uid_entry.delete('0', 'end'))
            uid_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

            ttk.Label(other_specs_frame, text="Name", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
            name_entry = ttk.Entry(other_specs_frame, width=10)
            name_entry.insert(0,"Atom")
            name_entry.bind("<FocusIn>", lambda args: name_entry.delete('0', 'end'))
            name_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

            ttk.Label(other_specs_frame, text="Mass [kg]", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
            mass_entry = ttk.Entry(other_specs_frame, width=10)
            mass_entry.insert(0,28)
            mass_entry.bind("<FocusIn>", lambda args: mass_entry.delete('0', 'end'))
            mass_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)

            ttk.Label(other_specs_frame, text="Volume [m3]", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
            vol_entry = ttk.Entry(other_specs_frame, width=10)
            vol_entry.insert(0,0.12)
            vol_entry.bind("<FocusIn>", lambda args: vol_entry.delete('0', 'end'))
            vol_entry.grid(row=3, column=1, sticky='w', padx=10, pady=10)

            ttk.Label(other_specs_frame, text="Power [W]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
            pow_entry = ttk.Entry(other_specs_frame, width=10)
            pow_entry.insert(0,32)
            pow_entry.bind("<FocusIn>", lambda args: pow_entry.delete('0', 'end'))
            pow_entry.grid(row=4, column=1, sticky='w', padx=10, pady=10)

            ttk.Label(other_specs_frame, text="Bits per pixel", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
            bpp_entry = ttk.Entry(other_specs_frame, width=10)
            bpp_entry.insert(0,8)
            bpp_entry.bind("<FocusIn>", lambda args: bpp_entry.delete('0', 'end'))
            bpp_entry.grid(row=5, column=1, sticky='w', padx=10, pady=10)

            ttk.Label(other_specs_frame, text="Data Rate [Megabits-per-sec]", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
            dr_entry = ttk.Entry(other_specs_frame, width=10)
            dr_entry.insert(0,250)
            dr_entry.bind("<FocusIn>", lambda args: dr_entry.delete('0', 'end'))
            dr_entry.grid(row=6, column=1, sticky='w', padx=10, pady=10)

            # define the widgets in fov_specs_frame
            class ConicalFOV(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    confov_specs_frame = ttk.Frame(self) 
                    confov_specs_frame.grid(row=0, column=0)

                    # define the widgets 
                    ttk.Label(confov_specs_frame, text="Full Cone Angle [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                    self.fca_entry = ttk.Entry(confov_specs_frame, width=10)
                    self.fca_entry.insert(0,10)
                    self.fca_entry.bind("<FocusIn>", lambda args: self.fca_entry.delete('0', 'end'))
                    self.fca_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

                def get_specs(self):
                    return (float(self.fca_entry.get()))

            class RectangularFOV(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    rectfov_specs_frame = ttk.Frame(self) 
                    rectfov_specs_frame.grid(row=0, column=0)

                    # define the widgets
                    ttk.Label(rectfov_specs_frame, text="Along track FOV [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                    self.atfov_entry = ttk.Entry(rectfov_specs_frame, width=10)
                    self.atfov_entry.insert(0,10)
                    self.atfov_entry.bind("<FocusIn>", lambda args: self.atfov_entry.delete('0', 'end'))
                    self.atfov_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)
                    
                    ttk.Label(rectfov_specs_frame, text="Cross track FOV [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                    self.ctfov_entry = ttk.Entry(rectfov_specs_frame, width=10)
                    self.ctfov_entry.insert(0,20)
                    self.ctfov_entry.bind("<FocusIn>", lambda args: self.ctfov_entry.delete('0', 'end'))
                    self.ctfov_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)
                
                def get_specs(self):
                    return [float(self.atfov_entry.get()), float(self.ctfov_entry.get())]

            fov_specs_container_frames = {}
            for F in (ConicalFOV, RectangularFOV):
                page_name = F.__name__
                fov_sc_frame = F(parent=fov_specs_container, controller=self)
                fov_specs_container_frames[page_name] = fov_sc_frame
                fov_sc_frame.grid(row=0, column=0, sticky="nsew")
                
            # define the widgets inside the child frames
            
            # constellation types child frame
            FOV_MODES = [
                ("Conical FOV", "ConicalFOV"),
                ("Rectangular FOV", "RectangularFOV")
            ]

            self._sen_fov_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
            self._sen_fov_type.set("ConicalFOV") # initialize

            def senfov_type_rbtn_click():
                if self._sen_fov_type.get() == "ConicalFOV":
                    self.fov_sc_frame = fov_specs_container_frames["ConicalFOV"]
                elif self._sen_fov_type.get() == "RectangularFOV":
                    self.fov_sc_frame = fov_specs_container_frames["RectangularFOV"]
                self.fov_sc_frame.tkraise()

            for text, mode in FOV_MODES:
                fov_type_rbtn = ttk.Radiobutton(fov_type_frame, text=text, command=senfov_type_rbtn_click,
                                variable=self._sen_fov_type, value=mode)
                fov_type_rbtn.pack(anchor='w')

            self.fov_sc_frame = fov_specs_container_frames[self._sen_fov_type.get()]
            self.fov_sc_frame.tkraise()      

            # define the widgets in maneuver_frame
            class FixedManeuver(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    fixedmanuv_specs_frame = ttk.Frame(self) 
                    fixedmanuv_specs_frame.grid(row=0, column=0)

                def get_specs(self):
                    return 0

            class ConeManeuver(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    conemanuv_specs_frame = ttk.Frame(self) 
                    conemanuv_specs_frame.grid(row=0, column=0)

                    # define the widgets 
                    ttk.Label(conemanuv_specs_frame, text="Full Cone Angle [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                    self.conemanuv_fca_entry = ttk.Entry(conemanuv_specs_frame, width=10)
                    self.conemanuv_fca_entry.insert(0,50)
                    self.conemanuv_fca_entry.bind("<FocusIn>", lambda args: self.conemanuv_fca_entry.delete('0', 'end'))
                    self.conemanuv_fca_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

                def get_specs(self):
                    return (float(self.conemanuv_fca_entry.get()))
            
            class RollOnlyManeuver(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    rollmanuv_specs_frame = ttk.Frame(self) 
                    rollmanuv_specs_frame.grid(row=0, column=0)

                    # define the widgets
                    ttk.Label(rollmanuv_specs_frame, text="Minimum Roll [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                    self.manuv_minroll_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
                    self.manuv_minroll_entry.insert(0,-30)
                    self.manuv_minroll_entry.bind("<FocusIn>", lambda args: self.manuv_minroll_entry.delete('0', 'end'))
                    self.manuv_minroll_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)                   

                    ttk.Label(rollmanuv_specs_frame, text="Maximum Roll [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                    self.manuv_maxroll_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
                    self.manuv_maxroll_entry.insert(0,30)
                    self.manuv_maxroll_entry.bind("<FocusIn>", lambda args: self.manuv_maxroll_entry.delete('0', 'end'))
                    self.manuv_maxroll_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)          

                    self.yaw180manuv_chkbut = tk.IntVar()
                    self.yaw180manuv_chkbut.set(0)
                    ttk.Checkbutton(rollmanuv_specs_frame, text='180 deg Yaw',variable=self.yaw180manuv_chkbut, onvalue=1, offvalue=0).grid(row=2, column=0, padx=10, pady=10, sticky='w')
                       
                def get_specs(self):
                    return [float(self.manuv_minroll_entry.get()), float(self.manuv_maxroll_entry.get()), self.yaw180manuv_chkbut.get()]
            
            manuv_specs_container_frames = {}
            for F in (FixedManeuver, ConeManeuver, RollOnlyManeuver):
                page_name = F.__name__
                manuv_sc_frame = F(parent=maneuver_specs_container, controller=self)
                manuv_specs_container_frames[page_name] = manuv_sc_frame
                manuv_sc_frame.grid(row=0, column=0, sticky="nsew")
                            
            # constellation types child frame
            MANUV_MODES = [
                ("Fixed", "FixedManeuver"),
                ("Cone", "ConeManeuver"),
                ("Roll-only", "RollOnlyManeuver")
            ]

            self._sen_manuv_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
            self._sen_manuv_type.set("FixedManeuver") # initialize

            def senmanuv_type_rbtn_click():
                if self._sen_manuv_type.get() == "FixedManeuver":
                    self.manuv_sc_frame = manuv_specs_container_frames["FixedManeuver"]
                elif self._sen_manuv_type.get() == "ConeManeuver":
                    self.manuv_sc_frame = manuv_specs_container_frames["ConeManeuver"]
                elif self._sen_manuv_type.get() == "RollOnlyManeuver":
                    self.manuv_sc_frame = manuv_specs_container_frames["RollOnlyManeuver"]
                self.manuv_sc_frame.tkraise()

            for text, mode in MANUV_MODES:
                senmanuv_type_rbtn = ttk.Radiobutton(maneuver_type_frame, text=text, command=senmanuv_type_rbtn_click,
                                variable=self._sen_manuv_type, value=mode)
                senmanuv_type_rbtn.pack(anchor='w')

            self.manuv_sc_frame = manuv_specs_container_frames[self._sen_manuv_type.get()]
            self.manuv_sc_frame.tkraise()    

            # define the widgets in orien_frame
            class NadirOrientation(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    nadirorien_specs_frame = ttk.Frame(self) 
                    nadirorien_specs_frame.grid(row=0, column=0)

                def get_specs(self):
                    return 0

            class SideLookOrientation(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    sidelookorien_specs_frame = ttk.Frame(self) 
                    sidelookorien_specs_frame.grid(row=0, column=0)

                    # define the widgets
                    ttk.Label(sidelookorien_specs_frame, text="Side Look Angle [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                    self.sla_entry = ttk.Entry(sidelookorien_specs_frame, width=10)
                    self.sla_entry.insert(0,10)
                    self.sla_entry.bind("<FocusIn>", lambda args: self.sla_entry.delete('0', 'end'))
                    self.sla_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)                   
                
                def get_specs(self):
                    return float(self.sla_entry.get())
            
            class XYZOrientation(ttk.Frame):
                def __init__(self, parent, controller):
                    ttk.Frame.__init__(self, parent)
                    xyzorien_specs_frame = ttk.Frame(self) 
                    xyzorien_specs_frame.grid(row=0, column=0)

                    # define the widgets
                    ttk.Label(xyzorien_specs_frame, text="X rotation [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                    self.xorien_entry = ttk.Entry(xyzorien_specs_frame, width=10)
                    self.xorien_entry.insert(0,10)
                    self.xorien_entry.bind("<FocusIn>", lambda args: self.xorien_entry.delete('0', 'end'))
                    self.xorien_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)
                    
                    ttk.Label(xyzorien_specs_frame, text="Y rotation [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                    self.yorien_entry = ttk.Entry(xyzorien_specs_frame, width=10)
                    self.yorien_entry.insert(0,20)
                    self.yorien_entry.bind("<FocusIn>", lambda args: self.yorien_entry.delete('0', 'end'))
                    self.yorien_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

                    ttk.Label(xyzorien_specs_frame, text="Z rotation [deg]", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
                    self.zorien_entry = ttk.Entry(xyzorien_specs_frame, width=10)
                    self.zorien_entry.insert(0,20)
                    self.zorien_entry.bind("<FocusIn>", lambda args: self.zorien_entry.delete('0', 'end'))
                    self.zorien_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)
                
                def get_specs(self):
                    return [float(self.xorien_entry.get()), float(self.yorien_entry.get()), float(self.zorien_entry.get())]

            orien_specs_container_frames = {}
            for F in (NadirOrientation, SideLookOrientation, XYZOrientation):
                page_name = F.__name__
                orien_sc_frame = F(parent=orien_specs_container, controller=self)
                orien_specs_container_frames[page_name] = orien_sc_frame
                orien_sc_frame.grid(row=0, column=0, sticky="nsew")
                
            # define the widgets inside the child frames
            
            # constellation types child frame
            ORIEN_MODES = [
                ("Nadir", "NadirOrientation"),
                ("Side-look", "SideLookOrientation"),
                ("X->Y->Z rotations", "XYZOrientation")
            ]

            self._sen_orien_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
            self._sen_orien_type.set("NadirOrientation") # initialize

            def senorien_type_rbtn_click():
                if self._sen_orien_type.get() == "NadirOrientation":
                    self.orien_sc_frame = orien_specs_container_frames["NadirOrientation"]
                elif self._sen_orien_type.get() == "SideLookOrientation":
                    self.orien_sc_frame = orien_specs_container_frames["SideLookOrientation"]
                elif self._sen_orien_type.get() == "XYZOrientation":
                    self.orien_sc_frame = orien_specs_container_frames["XYZOrientation"]
                self.orien_sc_frame.tkraise()

            for text, mode in ORIEN_MODES:
                senorien_type_rbtn = ttk.Radiobutton(orien_type_frame, text=text, command=senorien_type_rbtn_click,
                                variable=self._sen_orien_type, value=mode)
                senorien_type_rbtn.pack(anchor='w')

            self.orien_sc_frame = orien_specs_container_frames[self._sen_orien_type.get()]
            self.orien_sc_frame.tkraise()      

            # define the widgets in okcancel_frame
            # okcancel frame
            def add_sensor_click():  
                # create window to ask which satellites to attach the sensor to
                select_sat_win = tk.Toplevel()
                select_sat_win_frame = ttk.LabelFrame(select_sat_win, text='Select Satellite(s)')
                select_sat_win_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10) 
                okcancel_frame_2 = ttk.Label(select_sat_win)
                okcancel_frame_2.grid(row=1, column=0, columnspan=2, padx=10, pady=10) 

                orb_specs = miss_specs.get_satellite_kepl_specs()  # get all available sats in the configuration              

                sat_tree_scroll = ttk.Scrollbar(select_sat_win_frame)
                sat_tree_scroll.grid(row=0, column=1, sticky='nsw')
                sat_tree = ttk.Treeview(select_sat_win_frame, yscrollcommand=sat_tree_scroll.set)
                sat_tree.grid(row=0, column=0, sticky='e')
                sat_tree_scroll.config(command=sat_tree.yview)

                sat_tree['columns'] = ("ID", "Alt", "Inc", "RAAN", "AOP", "TA")
                sat_tree.column('#0', width=0, stretch="no")
                sat_tree.column("ID", width = 80)        
                sat_tree.column("Alt",  width = 80)     
                sat_tree.column("Inc", width = 80)     
                sat_tree.column("RAAN", width = 80)     
                sat_tree.column("AOP",  width = 80)     
                sat_tree.column("TA", width = 80)            

                sat_tree.heading("#0", text="", anchor="w")
                sat_tree.heading("ID", text="ID", anchor="w")
                sat_tree.heading("Alt", text="Altitude [km]", anchor="w")
                sat_tree.heading("Inc", text="Inclination [deg]", anchor="w")
                sat_tree.heading("RAAN", text="RAAN [deg]", anchor="w")
                sat_tree.heading("AOP", text="AOP [deg]", anchor="w")
                sat_tree.heading("TA", text="TA [deg]", anchor="w")

                for k in range(0,len(orb_specs)):
                    sat_tree.insert(parent='', index='end', iid=orb_specs[k][0], text="", values=(orb_specs[k][0], orb_specs[k][1], orb_specs[k][2], orb_specs[k][3], orb_specs[k][4], orb_specs[k][5], orb_specs[k][6]))

                def ok_click_2():
                    """ Actions upon the click add Sensor followed by selection of satellites. The mission configuration file is updated with the sensors
                        attached to the respective satellites.
                    """
                    data = {} 
                    data['name'] = name_entry.get() 
                    data['@id'] = uid_entry.get()
                    data['@type'] = "Basic Sensor"
                    data['volume'] = vol_entry.get()
                    data['mass'] = mass_entry.get()
                    data['power'] = pow_entry.get()
                    data['bitsPerPixel'] = bpp_entry.get()                    
                    data['dataRate'] = dr_entry.get()   

                    data['fieldOfView'] = {}
                    specs = self.fov_sc_frame.get_specs() 
                    if self._sen_fov_type.get() == "ConicalFOV":                                       
                        data['fieldOfView']['sensorGeometry'] = 'Conical'
                        data['fieldOfView']['fullConeAngle'] = specs     
                    elif self._sen_fov_type.get() == 'RectangularFOV':
                        data['fieldOfView']['sensorGeometry'] = 'Rectangular'
                        data['fieldOfView']['alongTrackFieldOfView'] = specs[0] 
                        data['fieldOfView']['crossTrackFieldOfView'] = specs[1]

                    data['maneuverability'] = {}
                    specs = self.manuv_sc_frame.get_specs()
                    if self._sen_manuv_type.get() == "FixedManeuver":                                        
                        data['maneuverability']['@type'] = 'Fixed'
                    elif self._sen_manuv_type.get() == 'ConeManeuver':
                        data['maneuverability']['@type'] = 'Cone'
                        data['maneuverability']['fullConeAngle'] = specs
                    elif self._sen_manuv_type.get() == 'RollOnlyManeuver':
                        if specs[2] == 0:
                            data['maneuverability']['@type'] = 'RollOnly'
                            data['maneuverability']['rollMin'] = specs[0] 
                            data['maneuverability']['rollMax'] = specs[1]
                        else: # yaw 180 manuver indicated
                            data['maneuverability']['@type'] = 'Yaw180Roll'
                            data['maneuverability']['rollMin'] = specs[0] 
                            data['maneuverability']['rollMax'] = specs[1]
                    
                    data['orientation'] = {}
                    specs = self.orien_sc_frame.get_specs()
                    if self._sen_orien_type.get() == "NadirOrientation":                                        
                        data['orientation']['convention'] = 'NADIR'
                    elif self._sen_orien_type.get() == 'SideLookOrientation':
                        data['orientation']['convention'] = 'SIDE_LOOK'
                        data['orientation']['sideLookAngle'] = specs
                    elif self._sen_orien_type.get() == 'XYZOrientation':
                        data['orientation']['convention'] = 'XYZ'
                        data['orientation']['xRotation'] = specs[0] 
                        data['orientation']['yRotation'] = specs[1]
                        data['orientation']['zRotation'] = specs[1]

                    _sen = Instrument.from_dict(data)
                    miss_specs.add_sensor(_sen, sat_tree.selection())
                    select_sat_win.destroy()

                ok_btn_2 = ttk.Button(okcancel_frame_2, text="Ok", command=ok_click_2, width=ConfigureFrame.BTNWIDTH)
                ok_btn_2.grid(row=0, column=0, sticky ='e')

                cancel_btn_2 = ttk.Button(okcancel_frame_2, text="Exit", command=select_sat_win.destroy, width=ConfigureFrame.BTNWIDTH)
                cancel_btn_2.grid(row=0, column=1, sticky ='w') 

            ok_btn = ttk.Button(okcancel_frame, text="Add", command=add_sensor_click, width=ConfigureFrame.BTNWIDTH)
            ok_btn.grid(row=0, column=0)

            cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=sensor_win.destroy, width=ConfigureFrame.BTNWIDTH)
            cancel_btn.grid(row=0, column=1) 

        def passive_opt_sen_input_config(win, tab):
            ttk.Label(tab,  text ="Under dev").grid(column = 0, row = 0, padx = 30, pady = 30)   

        def synthetic_aperture_radar_input_config(win, tab):
            ttk.Label(tab,  text ="Under dev").grid(column = 0, row = 0, padx = 30, pady = 30)   

        # create and configure child window, parent frame
        sensor_win = tk.Toplevel()
        sensor_win.rowconfigure(0,weight=1)
        sensor_win.columnconfigure(0,weight=1)

        tabControl = ttk.Notebook(sensor_win)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='Basic Sensor')
        tabControl.add(tab2, text='Passive Optical Sensor')
        tabControl.add(tab3, text='Synthetic Aperture Radar')

        tabControl.pack(expand = 1, fill ="both")   

        basic_sensor_input_config(sensor_win, tab1)
        passive_opt_sen_input_config(sensor_win, tab2)
        synthetic_aperture_radar_input_config(sensor_win, tab3)


    def click_propagate_settings_btn(self):      

        # create and configure child window, parent frame
        prop_win = tk.Toplevel()
        prop_win.rowconfigure(0,weight=1)
        prop_win.columnconfigure(0,weight=1)

        prop_win_frame = ttk.Frame(prop_win)
        prop_win_frame.grid(row=0, column=0, padx=10, pady=10)
        prop_win_frame.rowconfigure(0,weight=1) # propagator type
        prop_win_frame.rowconfigure(1,weight=1) # propagator specs
        prop_win_frame.rowconfigure(2,weight=1) # okcancel
        prop_win_frame.columnconfigure(0,weight=1)

        # define all child frames
        prop_type_frame = ttk.LabelFrame(prop_win_frame, text="Propagator")
        prop_type_frame.grid(row=0, column=0, sticky='nswe', padx=20, pady=20)
        prop_type_frame.columnconfigure(0,weight=1)
        prop_type_frame.rowconfigure(0,weight=1)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        # grid configure
        prop_specs_container = ttk.LabelFrame(prop_win_frame, text="Specifications", width=250, height=200)
        prop_specs_container.grid_propagate(0)
        prop_specs_container.grid(row=1, column=0, sticky='nswe', padx=20, pady=20)
        prop_specs_container.columnconfigure(0,weight=1)
        prop_specs_container.rowconfigure(0,weight=1)

        # okcancel frame
        okcancel_frame = ttk.Label(prop_win_frame)
        okcancel_frame.grid(row=2, column=0, sticky='nswe', padx=20, pady=20)
        okcancel_frame.columnconfigure(0,weight=1)
        okcancel_frame.rowconfigure(0,weight=1)

        class OrbitPyJ2AnalyticalPropagator(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)
                orbitpy_specs_frame = ttk.Frame(self) 
                orbitpy_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)

                # define the widgets inside the child frames
                ttk.Label(orbitpy_specs_frame, text="All entries are optional", wraplength=150).grid(row=0, column=0, padx=10, pady=10)

                ttk.Label(orbitpy_specs_frame, text="Custom Time Step [s]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                self.cus_time_step_entry = ttk.Entry(orbitpy_specs_frame, width=10)
                self.cus_time_step_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(orbitpy_specs_frame, text="Custom Time Resolution Factor", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
                self.cus_time_resf_entry = ttk.Entry(orbitpy_specs_frame, width=10)
                self.cus_time_resf_entry.grid(row=2, column=1, sticky='w')               
            
            def get_specs(self):
                return [self.cus_time_step_entry.get(), self.cus_time_resf_entry.get()]               

        class GMATPreComputedSatelliteStates(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)         
                hetw_specs_frame = ttk.Frame(self) 
                hetw_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)    
                ttk.Label(hetw_specs_frame, text="Under development").pack()
                #sim_dir_path = tkinter.filedialog.askdirectory(initialdir=os.getcwd(), title="Please select an empty folder:")      
        
        class STKPreComputedSatelliteStates(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)  
                trainc_specs_frame = ttk.Frame(self) 
                trainc_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)
                ttk.Label(trainc_specs_frame, text="Under development").pack()          

        frames = {}
        for F in (OrbitPyJ2AnalyticalPropagator, GMATPreComputedSatelliteStates, STKPreComputedSatelliteStates):
            page_name = F.__name__
            frame = F(parent=prop_specs_container, controller=self)
            frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # define the widgets inside the child frames
        
        # propagator types child frame
        MODES = [
            ("J2 Analytical Propagator", "OrbitPyJ2AnalyticalPropagator"),
            ("GMAT Pre-computed Satellite States", "GMATPreComputedSatelliteStates"),
            ("STK Pre-computed Satellite States", "STKPreComputedSatelliteStates")
        ]

        self._prop_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._prop_type.set("OrbitPyJ2AnalyticalPropagator") # initialize

        def prop_type_rbtn_click():
            if self._prop_type.get() == "OrbitPyJ2AnalyticalPropagator":
                frame = frames["OrbitPyJ2AnalyticalPropagator"]
            elif self._prop_type.get() == "GMATPreComputedSatelliteStates":
                frame = frames["GMATPreComputedSatelliteStates"]
            elif self._prop_type.get() == "STKPreComputedSatelliteStates":
                frame = frames["STKPreComputedSatelliteStates"]

            frame.tkraise()

        for text, mode in MODES:
            prop_type_rbtn = ttk.Radiobutton(prop_type_frame, text=text, command=prop_type_rbtn_click,
                            variable=self._prop_type, value=mode)
            prop_type_rbtn.pack(anchor='w', padx=20, pady=20)

        frame = frames[self._prop_type.get()]
        frame.tkraise()    

        # okcancel frame
        def ok_click():               
            if self._prop_type.get() == "OrbitPyJ2AnalyticalPropagator":
                specs = frames[self._prop_type.get()].get_specs()
                prop = {}
                prop['@type'] = 'OrbitPyJ2Analytical'
                prop['customTimeStep'] = float(specs[0]) if specs[0] != "" else None
                prop['customTimeResFactor'] = float(specs[1]) if specs[1] != "" else None          
 
                miss_specs.add_propagator(prop)
                prop_win.destroy()
            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=prop_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)  

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

                sen_specs = miss_specs.get_sensor_specs()  # get all available sensors in the configuration                 
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
                miss_specs.add_coverage_grid(specs)
                cov_win.destroy()
            if self._cov_type.get() == "PointingOptionsCoverageCalculator":
                specs = frames[self._cov_type.get()].get_specs()
                miss_specs.add_pointing_options(specs) 
                cov_win.destroy()
            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=cov_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)  
        
    def click_gs_btn(self):
         # create and configure child window, parent frame
        gs_win = tk.Toplevel()

        gs_win_frame = ttk.Frame(gs_win)
        gs_win_frame.grid(row=0, column=0, padx=5, pady=5)

        gs_add_by_entry_frame = ttk.Frame(gs_win_frame)
        gs_add_by_entry_frame.grid(row=0, column=0)

        gs_add_by_datafile_frame = ttk.Frame(gs_win_frame)
        gs_add_by_datafile_frame.grid(row=1, column=0)

        # okcancel frame
        okcancel_frame = ttk.Label(gs_win_frame)
        okcancel_frame.grid(row=2, column=0, sticky='nswe', padx=5, pady=5)
        okcancel_frame.columnconfigure(0,weight=1)
        okcancel_frame.rowconfigure(0,weight=1)

        # define the widgets inside the child frames
        self._gs_specs_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._gs_specs_type.set("ManualEntry") # initialize
        def gs_specs_rbtn_click():
            if self._gs_specs_type.get() == "ManualEntry":
                # disable the frame containing the other option, except for the radio-button
                for child in gs_add_by_datafile_frame.winfo_children():
                    child.configure(state='disable')
                gs_specs_type_rbtn_2.configure(state='normal')
                # enable the frame containing the current option
                for child in gs_add_by_entry_frame.winfo_children():
                    child.configure(state='normal')
                
            elif self._gs_specs_type.get() == "DataFile":
                # disable the frame containing the other option, except for the radio-button
                for child in gs_add_by_entry_frame.winfo_children():
                    child.configure(state='disable')   
                gs_specs_type_rbtn_1.configure(state='normal')
                # enable the frame containing the current option
                for child in gs_add_by_datafile_frame.winfo_children():
                    child.configure(state='normal')             

        gs_specs_type_rbtn_1 = ttk.Radiobutton(gs_add_by_entry_frame, text="Manual Entry", command=gs_specs_rbtn_click,
                                                        variable=self._gs_specs_type, value="ManualEntry")
        gs_specs_type_rbtn_1.grid(row=0, column=0, padx=10, pady=10)

        self.gs_info = []
        def add_gs():
            self.gs_info.append({'@id': float(gs_specs_gsid_entry.get()), 
                                 'name': float(gs_specs_name_entry.get()), 
                                 'lat': float(gs_specs_lat_entry.get()), 
                                 'lon': float(gs_specs_lon_entry.get()),                                              
                                 'alt': float(gs_specs_alt_entry.get()),
                                 'minElevation': float(gs_specs_minelv_entry.get())})

        ttk.Button(gs_add_by_entry_frame, text="Add GS", command=add_gs).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(gs_add_by_entry_frame, text="ID").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        gs_specs_gsid_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_gsid_entry.insert(0,random.randint(0,100))
        gs_specs_gsid_entry.bind("<FocusIn>", lambda args: gs_specs_gsid_entry.delete('0', 'end'))
        gs_specs_gsid_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Name").grid(row=2, column=0, sticky='w', padx=10, pady=10)
        gs_specs_name_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_name_entry.insert(0,-10)
        gs_specs_name_entry.bind("<FocusIn>", lambda args: gs_specs_name_entry.delete('0', 'end'))
        gs_specs_name_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Lat [deg]").grid(row=3, column=0, sticky='w', padx=10, pady=10)
        gs_specs_lat_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_lat_entry.insert(0,-10)
        gs_specs_lat_entry.bind("<FocusIn>", lambda args: gs_specs_lat_entry.delete('0', 'end'))
        gs_specs_lat_entry.grid(row=3, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Lon [deg]").grid(row=4, column=0, sticky='w', padx=10, pady=10)
        gs_specs_lon_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_lon_entry.insert(0,20)
        gs_specs_lon_entry.bind("<FocusIn>", lambda args: gs_specs_lon_entry.delete('0', 'end'))
        gs_specs_lon_entry.grid(row=4, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Alt [km]").grid(row=5, column=0, sticky='w', padx=10, pady=10)
        gs_specs_alt_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_alt_entry.insert(0,-110)
        gs_specs_alt_entry.bind("<FocusIn>", lambda args: gs_specs_alt_entry.delete('0', 'end'))
        gs_specs_alt_entry.grid(row=5, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Min Elevation [deg]").grid(row=6, column=0, sticky='w', padx=10, pady=10)
        gs_specs_minelv_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_minelv_entry.insert(0,-10)
        gs_specs_minelv_entry.bind("<FocusIn>", lambda args: gs_specs_minelv_entry.delete('0', 'end'))
        gs_specs_minelv_entry.grid(row=6, column=1, sticky='w')

        gs_specs_type_rbtn_2 = ttk.Radiobutton(gs_add_by_datafile_frame, text="Data file", command=gs_specs_rbtn_click,
                            variable=self._gs_specs_type, value="DataFile")
        gs_specs_type_rbtn_2.grid(row=0, column=0, padx=10, pady=5)

        def click_gs_data_file_path_btn():
            self.gs_data_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the ground-station data file:", filetypes=(("All files","*.*"), ("csv files","*.csv")))  
            gs_data_fp_entry.configure(state='normal')
            gs_data_fp_entry.delete(0,'end')
            gs_data_fp_entry.insert(0,self.gs_data_fp)
            gs_data_fp_entry.configure(state='disabled')                    

        ttk.Button(gs_add_by_datafile_frame, text="Select Path", command=click_gs_data_file_path_btn, state='disabled').grid(row=0, column=1, sticky='w', padx=10, pady=10)
        gs_data_fp_entry=tk.Entry(gs_add_by_datafile_frame, state='disabled')
        gs_data_fp_entry.grid(row=1,column=0, padx=10, pady=10, columnspan=2, sticky='ew')

        # okcancel frame
        def ok_click():               
            if self._gs_specs_type.get() == "ManualEntry":
                specs = {"stationInfo": self.gs_info}                
            if self._gs_specs_type.get() == "DataFile":
                specs = {"gndStnFilePath": self.gs_data_fp  }              
            miss_specs.add_ground_stations(specs)
            gs_win.destroy()  
                            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=gs_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)  

    def click_visualize_btn(self):
        vis_win = tk.Toplevel()
        ttk.Label(vis_win, text=(miss_specs.to_dict()), wraplength=150).pack(padx=5, pady=5)

    