from tkinter import ttk 
import tkinter as tk
from eosim import config
import orbitpy
import eosim.gui.helpwindow as helpwindow
import logging

logger = logging.getLogger(__name__)

class CfPropagate():

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
                specs = {}
                specs['@type'] = 'J2 ANALYTICAL PROPAGATOR'
                specs['stepSize'] = float(self.cus_time_step_entry.get()) if self.cus_time_step_entry.get() != "" else None
                specs['propTimeResFactor'] = float(self.cus_time_resf_entry.get()) if self.cus_time_resf_entry.get() != "" else None
                return specs             

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
            ("J2 ANALYTICAL PROPAGATOR", "OrbitPyJ2AnalyticalPropagator"),
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
                config.mission.update_propagator_settings(specs, propTimeResFactor=specs["propTimeResFactor"])
                logger.info('Updated propagator settings. If you have relied upon the auto-generated (time) step-size,note that it has been generated using the current list of spacecraft.')
                prop_win.destroy()
            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=prop_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)  
