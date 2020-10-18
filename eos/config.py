from tkinter import ttk 
import tkinter as tk


class GuiStyle():
    main_win_width = 900
    main_win_height = int(900*9/21)
    main_window_geom = "900x386" # 900 width, 21:9 aspect ratio
    child_window_geom = "500x500"
    
    def __init__(self):     
        gui_style = ttk.Style()
        gui_style.configure('My.TButton', foreground='#334353')
        gui_style.configure('helparea.TFrame', background='blue')
        gui_style.configure('messagearea.TFrame', background='white',  relief='sunken')
        gui_style.configure('statusbar.TFrame',background='yellow',  relief='sunken')  
