import tkinter as tk
from tkinter import ttk 
from eos.gui.common import TopMenuBar
import os

class MainApplication:
    def __init__(self, parent):
        self.parent = parent

        self.parent.title("Earth Observation Simulator")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.parent.iconbitmap(dir_path+"/../../icon.ico")
        self.win_width = 900 #int(0.75*self.parent.winfo_screenwidth()) (assume screen szie of 1280x720, use 21:9 ultrawide aspect ratio)
        self.win_height = int(900*9/21) #int(0.75*self.parent.winfo_screenheight())
        self.parent.geometry(str(self.win_width)+"x"+str(self.win_height))
       
        MainApplication.build_main_window(self)        
        
    def build_main_window(self):
                
        gui_style = ttk.Style()
        gui_style.configure('My.TButton', foreground='#334353')
        gui_style.configure('rightsidebar.TFrame', background='blue')
        gui_style.configure('messagearea.TFrame', background='white',  relief='sunken')
        gui_style.configure('statusbar.TFrame',background='yellow',  relief='sunken')

        TopMenuBar(self.parent)
        
        # left-sidebar
        lsidebar = ttk.Frame(self.parent, width=0.2*self.win_width,  height=0.9*self.win_height)
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
        
        configure_btn = ttk.Button(lsidebar, text='CONFIGURE')
        configure_btn.grid(row=0, column=0, sticky='nswe')
        propagate_btn = ttk.Button(lsidebar, text='PROPOGATE') 
        propagate_btn.grid(row=1, column=0, sticky='nswe')
        power_btn = ttk.Button(lsidebar, text='POWER') 
        power_btn.grid(row=2, column=0, sticky='nswe')
        gndstncon_btn = ttk.Button(lsidebar, text='GND CONTACTS') 
        gndstncon_btn.grid(row=3, column=0, sticky='nswe')
        isatcon_btn = ttk.Button(lsidebar, text='I-SAT CONTACTS') 
        isatcon_btn.grid(row=4, column=0, sticky='nswe')
        cov_btn = ttk.Button(lsidebar, text='COVERAGE') 
        cov_btn.grid(row=5, column=0, sticky='nswe')
        dataq_btn = ttk.Button(lsidebar, text='DATA Q') 
        dataq_btn.grid(row=6, column=0, sticky='nswe')
        synobs_btn = ttk.Button(lsidebar, text='SYN OBS') 
        synobs_btn.grid(row=7, column=0, sticky='nswe')       
        
        # right sidebar
        rsidebar = ttk.Frame(self.parent, width=0.2*self.win_width,  height=0.9*self.win_height, style ='rightsidebar.TFrame')
        rsidebar.grid_propagate(0)
        rsidebar.grid(row=0, column=2, rowspan=2,sticky='nswe')
        rsidebar.columnconfigure(0,weight=1)
        rsidebar.rowconfigure(0,weight=1)        

        # message area
        messagearea = ttk.Frame(self.parent, width= 0.6*self.win_width, height=0.2*self.win_height, style ='messagearea.TFrame')
        messagearea.grid_propagate(0)
        messagearea.grid(row=1, column=1, columnspan=1, sticky='nswe')
        messagearea.columnconfigure(0,weight=1)
        messagearea.rowconfigure(0,weight=1)

        # status
        statusarea = ttk.Frame(self.parent, width= self.win_width, style ='statusbar.TFrame')
        statusarea.grid_propagate(0)
        statusarea.grid(row=2, column=0, columnspan=3, sticky='nswe')
        statusarea.columnconfigure(0,weight=1)
        statusarea.rowconfigure(0,weight=1)
        l1 = ttk.Label(statusarea, text="status", relief='sunken')
        l1.pack(anchor='w',  fill='both')      

        # main content area
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = ttk.Frame(self.parent, width=0.6*self.win_width, height=0.7*self.win_height)
        container.grid_propagate(0)
        container.grid(row=0, column=1, sticky='nswe')
        container.columnconfigure(0,weight=1)
        container.rowconfigure(0,weight=1)

        self.frames = {}
        # put all of the pages in the same location;
        # the one on the top of the stacking order
        # will be the one that is visible.
        for F in (Start, Configure):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Start")  

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class Start(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text="This is the start page")
        label.pack()

        button1 = ttk.Button(self, text="Go to Page One",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = ttk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        button2.pack()

class Configure(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text="This is the start page")
        label.pack()

        button1 = ttk.Button(self, text="Go to Page One",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = ttk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        button2.pack()
