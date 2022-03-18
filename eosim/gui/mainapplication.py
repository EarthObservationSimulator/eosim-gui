import tkinter as tk 
from tkinter import ttk 
from .welcomeframe import WelcomeFrame
from .configure.cfframe import ConfigureFrame
from .executeframe import ExecuteFrame 
from .visualize.visualizeframe import VisualizeFrame
from .operations.operationsframe import OperationsFrame

from eosim import config
import eosim.gui.helpwindow as helpwindow

import tkinter.scrolledtext
import os
import sys
import logging
import time
import json
import logging

logger = logging.getLogger(__name__)
class MainApplication:   

    def __init__(self, parent, loglevel=logging.INFO):
        parent.report_callback_exception = self.report_callback_exception
        self.parent = parent
        
        self.parent.title("Earth Observation Simulator")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        #self.parent.iconbitmap(True, dir_path+"/../../icon.ico")
        self.parent.geometry(config.GuiStyle.main_window_geom)    
               
        MainApplication.build_main_window(self, loglevel)      
        
        config.GuiStyle() # configure all the styles used in the GUI (shall affect the other modules too)        
        
    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        logging.error(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )

    def build_main_window(self, loglevel):
        """ This function configures the various frames within the self.parent (root) window."""

        TopMenuBar(self.parent)
        
        # create a parent frame to encompass all frames
        self.parent_frame = ttk.Frame(self.parent)
        self.parent_frame.grid(row=0, column=0, padx=10, pady=10)
        parent_frame_width = config.GuiStyle.main_win_width - 20
        parent_frame_height = config.GuiStyle.main_win_height - 20

        # parent window grid configure
        self.parent_frame.rowconfigure(0,weight=1)
        self.parent_frame.rowconfigure(1,weight=1)

        # left-sidebar frame
        # grid configure
        lsidebar = ttk.Frame(self.parent_frame, width=0.2*parent_frame_width,  height=0.9*parent_frame_height, style="lsidebar.TFrame")
        lsidebar.grid_propagate(0)
        lsidebar.grid(row=0, column=0, rowspan=2, sticky='nswe')
        lsidebar.columnconfigure(0,weight=1)
        lsidebar.rowconfigure(0,weight=1)
        lsidebar.rowconfigure(1,weight=1)
        lsidebar.rowconfigure(2,weight=1)
        lsidebar.rowconfigure(3,weight=1)
        lsidebar.rowconfigure(4,weight=1)
        lsidebar.rowconfigure(5,weight=8)
        
        welcome_btn = ttk.Button(lsidebar, text='WELCOME',command=lambda: self.show_frame("WelcomeFrame"), style="lsidebar.TButton")
        welcome_btn.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)
        welcome_btn.bind('<Enter>',lambda event, widget_id="welcome": helpwindow.update_help_window(event, widget_id))
        configure_btn = ttk.Button(lsidebar, text='CONFIGURE',command=lambda: self.show_frame("ConfigureFrame"), style="lsidebar.TButton")
        configure_btn.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)
        configure_btn.bind('<Enter>',lambda event, widget_id="configure": helpwindow.update_help_window(event, widget_id))
        execute_btn = ttk.Button(lsidebar, text='EXECUTE',command=lambda: self.show_frame("ExecuteFrame"), style="lsidebar.TButton") 
        execute_btn.grid(row=2, column=0, sticky='nswe', padx=5, pady=5)
        execute_btn.bind('<Enter>',lambda event, widget_id="execute": helpwindow.update_help_window(event, widget_id))
        visualize_btn = ttk.Button(lsidebar, text='VISUALIZE',command=lambda: self.show_frame("VisualizeFrame"), style="lsidebar.TButton") 
        visualize_btn.grid(row=3, column=0, sticky='nswe', padx=5, pady=5)
        visualize_btn.bind('<Enter>',lambda event, widget_id="visualize": helpwindow.update_help_window(event, widget_id))
        operations_btn = ttk.Button(lsidebar, text='OPERATIONS',command=lambda: self.show_frame("OperationsFrame"), style="lsidebar.TButton") 
        operations_btn.grid(row=4, column=0, sticky='nswe', padx=5, pady=5)            
        
        # message area frame
        # grid configure
        messagearea = ttk.Frame(self.parent_frame, width= 0.8*parent_frame_width, height=0.2*parent_frame_height, style ='messagearea.TFrame')
        messagearea.grid_propagate(0)
        messagearea.grid(row=1, column=1, columnspan=1, sticky='nswe')
        messagearea.columnconfigure(0,weight=1)
        messagearea.rowconfigure(0,weight=1)     
        messages = tk.scrolledtext.ScrolledText(messagearea)
        messages.grid(row=0, column=0, sticky='nsew')        
        messages.configure(state ='disabled') # Making the text read only 

        # redirect stdout, logging messages to messages ScrolledText widget
        sys.stdout = TextRedirector(messages, "stdout")
        sys.stderr = TextRedirector(messages, "stderr")
        logging.basicConfig(level=loglevel, handlers=[
                    logging.FileHandler("debug.log", 'w'),
                    logging.StreamHandler(stream=sys.stdout)
                    ])         

        
        logging.info("Application started at: "+ str(time.asctime()))

        # main content area
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = ttk.Frame(self.parent_frame, width=0.6*parent_frame_width, height=0.8*parent_frame_height)
        # grid configure
        container.grid_propagate(0)
        container.grid(row=0, column=1, sticky='nswe')
        container.columnconfigure(0,weight=1)
        container.rowconfigure(0,weight=1)

        self.frames = {}
        # put all of the pages in the same location;
        # the one on the top of the stacking order
        # will be the one that is visible.
        for F in (WelcomeFrame, ConfigureFrame, ExecuteFrame, VisualizeFrame, OperationsFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeFrame")  

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

def donothing():
    pass

def click_new_sim():  
    """ Configure the working directory where the MissionSpecs.json file, auxillary i/p files and the results are to be stored.

    """    
    sim_dir_path = tkinter.filedialog.askdirectory(initialdir=os.getcwd(), title="Please select an empty folder:")  
    config.mission.update_settings(outDir=sim_dir_path+"/")
    logger.info("New workspace directory selected.")

def open_sim():      
    """ Load a previously run simulation.

        .. todo:: Add checks to see if the any required auxillary files are present (grid files, ground-station i/p files, etc).
    """
    sim_dir_path = tkinter.filedialog.askdirectory(initialdir=os.getcwd(), title="Please select the simulation directory:")  
    
    try:
        with open(sim_dir_path+'/MissionSpecs.json') as f:
            mission_dict = json.load(f)
    except:
        logger.error('Selected directory does not contain the required MissionSpecs.json file.')
        mission_dict = None

    if mission_dict is not None:
        config.mission = config.mission.from_dict(mission_dict)
        config.mission.update_settings(outDir=sim_dir_path+"/") # as a precaution since the folder could be copied from elsewhere, update the output-directory specification.
        logger.info("Simulation loaded.")
        logger.warning("Incomplete mission specifications (e.g. missing propagator settings) shall be populated with default values.")
    else:
        config.mission.update_settings(outDir=sim_dir_path+"/")
        logger.info("Directory is treated as a new workspace.")
    return

def click_save():
    """ Save the mission configuration as a JSON file."""
    
    wdir = config.mission.settings.outDir
    if wdir is None:
        logger.info("Please select the workspace directory in the menubar by going to Sim->New.")
        return
    
    with open(wdir+'MissionSpecs.json', 'w', encoding='utf-8') as f:
        json.dump(config.mission.to_dict(), f, ensure_ascii=False, indent=4)
    logger.info("Mission configuration Saved.")
class TopMenuBar:
    
    def __init__(self, parent):
        self.parent = parent
        menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=click_new_sim)
        filemenu.add_command(label="Open", command=open_sim)
        filemenu.add_command(label="Save", command=click_save)
        filemenu.add_command(label="Save as...", command=donothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.parent.quit)
        menubar.add_cascade(label="Sim", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Window", command=lambda: helpwindow.click_help(parent))
        helpmenu.add_command(label="About...", command=donothing)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.parent.config(menu=menubar)

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.see("end")
        self.widget.insert("end",'\n')
        self.widget.configure(state="disabled")