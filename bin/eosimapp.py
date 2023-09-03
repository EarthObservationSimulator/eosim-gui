import tkinter as tk
from tkinter import messagebox
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from eosim.gui.mainapplication import MainApplication
import argparse
import logging

def main(loglevel):         

    current_directory = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(current_directory, '../cesium_app/')
    examples_dir = os.path.join(current_directory, '../examples')

    # Start web server in the cesium_app directory (which contains the `index.html` file which then references the eosimApp.js script).
    httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    def start_webserver():        
        os.chdir(web_dir)      
        print("server starting")
        httpd.serve_forever()
    threading.Thread(target=start_webserver).start() # creating a thread so that the GUI doesn't freeze.
    
    os.chdir(examples_dir) # change directory to examples
    root = tk.Tk()
    root.resizable(False, False)
    MainApplication(root, loglevel)
    
    # define what to do on closing window
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            setattr(httpd, '_BaseServer__shutdown_request', True) # shutown server
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Earth Observation Simulator (EOSim)'
    )
    parser.add_argument(
        '-loglevel',
        default="INFO",
        type=str,
        help="Logging level: Specify CRITICAL or ERROR or WARNING or INFO or DEBUG."
    )   

    args = parser.parse_args()
    if(args.loglevel=='CRITICAL'):
        loglevel = logging.CRITICAL
    elif(args.loglevel=='ERROR'):
        loglevel = logging.ERROR
    elif(args.loglevel=='WARNING'):
        loglevel = logging.WARNING
    elif(args.loglevel=='INFO'):
        loglevel = logging.INFO
    elif(args.loglevel=='DEBUG'):
        loglevel = logging.DEBUG

    main(loglevel)