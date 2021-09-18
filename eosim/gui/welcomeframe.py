import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
import eosim.gui.helpwindow as helpwindow
from eosim import config
import logging

logger = logging.getLogger(__name__)
class WelcomeFrame(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        ''' REV_TEST
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        '''

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=2)
        self.rowconfigure(2,weight=2)

        welcomenote1 = ttk.Label(self, text="Welcome to the EOSIM Application!", wraplength=400, justify="center")
        welcomenote1.config(font=("Times", "30", "bold"))
        welcomenote1.grid(row=0, column=0, pady=(20,10))        
        

        text = "Click on Sim->New to define and start a new simulation, or click on Sim->Open to re-run a previous configuration."
        welcomenote2 = ttk.Label(self, text=text, wraplength=500, justify="left", font="Arial 12")
        welcomenote2.grid(row=1, column=0, pady=10) 

        text = "Navigate to the 'examples' folder if you wish to open an example"
        welcomenote3 = ttk.Label(self, text=text, wraplength=500, justify="left", font="Arial 12")
        welcomenote3.grid(row=2, column=0, pady=10)

        
        ''' REV_TEST
        new_btn = ttk.Button(self, text="New", command=self.click_new_sim, width=15)       
        new_btn.bind('<Enter>',lambda event, widget_id="new": helpwindow.update_help_window(event, widget_id)) 
        help_btn = ttk.Button(self, text="Help", width=15, command=lambda: helpwindow.click_help(self))
        help_btn.bind('<Enter>',lambda event, widget_id="main": helpwindow.update_help_window(event, widget_id))
        open_btn = ttk.Button(self, text="Open", width=15)
        open_btn.bind('<Enter>',lambda event, widget_id="open": helpwindow.update_help_window(event, widget_id))
        ex_btn = ttk.Button(self, text="Examples", width=15)
        
        new_btn.grid(row=1, column=0, ipady=30, pady=(20,30))
        open_btn.grid(row=1, column=1, ipady=30, pady=(20,30))
        ex_btn.grid(row=1, column=2, ipady=30, pady=(20,30))
        help_btn.grid(row=1, column=3, ipady=30, pady=(20,30))
        '''

    
    def click_new_sim(self):      
        sim_dir_path = tkinter.filedialog.askdirectory(initialdir=os.getcwd(), title="Please select an empty folder:")  
        config.out_config.set_user_dir(sim_dir_path+"/")



        
        