from tkinter import ttk 
import tkinter as tk
from eosim import config
import random
import json
import tkinter.filedialog, tkinter.messagebox
import os
import eosim.gui.helpwindow as helpwindow
import logging

logger = logging.getLogger(__name__)

class CfGroundStation():
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

        def add_gs():
            gs_info_dict = {'@id': (gs_specs_gsid_entry.get()), 
                            'name': str(gs_specs_name_entry.get()), 
                            'latitude': float(gs_specs_lat_entry.get()), 
                            'longitude': float(gs_specs_lon_entry.get()),                                              
                            'altitude': float(gs_specs_alt_entry.get()),
                            'minimumElevation': float(gs_specs_minelv_entry.get())
                            }
            config.mission_specs.add_groundstation_from_dict(gs_info_dict)
            logger.info("Ground station added.")

        ttk.Button(gs_add_by_entry_frame, text="Add GS", command=add_gs).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(gs_add_by_entry_frame, text="ID").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        gs_specs_gsid_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_gsid_entry.insert(0,random.randint(0,100))
        gs_specs_gsid_entry.bind("<FocusIn>", lambda args: gs_specs_gsid_entry.delete('0', 'end'))
        gs_specs_gsid_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Name").grid(row=2, column=0, sticky='w', padx=10, pady=10)
        gs_specs_name_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_name_entry.insert(0,'GreenSpinach')
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
        gs_specs_alt_entry.insert(0,10)
        gs_specs_alt_entry.bind("<FocusIn>", lambda args: gs_specs_alt_entry.delete('0', 'end'))
        gs_specs_alt_entry.grid(row=5, column=1, sticky='w')

        ttk.Label(gs_add_by_entry_frame, text="Min Elevation [deg]").grid(row=6, column=0, sticky='w', padx=10, pady=10)
        gs_specs_minelv_entry = ttk.Entry(gs_add_by_entry_frame, width=10)
        gs_specs_minelv_entry.insert(0,7)
        gs_specs_minelv_entry.bind("<FocusIn>", lambda args: gs_specs_minelv_entry.delete('0', 'end'))
        gs_specs_minelv_entry.grid(row=6, column=1, sticky='w')

        gs_specs_type_rbtn_2 = ttk.Radiobutton(gs_add_by_datafile_frame, text="Data file", command=gs_specs_rbtn_click,
                            variable=self._gs_specs_type, value="DataFile")
        gs_specs_type_rbtn_2.grid(row=0, column=0, padx=10, pady=5)

        def click_gs_data_file_path_btn():
            self.gs_data_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the ground-station data file:", filetypes=(("All files","*.*"), ("JSON files","*.json")))  
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
                pass           
            if self._gs_specs_type.get() == "DataFile":
                with open(self.gs_data_fp, 'r') as f:
                    specs = json.load(f)            
                config.mission_specs.add_groundstation_from_dict(specs)
                logger.info("Ground station(s) added from data-file.")
            gs_win.destroy()  
                            
        ok_btn = ttk.Button(okcancel_frame, text="Ok", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=gs_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)  
