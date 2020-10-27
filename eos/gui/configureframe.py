from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
from orbitpy.preprocess import OrbitParameters, PreProcess
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.basic_sensor import BasicSensor

miss_specs = MissionConfig()     

class ConfigureFrame(ttk.Frame):

    BTNWIDTH = 15

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=2)
        self.rowconfigure(1,weight=2)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=2)
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
        gndstn_btn = ttk.Button(resource_frame, text="Ground Station", width=ConfigureFrame.BTNWIDTH)
        gndstn_btn.grid(row=1, column=1)

        #
        visual_frame = ttk.LabelFrame(self, text="Visualize", labelanchor='n') 
        visual_frame.grid(row=1, column=0, ipadx=20, ipady=20)
        visual_frame.rowconfigure(0,weight=1)
        visual_frame.columnconfigure(0,weight=1)
        vis_arch_btn = ttk.Button(visual_frame, text="Visualize Arch", command=self.click_visualize_frame, width=ConfigureFrame.BTNWIDTH)
        vis_arch_btn.grid(row=0, column=0)

        # "Settings" frame
        settings_frame = ttk.LabelFrame(self, text="Settings", labelanchor='n') 
        settings_frame.grid(row=1, column=1, ipadx=20, ipady=20)
        settings_frame.rowconfigure(0,weight=1)
        settings_frame.rowconfigure(1,weight=1)
        settings_frame.columnconfigure(0,weight=1)
        settings_frame.columnconfigure(1,weight=1)
        prp_set_btn = ttk.Button(settings_frame, text="Propagate", width=ConfigureFrame.BTNWIDTH)
        prp_set_btn.grid(row=0, column=0)
        com_set_btn = ttk.Button(settings_frame, text="Comm", width=ConfigureFrame.BTNWIDTH)
        com_set_btn.grid(row=0, column=1)
        cov_set_btn = ttk.Button(settings_frame, text="Coverage", width=ConfigureFrame.BTNWIDTH)
        cov_set_btn.grid(row=1, column=0)
        obs_syn_btn = ttk.Button(settings_frame, text="Obs Synthesis", width=ConfigureFrame.BTNWIDTH)
        obs_syn_btn.grid(row=1, column=1)

        #
        save_conf_btn = ttk.Button(self, text="Save Config", command=self.click_save_config, width=ConfigureFrame.BTNWIDTH)
        save_conf_btn.grid(row=2, column=0, pady=(1,10), sticky='e')
        run_all_btn = ttk.Button(self, text="Run All", width=ConfigureFrame.BTNWIDTH)
        run_all_btn.grid(row=2, column=1, pady=(1,10), sticky='w')

    def click_save_config(self):
        with open('MissionConfig.json', 'w', encoding='utf-8') as f:
            json.dump(miss_specs.to_dict(), f, ensure_ascii=False, indent=4)
        tkinter.messagebox.showinfo(title=None, message="Configuration saved in working directory.")

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
                specs = frame.get_specs()
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
            other_specs_frame = ttk.LabelFrame(specs_frame) # specifications other then FOV, maneuver, orientation frame
            other_specs_frame.grid(row=0, column=0, padx=10, pady=10)
            
            fov_specs_frame = ttk.LabelFrame(specs_frame, text="Field-Of-View") # field-of-view (FOV) specifications frame
            fov_specs_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n')
            # define all child frames
            fov_type_frame = ttk.Frame(fov_specs_frame)
            fov_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
            fov_type_frame.columnconfigure(0,weight=1)
            fov_type_frame.rowconfigure(0,weight=1)

            fov_specs_container = ttk.Frame(fov_specs_frame)
            fov_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
            fov_specs_container.columnconfigure(0,weight=1)
            fov_specs_container.rowconfigure(0,weight=1)

            maneuver_frame = ttk.LabelFrame(specs_frame, text="Manuever") # manuver specs frame
            maneuver_frame.grid(row=0, column=2, padx=10, pady=10)

            orien_frame = ttk.LabelFrame(specs_frame, text="Orientation") # sensor orientation frame
            orien_frame.grid(row=0, column=3, padx=10, pady=10)
            # define all child frames
            orien_type_frame = ttk.Frame(orien_frame)
            orien_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
            orien_type_frame.columnconfigure(0,weight=1)
            orien_type_frame.rowconfigure(0,weight=1)

            orien_specs_container = ttk.Frame(orien_frame)
            orien_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
            orien_specs_container.columnconfigure(0,weight=1)
            orien_specs_container.rowconfigure(0,weight=1)

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
                    self.fca_entry.insert(0,35)
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
                    self.zorien_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)
                
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
            def ok_click():  
                data = {} 
                data['name'] = name_entry.get() 
                data['@id'] = uid_entry.get()
                data['volume'] = vol_entry.get()
                data['mass'] = mass_entry.get()
                data['power'] = pow_entry.get()
                data['bitsPerPixel'] = bpp_entry.get()                    
                data['dataRate'] = dr_entry.get()   

                data['fieldOfView'] = {}
                specs = self.fov_sc_frame.get_specs() 
                print(specs)
                if self._sen_fov_type.get() == "ConicalFOV":                                       
                    data['fieldOfView']['sensorGeometry'] = 'Conical'
                    data['fieldOfView']['fullConeAngle'] = specs     
                elif self._sen_fov_type.get() == 'RectangularFOV':
                    data['fieldOfView']['sensorGeometry'] = 'Rectangular'
                    data['fieldOfView']['alongTrackFieldOfView'] = specs[0] 
                    data['fieldOfView']['crossTrackFieldOfView'] = specs[1]
                      
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
                print(data)
                basic_sen = BasicSensor.from_dict(data)
                miss_specs.add_sensor(basic_sen)
            
            #miss_config.get_satellite_ids

            ok_btn = ttk.Button(okcancel_frame, text="Add", command=ok_click, width=ConfigureFrame.BTNWIDTH)
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


    def click_visualize_frame(self):
        vis_win = tk.Toplevel()
        ttk.Label(vis_win, text=(miss_specs.to_dict()), wraplength=150).pack(padx=20, pady=20)

