import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
import json
import webbrowser
from PIL import ImageTk,Image

help_win = None

with open(os.path.dirname(os.path.realpath(__file__))+"/help/help_database.json", 'r') as help_db_file:
    help_db = json.load(help_db_file) 

def on_closing():
    global help_win
    help_win.destroy()
    help_win = None

def make_help_win_frames(win):
    win.rowconfigure(0,weight=2)
    win.rowconfigure(1,weight=8)
    win.rowconfigure(2,weight=1)
    win.columnconfigure(0,weight=1)

    heading_frame = ttk.Frame(win, style='helpHeading.TFrame')
    heading_frame.grid(row=0, column=0, sticky='nsew')

    desc_frame = ttk.Frame(win, style='helpDescription.TFrame')
    desc_frame.grid(row=1, column=0, sticky='nsew')

    morehelp_frame = ttk.Frame(win, style='helpMoreHelp.TFrame')
    morehelp_frame.grid(row=2, column=0, sticky='nsew')

    return [heading_frame, desc_frame, morehelp_frame]

def click_help(parent):
    ''' Make a new help window '''
    global help_win
    help_win = tk.Toplevel(parent)
    help_win.geometry("300x200") 
    help_win.title("Help Window") 
    help_win.protocol("WM_DELETE_WINDOW", on_closing)
    [heading_frame, desc_frame, morehelp_frame] = make_help_win_frames(help_win)    
    # insert the content
    update_help_window(None, "main")

def update_help_window(event, widget_id):
    
    img_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "help") + "/"

    global help_win
    if(help_win is None):
        return       
    [heading_frame, desc_frame, morehelp_frame] = make_help_win_frames(help_win)

    # load the help content into a dictinary
    help_content = help_db[widget_id]

    # heading area
    ttk.Label(heading_frame, text=help_content["heading"], style='helpHeading.Label').pack(expand=True)
    
    # description area    
    desc_frame.columnconfigure(0,weight=1)
    desc_frame.rowconfigure(0,weight=1)     
    desc = tk.scrolledtext.ScrolledText(desc_frame, wrap='word', height=10, width=50, selectbackground='yellow', selectforeground='black')
    desc.grid(row=0, column=0, sticky='nsew')
    
    desc.insert("end", "".join(help_content["description"]))
    
    if(help_content["images"] is not None and help_content["images"] is not False):
        global org_img # to prevent garbage collection
        global img # to prevent garbage collection
        org_img = Image.open(img_dir+help_content["images"][0])
        resized = org_img.resize((400,400),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(resized) # Keep a reference, prevent GC
        desc.image_create('end', image=img)

    desc.configure(state ='disabled') # Making the text read only     
    
    # more help area
    if(help_content["morehelp"] is not None and help_content["morehelp"] is not False):
        #ttk.Label(morehelp_frame, text=help_content["morehelp"], style='helpMoreHelp.Label').pack(expand=True)
        link = ttk.Label(morehelp_frame, text="More help", cursor="hand2", style="helpMoreHelp.Label")
        link.pack(expand=True)
        link.bind("<Button-1>", lambda event: webbrowser.open(help_content["morehelp"]))
    else:
        ttk.Label(morehelp_frame, text=None, style="helpMoreHelp.Label").pack(expand=True)
        
        

    