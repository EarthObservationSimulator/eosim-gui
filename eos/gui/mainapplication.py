import tkinter as tk 
from tkinter import ttk 
from .startframe import StartFrame
from .configureframe import ConfigureFrame
import os
from eos.config import GuiStyle
class MainApplication:   

    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Earth Observation Simulator")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.parent.iconbitmap(True, dir_path+"/../../icon.ico")
        self.parent.geometry(GuiStyle.main_window_geom)            
        MainApplication.build_main_window(self)      
        GuiStyle()
        
    def build_main_window(self):

        TopMenuBar(self.parent)
        
        # create a parent frame to encompass all frames
        self.parent_frame = ttk.Frame(self.parent)
        self.parent_frame.grid(row=0, column=0, padx=10, pady=10)
        parent_frame_width = GuiStyle.main_win_width - 20
        parent_frame_height = GuiStyle.main_win_height - 20

        # parent window grid configure
        self.parent_frame.rowconfigure(0,weight=1)
        self.parent_frame.rowconfigure(1,weight=1)

        # left-sidebar frame
        # grid configure
        lsidebar = ttk.Frame(self.parent_frame, width=0.2*parent_frame_width,  height=0.9*parent_frame_height)
        lsidebar.grid_propagate(0)
        lsidebar.grid(row=0, column=0, rowspan=2, sticky='nswe')
        lsidebar.columnconfigure(0,weight=1)
        lsidebar.rowconfigure(0,weight=1)
        lsidebar.rowconfigure(1,weight=1)
        lsidebar.rowconfigure(2,weight=1)
        lsidebar.rowconfigure(3,weight=1)
        lsidebar.rowconfigure(4,weight=1)
        lsidebar.rowconfigure(5,weight=1)
        lsidebar.rowconfigure(6,weight=1)
        lsidebar.rowconfigure(7,weight=1)
        lsidebar.rowconfigure(8,weight=1)
        
        welcome_btn = ttk.Button(lsidebar, text='WELCOME',command=lambda: self.show_frame("StartFrame"))
        welcome_btn.grid(row=0, column=0, sticky='nswe')
        configure_btn = ttk.Button(lsidebar, text='CONFIGURE',command=lambda: self.show_frame("ConfigureFrame"))
        configure_btn.grid(row=1, column=0, sticky='nswe')
        propagate_btn = ttk.Button(lsidebar, text='PROPAGATE',command=lambda: self.show_frame("PropogateFrame")) 
        propagate_btn.grid(row=2, column=0, sticky='nswe')
        power_btn = ttk.Button(lsidebar, text='POWER',command=lambda: self.show_frame("PowerFrame")) 
        power_btn.grid(row=3, column=0, sticky='nswe')
        gndstncon_btn = ttk.Button(lsidebar, text='GROUND STATION CONTACTS',command=lambda: self.show_frame("GndStnConFrame")) 
        gndstncon_btn.grid(row=4, column=0, sticky='nswe')
        isatcon_btn = ttk.Button(lsidebar, text='INTER-SATELLITE CONTACTS',command=lambda: self.show_frame("InterSatConFrame")) 
        isatcon_btn.grid(row=5, column=0, sticky='nswe')
        cov_btn = ttk.Button(lsidebar, text='COVERAGE',command=lambda: self.show_frame("CoverageFrame")) 
        cov_btn.grid(row=6, column=0, sticky='nswe')
        dataq_btn = ttk.Button(lsidebar, text='DATA QUALITY',command=lambda: self.show_frame("DataQFrame")) 
        dataq_btn.grid(row=7, column=0, sticky='nswe')
        synobs_btn = ttk.Button(lsidebar, text='SYNTHETIC OBSERVATIONS',command=lambda: self.show_frame("SynObsFrame")) 
        synobs_btn.grid(row=8, column=0, sticky='nswe')            

        # message area frame
        # grid configure
        messagearea = ttk.Frame(self.parent_frame, width= 0.8*parent_frame_width, height=0.2*parent_frame_height, style ='messagearea.TFrame')
        messagearea.grid_propagate(0)
        messagearea.grid(row=1, column=1, columnspan=1, sticky='nswe')
        messagearea.columnconfigure(0,weight=1)
        messagearea.rowconfigure(0,weight=1)     

        # main content area
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        # grid configure
        container = ttk.Frame(self.parent_frame, width=0.6*parent_frame_width, height=0.8*parent_frame_height)
        container.grid_propagate(0)
        container.grid(row=0, column=1, sticky='nswe')
        container.columnconfigure(0,weight=1)
        container.rowconfigure(0,weight=1)

        self.frames = {}
        # put all of the pages in the same location;
        # the one on the top of the stacking order
        # will be the one that is visible.
        for F in (StartFrame, ConfigureFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartFrame")  

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

def donothing():
    pass
class TopMenuBar:
    
    def __init__(self, parent):
        self.parent = parent
        menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=donothing)
        filemenu.add_command(label="Open", command=donothing)
        filemenu.add_command(label="Save", command=donothing)
        filemenu.add_command(label="Save as...", command=donothing)
        filemenu.add_command(label="Close", command=donothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.parent.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=donothing)

        editmenu.add_separator()

        editmenu.add_command(label="Cut", command=donothing)
        editmenu.add_command(label="Copy", command=donothing)
        editmenu.add_command(label="Paste", command=donothing)
        editmenu.add_command(label="Delete", command=donothing)
        editmenu.add_command(label="Select All", command=donothing)

        menubar.add_cascade(label="Edit", menu=editmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=donothing)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.parent.config(menu=menubar)

