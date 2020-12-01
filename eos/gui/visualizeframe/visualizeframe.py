from tkinter import ttk 
import tkinter as tk
from eos.config import GuiStyle, MissionConfig
from eos import config
from eos.gui.visualizeframe.insightsframe import InsightsFrame
from eos.gui.visualizeframe.vis2dframe import Vis2DFrame
from eos.gui.visualizeframe.vismapframe import VisMapFrame
from eos.gui.visualizeframe.visglobeframe import VisGlobeFrame
import random
from tkinter import messagebox
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.public_library import Instrument
from instrupy.util import *
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util

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

        tabControl.add(tab1, text='Insights')
        tabControl.add(tab2, text='2D Plot visualization')
        tabControl.add(tab3, text='Map visualization')
        tabControl.add(tab4, text='Globe visualization')

        tabControl.pack(expand = True, fill ="both")   

        InsightsFrame(vis_frame, tab1)
        Vis2DFrame(vis_frame, tab2)
        VisMapFrame(vis_frame, tab3)
        VisGlobeFrame(vis_frame, tab4)

