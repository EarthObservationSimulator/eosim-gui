import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os

help_win = None

def on_closing():
    global help_win
    help_win.destroy()
    help_win = None
    

def click_help():
    ''' Make a new help window '''
    global help_win
    help_win = tk.Toplevel()
    help_win.geometry("500x400") 
    help_win.title("Help Window") 
    help_win.protocol("WM_DELETE_WINDOW", on_closing)

def help_window_update(event):
    global help_win
    if(help_win is not None):
        ttk.Label(help_win, text=event.widget).pack()
    else:
        print("help win does not exist")