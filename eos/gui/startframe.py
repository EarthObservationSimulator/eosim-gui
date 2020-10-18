import tkinter as tk
from tkinter import ttk 

class StartFrame(ttk.Frame):

    BTNWIDTH = 15

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)

        text = "Click on Config to define and start a new simulation, or click any option below to load a previous configuration."
        welcomenote = ttk.Label(self, text=text, wraplength=400, justify="center")
        welcomenote.grid(row=0, column=0, columnspan=3, pady=(20,10))        
        
        load_btn = ttk.Button(self, text="Load", width=StartFrame.BTNWIDTH)
        ex_btn = ttk.Button(self, text="Examples", width=StartFrame.BTNWIDTH)
        help_btn = ttk.Button(self, text="Help", width=StartFrame.BTNWIDTH)
        load_btn.grid(row=1, column=0)
        ex_btn.grid(row=1, column=1)
        help_btn.grid(row=1, column=2)

        recent_lbl = ttk.Label(self, text="Recent:", wraplength=400, justify="center")
        recent_lbl.grid(row=2, column=0, columnspan=3, pady=(20,30), padx=20, sticky='w')

        legend_lbl = ttk.Label(self, text="Legend:", wraplength=400, justify="center")
        legend_lbl.grid(row=3, column=0, columnspan=3, pady=(10,10), padx=20, sticky='w')
        