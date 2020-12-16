import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
import eosim.gui.helpwindow as helpwindow
from eosim import config
from eosim.gui.mapprojections import Mercator, EquidistantConic, LambertConformal, Robinson, LambertAzimuthalEqualArea, Gnomonic
import json
import logging
logger = logging.getLogger(__name__)

class OperationsFrame(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

        synobsmain_frame = ttk.LabelFrame(self, text="Synthesize Observations", labelanchor='n') 
        synobsmain_frame.grid(row=0, column=0, ipadx=20, ipady=20, sticky='nsew')
        synobsmain_frame.rowconfigure(0,weight=1)
        synobsmain_frame.rowconfigure(1,weight=1)
        synobsmain_frame.columnconfigure(0,weight=1)
        synobsmain_frame.columnconfigure(1,weight=1)

        synobsvisz_frame = ttk.LabelFrame(self, text="Observations Visualization", labelanchor='n') 
        synobsvisz_frame.grid(row=0, column=1, rowspan=2, ipadx=20, ipady=20, sticky='nsew')
        synobsvisz_frame.rowconfigure(0,weight=1)
        synobsvisz_frame.rowconfigure(1,weight=1)
        synobsvisz_frame.rowconfigure(2,weight=1)
        synobsvisz_frame.columnconfigure(0,weight=1)
        
        synobsvis_choose_image_frame = ttk.Frame(synobsvisz_frame)
        synobsvis_choose_image_frame.grid(row=0, column=0, sticky='nswe') 
        synobsvis_choose_image_frame.columnconfigure(0,weight=1)
        synobsvis_choose_image_frame.rowconfigure(0,weight=1)

        synobsvis_map_proj_frame = ttk.LabelFrame(synobsvisz_frame, text='Set Map Projection', labelanchor='n')
        synobsvis_map_proj_frame.grid(row=1, column=0, sticky='nswe', padx=10)
        synobsvis_map_proj_frame.columnconfigure(0,weight=1)
        synobsvis_map_proj_frame.rowconfigure(0,weight=1)
        synobsvis_map_proj_frame.rowconfigure(1,weight=1)

        synobsvis_map_proj_type_frame = ttk.Frame(synobsvis_map_proj_frame)
        synobsvis_map_proj_type_frame.grid(row=0, column=0)       
        proj_specs_container = ttk.Frame(synobsvis_map_proj_frame)
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

        synobsvis_map_plot_frame = ttk.Frame(synobsvisz_frame)
        synobsvis_map_plot_frame.grid(row=2, column=0, sticky='nswe') 
        synobsvis_map_plot_frame.columnconfigure(0,weight=1)
        synobsvis_map_plot_frame.columnconfigure(1,weight=1)
        synobsvis_map_plot_frame.columnconfigure(2,weight=1)
        synobsvis_map_plot_frame.rowconfigure(0,weight=1)

        opvisz_frame = ttk.LabelFrame(self, text="Operations Visualization", labelanchor='n') 
        opvisz_frame.grid(row=1, column=0, ipadx=20, ipady=20, sticky='nsew')
        opvisz_frame.rowconfigure(0,weight=1)
        opvisz_frame.rowconfigure(1,weight=8)
        opvisz_frame.columnconfigure(0,weight=1)

        # define the widgets in the synobsmain_frame
        tk.Button(synobsmain_frame, text="Select Command File", wraplength=100, width=15, command=self.click_select_command_file).grid(row=0, column=0)
        tk.Button(synobsmain_frame, text="Synthesize Observations", wraplength=100, width=15, command=self.click_synobs_plot_btn).grid(row=1, column=0)

        # define widgets for the synobsvisz_frame
        ttk.Button(synobsvis_choose_image_frame, text="Choose images to plot").grid(row=0, column=0)
        
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

        projtype_combo_box = ttk.Combobox(synobsvis_map_proj_type_frame, 
                                        values=PROJ_TYPES, textvariable = self._proj_type, width=25)
        projtype_combo_box.current(0)
        projtype_combo_box.grid(row=0, column=0)
        projtype_combo_box.bind("<<ComboboxSelected>>", proj_type_combobox_change)
        
        # plot frame
        ttk.Checkbutton(synobsvis_map_plot_frame, text="Auto crop").grid(row=0, column=0)
        ttk.Button(synobsvis_map_plot_frame, text="Plot", command=self.click_synobs_plot_btn).grid(row=0, column=1, columnspan=2, padx=20)

        # define widgets in the opvisz_frame
        tk.Button(opvisz_frame, text="Launch \n (Cesium powered Globe visualization)", wraplength=150, width=20).grid(row=0, column=0, ipadx=20, ipady=10, pady=10)
    
    


    def click_synobs_plot_btn(self):
        pass
    
    def click_select_command_file(self):
        cmdfile_fp = None
        cmdfile_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the command file:", filetypes=(("All files","*.*"),("json files","*.json")))
        if cmdfile_fp != '':
            with open(cmdfile_fp) as f:
                self.command = json.load(f)  
            logger.info("Command file successfully is read.")