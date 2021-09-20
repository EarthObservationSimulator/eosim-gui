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

class CfInterSatelliteComm():

    def click_intersatcomm_settings_btn(self):
        intersatcomm_settings_win = tk.Toplevel()
        intersatcomm_settings_win.rowconfigure(0,weight=1)
        intersatcomm_settings_win.rowconfigure(1,weight=1)
        intersatcomm_settings_win.rowconfigure(2,weight=1)
        intersatcomm_settings_win.columnconfigure(0,weight=1)

        intersatcomm_settings_frame = ttk.Frame(intersatcomm_settings_win)
        intersatcomm_settings_frame.grid(row=0, column=0, padx=20, pady=20)
        intersatcomm_settings_frame.bind('<Enter>',lambda event, widget_id="opaque_atmos_height": helpwindow.update_help_window(event, widget_id)) 

        okcancel_frame = ttk.Frame(intersatcomm_settings_win)
        okcancel_frame.grid(row=1, column=0, padx=20, pady=20)

        ttk.Label(intersatcomm_settings_frame, text="Opaque Atmosphere Height [km]").grid(row=0, column=0, sticky='w')
        opaque_atmos_height_entry = ttk.Entry(intersatcomm_settings_frame, width=6)
        opaque_atmos_height_entry.grid(row=0, column=1, padx=2, pady=2)
        opaque_atmos_height_entry.insert(0,30)
        opaque_atmos_height_entry.bind("<FocusIn>", lambda args: opaque_atmos_height_entry.delete('0', 'end'))

        # okcancel frame
        def ok_click():
            config.mission_specs.update_settings(opaque_atmos_height = float(opaque_atmos_height_entry.get()))
            logger.info("Updated opaque atmospheric height")
            intersatcomm_settings_win.destroy()

        ok_btn = ttk.Button(okcancel_frame, text="OK", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Cancel", command=intersatcomm_settings_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)
        
