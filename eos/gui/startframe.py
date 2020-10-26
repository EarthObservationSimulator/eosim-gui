import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
class StartFrame(ttk.Frame):

    BTNWIDTH = 15

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
        
        new_btn = ttk.Button(self, text="New", command=self.click_new_sim, width=StartFrame.BTNWIDTH)
        load_btn = ttk.Button(self, text="Load", width=StartFrame.BTNWIDTH)
        ex_btn = ttk.Button(self, text="Examples", width=StartFrame.BTNWIDTH)
        help_btn = ttk.Button(self, text="Help", width=StartFrame.BTNWIDTH)
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
        