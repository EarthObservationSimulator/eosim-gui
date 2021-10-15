from tkinter import ttk 
import tkinter as tk
from eosim.gui.visualize.insightsframe import InsightsFrame
from eosim.gui.visualize.vis2dframe import Vis2DFrame
from eosim.gui.visualize.vismapframe import VisMapFrame
from eosim.gui.visualize.visglobeframe import VisGlobeFrame

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='sans-serif') 
matplotlib.rc('font', serif='Times New Roman') 
matplotlib.rc('text', usetex='false') 
matplotlib.rcParams.update({'font.size': 12})

import logging

logger = logging.getLogger(__name__)

class VisualizeFrame(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)        

        # define the visualization frame
        vis_frame = ttk.Frame(self) 
        vis_frame.grid(row=0, column=0, sticky='nswe')
        vis_frame.rowconfigure(0,weight=1)
        vis_frame.columnconfigure(0,weight=1)

        tabControl = ttk.Notebook(vis_frame)
        
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        tab4 = ttk.Frame(tabControl)
              
        tabControl.add(tab2, text='2D Plot visualization')
        tabControl.add(tab3, text='Map visualization')
        tabControl.add(tab4, text='Globe visualization')
        tabControl.add(tab1, text='Insights')  # TODO: Shift to top when the functionality has been added.

        tabControl.pack(expand = True, fill ="both")   

        InsightsFrame(vis_frame, tab1)
        Vis2DFrame(vis_frame, tab2)
        VisMapFrame(vis_frame, tab3)
        VisGlobeFrame(vis_frame, tab4)

