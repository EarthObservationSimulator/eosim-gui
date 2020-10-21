from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
from orbitpy.preprocess import OrbitParameters
import random
from tkinter import messagebox
import json
import orbitpy

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
        sen_btn = ttk.Button(resource_frame, text="Sensor", width=ConfigureFrame.BTNWIDTH)
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
        save_conf_btn = ttk.Button(self, text="Save Config", width=ConfigureFrame.BTNWIDTH)
        save_conf_btn.grid(row=2, column=0, pady=(1,10), sticky='e')
        run_all_btn = ttk.Button(self, text="Run All", width=ConfigureFrame.BTNWIDTH)
        run_all_btn.grid(row=2, column=1, pady=(1,10), sticky='w')

    def click_mission_btn(self):      

        # create and configure child window, parent frame
        miss_win = tk.Toplevel()
        #miss_win.geometry(GuiStyle.child_window_geom)

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
            satellite = OrbitParameters(_id=uid_entry.get(), sma=sma_entry.get()+orbitpy.util.Constants.radiusOfEarthInKM, ecc=ecc_entry.get(), 
                            inc=inc_entry.get(), raan=raan_entry.get(), aop=aop_entry.get(), ta=ta_entry.get())
            miss_specs.add_satellite(satellite)
            

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=ok_click, width=ConfigureFrame.BTNWIDTH)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=sat_win.destroy, width=ConfigureFrame.BTNWIDTH)
        cancel_btn.grid(row=0, column=1)

    def click_constellation_btn(self):      

        class HomogenousWalkerFrame(ttk.Frame):
            def __init__(self, parent, controller):
                ttk.Frame.__init__(self, parent)
                hwd_specs_frame = ttk.Frame(self) 
                hwd_specs_frame.grid(row=0, column=0, ipadx=20, ipady=20)

                # define the widgets inside the child frames
                ttk.Label(hwd_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
                uid_entry = ttk.Entry(hwd_specs_frame, width=10)
                uid_entry.insert(0,"constl_A_"+str(random.randint(0,1000)))
                uid_entry.bind("<FocusIn>", lambda args: uid_entry.delete('0', 'end'))
                uid_entry.grid(row=0, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="# Satellites", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
                nsats_entry = ttk.Entry(hwd_specs_frame, width=10)
                nsats_entry.insert(0,6)
                nsats_entry.bind("<FocusIn>", lambda args: nsats_entry.delete('0', 'end'))
                nsats_entry.grid(row=1, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="# Orbital planes", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
                sma_entry = ttk.Entry(hwd_specs_frame, width=10)
                sma_entry.insert(0,800)
                sma_entry.bind("<FocusIn>", lambda args: sma_entry.delete('0', 'end'))
                sma_entry.grid(row=2, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="Relative spacing", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
                ecc_entry = ttk.Entry(hwd_specs_frame, width=10)
                ecc_entry.insert(0,1)
                ecc_entry.bind("<FocusIn>", lambda args: ecc_entry.delete('0', 'end'))
                ecc_entry.grid(row=3, column=1, sticky='w')

                ttk.Label(hwd_specs_frame, text="Inclination [deg]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
                inc_entry = ttk.Entry(hwd_specs_frame, width=10)
                inc_entry.insert(0,67)
                inc_entry.bind("<FocusIn>", lambda args: inc_entry.delete('0', 'end'))
                inc_entry.grid(row=4, column=1, sticky='w')
                
                ttk.Label(hwd_specs_frame, text="Altitude [km]", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
                raan_entry = ttk.Entry(hwd_specs_frame, width=10)
                raan_entry.insert(0,270)
                raan_entry.bind("<FocusIn>", lambda args: raan_entry.delete('0', 'end'))
                raan_entry.grid(row=5, column=1, sticky='w')

                tk.Label(hwd_specs_frame, text="Eccentricity", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
                aop_entry = ttk.Entry(hwd_specs_frame, width=10)
                aop_entry.insert(0,0)
                aop_entry.bind("<FocusIn>", lambda args: aop_entry.delete('0', 'end'))
                aop_entry.grid(row=6, column=1, sticky='w')

                tk.Label(hwd_specs_frame, text="AOP [deg]", wraplength=150).grid(row=7, column=0, padx=10, pady=10, sticky='w')
                ta_entry = ttk.Entry(hwd_specs_frame, width=10)
                ta_entry.insert(0,20)
                ta_entry.bind("<FocusIn>", lambda args: ta_entry.delete('0', 'end'))
                ta_entry.grid(row=7, column=1, sticky='w')

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

        # create and configure child window, parent frame
        constl_win = tk.Toplevel()
        constl_win.rowconfigure(0,weight=1)
        constl_win.columnconfigure(0,weight=1)

        constl_win_frame =ttk.Frame(constl_win)
        constl_win_frame.grid(row=0, column=0, padx=10, pady=10)
        constl_win_frame.rowconfigure(0,weight=1)
        constl_win_frame.rowconfigure(1,weight=1)
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
        constl_specs_container = ttk.LabelFrame(constl_win_frame, text="Specifications", width=200, height=300)
        constl_specs_container.grid_propagate(0)
        constl_specs_container.grid(row=1, column=0, sticky='nswe', padx=20, pady=20)
        constl_specs_container.columnconfigure(0,weight=1)
        constl_specs_container.rowconfigure(0,weight=1)

        frames = {}
        for F in (HomogenousWalkerFrame, HeterogenousWalkerFrame, TrainConstlFrame):
            page_name = F.__name__
            frame = F(parent=constl_specs_container, controller=self)
            frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        okcancel_frame = ttk.Frame(constl_win_frame)
        okcancel_frame.grid(row=2, column=0)  
        
        # define the widgets inside the child frames
        
        # constellation types child frame
        MODES = [
            ("Homogenous Walker Delta", "HomogenousWalkerFrame"),
            ("Heterogenous Walker", "HeterogenousWalkerFrame"),
            ("Train", "TrainConstlFrame")
        ]

        self._ctype = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._ctype.set("HomogenousWalkerFrame") # initialize

        def constl_type_rbtn_click():
            if self._ctype.get() == "HomogenousWalkerFrame":
                frame = frames["HomogenousWalkerFrame"]
            elif self._ctype.get() == "HeterogenousWalkerFrame":
                frame = frames["HeterogenousWalkerFrame"]
            elif self._ctype.get() == "TrainConstlFrame":
                frame = frames["TrainConstlFrame"]

            frame.tkraise()

        for text, mode in MODES:
            constl_type_rbtn = ttk.Radiobutton(constl_type_frame, text=text, command=constl_type_rbtn_click,
                            variable=self._ctype, value=mode)
            constl_type_rbtn.pack(anchor='w', padx=20, pady=20)

        frame = frames[self._ctype.get()]
        frame.tkraise()
        
        


    def click_visualize_frame(self):
        vis_win = tk.Toplevel()
        ttk.Label(vis_win, text=(miss_specs.to_dict()), wraplength=150).pack(padx=20, pady=20)

