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
        insights_frame.rowconfigure(0,weight=1)
        insights_frame.rowconfigure(1,weight=1)