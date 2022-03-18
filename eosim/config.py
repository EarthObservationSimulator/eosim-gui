from tkinter import ttk 
import os

from orbitpy.mission import Mission

import logging
logger = logging.getLogger(__name__)

""" A MissionConfig instance to be used to store the mission configuration. This 
    object is imported and referenced over all the EOSim modules and hence
    acts as a sort of global variable for the entire EOSim software.
"""
mission = Mission() 
class GuiStyle():
    main_win_width = 900
    main_win_height = int(main_win_width*9/21) # 21:9 aspect ratio
    main_window_geom = str(main_win_width)+"x"+str(main_win_height) 
    child_window_geom = "500x500"
    
    def __init__(self):     
        gui_style = ttk.Style()
        gui_style.configure('My.TButton', foreground='#334353')
        gui_style.configure('messagearea.TFrame', background='white',  relief='sunken')
        gui_style.configure('lsidebar.TFrame', background='light grey',  relief='groove')
        gui_style.configure('lsidebar.TButton')
        # Create style for the frames used within the help window
        gui_style.configure('helpHeading.TFrame', background='#87ceeb')
        gui_style.configure('helpHeading.Label', background='#87ceeb', foreground='white', font=('Times New Roman',18,'bold'))
        
        gui_style.configure('helpDescription.TFrame', background='white')
        gui_style.configure('helpDescription.Label', background='white', foreground='black', font=('Times New Roman',16))

        gui_style.configure('helpMoreHelp.TFrame', background='light grey') 
        gui_style.configure('helpMoreHelp.Label', background='light grey', foreground='dark blue', font=('Times New Roman',12))