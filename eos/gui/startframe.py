import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
import eos.gui.helpwindow as helpwindow
import logging

logger = logging.getLogger(__name__)
class StartFrame(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)

        text = "Click on New to define and start a new simulation, or click on Load to re-run a previous configuration."
        welcomenote = ttk.Label(self, text=text, wraplength=400, justify="center")
        welcomenote.grid(row=0, column=0, columnspan=4, pady=(20,10))        
        
        new_btn = ttk.Button(self, text="New", command=self.click_new_sim, width=15)       
        new_btn.bind('<Enter>',lambda event, widget_id="new": helpwindow.update_help_window(event, widget_id)) 
        help_btn = ttk.Button(self, text="Help", width=15, command=lambda: helpwindow.click_help(self))
        help_btn.bind('<Enter>',lambda event, widget_id="main": helpwindow.update_help_window(event, widget_id))
        load_btn = ttk.Button(self, text="Load", width=15)
        load_btn.bind('<Enter>',lambda event, widget_id="load": helpwindow.update_help_window(event, widget_id))
        ex_btn = ttk.Button(self, text="Examples", width=15)
        
        new_btn.grid(row=1, column=0)
        load_btn.grid(row=1, column=1)
        ex_btn.grid(row=1, column=2)
        help_btn.grid(row=1, column=3)

        recent_lbl = ttk.Label(self, text="Recent:", wraplength=400, justify="center")
        recent_lbl.grid(row=2, column=0, columnspan=4, pady=(20,30), padx=20, sticky='w')

        legend_lbl = ttk.Label(self, text="Legend:", wraplength=400, justify="center")
        legend_lbl.grid(row=3, column=0, columnspan=4, pady=(10,10), padx=20, sticky='w')
    
    def click_new_sim(self):      
        sim_dir_path = tkinter.filedialog.askdirectory(initialdir=os.getcwd(), title="Please select an empty folder:")  
        os.chdir(sim_dir_path) # set working directory
    


        
        