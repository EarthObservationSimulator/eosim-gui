from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
from eos import config
import logging

logger = logging.getLogger(__name__)
class InsightsFrame(ttk.Frame):

    def __init__(self, win, tab):        
        insights_frame = ttk.Frame(tab)
        insights_frame.pack(expand = True, fill ="both", padx=10, pady=10)
        insights_frame.columnconfigure(0,weight=1)
        insights_frame.rowconfigure(0,weight=5)
        insights_frame.rowconfigure(1,weight=1)

        insights = tk.scrolledtext.ScrolledText(insights_frame, wrap='word', height=10, width=50, background='#A7E8C5', selectbackground='yellow', selectforeground='black')
        insights.grid(row=0, column=0, sticky='nsew')
        content = "Coverage percentage = \n average revisit period =\n, max revisit period =  \n Which ground-station received maximum contact times? \n Which region receives max coverage? \n Which satellite has maximum coverage? \n, etc."
        insights.insert("end", content)
        insights.configure(state ='disabled') # Making the text read only 

        ttk.Button(insights_frame, text="Export").grid(row=1, column=0)