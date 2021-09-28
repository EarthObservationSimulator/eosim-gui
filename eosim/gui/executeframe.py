from tkinter import ttk 
import tkinter as tk
from eosim.config import GuiStyle, MissionConfig, OutputConfig
from eosim import config
import json
import orbitpy
import tkinter.filedialog, tkinter.messagebox
from instrupy.util import *

#from orbitpy import orbitpropcov, communications, obsdatametrics, util REV_TEST
import threading
import time
import pickle
import copy

import logging

logger = logging.getLogger(__name__)

class ExecuteFrame(ttk.Frame):

    BTNWIDTH = 15

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)      
        self.columnconfigure(1,weight=1)    
        self.columnconfigure(2,weight=1) 

        # define propagation execution frame 
        pexec_frame = ttk.Frame(self) 
        pexec_frame.grid(row=0, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        pexec_frame.columnconfigure(0,weight=1)
        pexec_frame.rowconfigure(0,weight=1)

        covexec_frame = ttk.Frame(self) 
        covexec_frame.grid(row=0, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        covexec_frame.columnconfigure(0,weight=1)
        covexec_frame.rowconfigure(0,weight=1)

        gndconexec_frame = ttk.Frame(self) 
        gndconexec_frame.grid(row=0, column=2, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        gndconexec_frame.columnconfigure(0,weight=1)
        gndconexec_frame.rowconfigure(0,weight=1)

        sat2satconexec_frame = ttk.Frame(self) 
        sat2satconexec_frame.grid(row=1, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        sat2satconexec_frame.columnconfigure(0,weight=1)
        sat2satconexec_frame.rowconfigure(0,weight=1)

        obsmetcalcsexec_frame = ttk.Frame(self) 
        obsmetcalcsexec_frame.grid(row=1, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        obsmetcalcsexec_frame.columnconfigure(0,weight=1)
        obsmetcalcsexec_frame.rowconfigure(0,weight=1)

        eclipsefinderexec_frame = ttk.Frame(self) 
        eclipsefinderexec_frame.grid(row=1, column=2, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        eclipsefinderexec_frame.columnconfigure(0,weight=1)
        eclipsefinderexec_frame.rowconfigure(0,weight=1)

        progressbar_frame = ttk.Frame(self) 
        progressbar_frame.grid(row=2, column=0, columnspan=3, ipadx=10, ipady=10, padx=10, pady=10, sticky='nswe')
        progressbar_frame.columnconfigure(0,weight=1)
        progressbar_frame.rowconfigure(0,weight=1)

        # define the widgets inside the frames 
        progress_bar = ttk.Progressbar(progressbar_frame, orient='horizontal', length=300, mode='indeterminate')
        progress_bar.grid(row=0, column=0,  padx=20, sticky='n')

        pexec_btn = tk.Button(pexec_frame, text="Orbit Propagator", width=40, wraplength=100, command=lambda:self.click_pexec_btn(progress_bar))
        pexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')
        
        
        covexec_btn = tk.Button(covexec_frame, text="Coverage Calculator", width=40, wraplength=100, command=lambda:self.click_covexec_btn(progress_bar))
        covexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


        gndconexec_btn = tk.Button(gndconexec_frame, text="Ground-Station Contact Finder", width=40, wraplength=100, command=lambda:self.click_gndconexec_btn(progress_bar))
        gndconexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


        sat2satconexec_btn = tk.Button(sat2satconexec_frame, text="Sat-to-Sat Contact Finder", width=40, wraplength=100, command=lambda:self.click_sat2satconexec_btn(progress_bar))
        sat2satconexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


        obsmetcalcexec_btn = tk.Button(obsmetcalcsexec_frame, text="Data-metrics Calculator", width=40, wraplength=100, command=lambda:self.click_datametricsexec_btn(progress_bar))
        obsmetcalcexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')

        eclipsefinderexec_btn = tk.Button(eclipsefinderexec_frame, text="Eclipse Finder", width=40, wraplength=100, command=lambda:self.click_eclipsefinderexec_btn(progress_bar))
        eclipsefinderexec_btn.grid(row=0, column=0, padx=20, ipady=10, pady=5, sticky='s')


    def click_pexec_btn(self, progress_bar):

        def real_click_pexec_btn():
            progress_bar.start(10)
            logger.info(".......Running orbit propagation.......")
            start_time = time.time()
            config.mission.execute_propagation()
            logger.info(".......Done.......")     
            logger.info('TIme taken is %f secs.' %(time.time()-start_time))            

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_pexec_btn).start()

    
    def click_eclipsefinderexec_btn(self, progress_bar):

        def real_click_eclipsefinderexec_btn():
            progress_bar.start(10)
            logger.info(".......Running eclipse finder.......")
            start_time = time.time()
            config.mission.execute_eclipse_finder()
            logger.info(".......Done.......")     
            logger.info('TIme taken is %f secs.' %(time.time()-start_time))            

            progress_bar.stop()            

        # execute propagation
        threading.Thread(target=real_click_eclipsefinderexec_btn).start()

    def click_gndconexec_btn(self, progress_bar):
        
        def real_click_gndconexec_btn():
            progress_bar.start(10)
            logger.info(".......Running ground-station contact finder.......")
            start_time = time.time()
            config.mission.execute_groundstation_contact_finder()
            logger.info(".......Done.......")     
            logger.info('TIme taken is %f secs.' %(time.time()-start_time))            

            progress_bar.stop()            

        # execute ground-station contact finder
        threading.Thread(target=real_click_gndconexec_btn).start()

    def click_sat2satconexec_btn(self, progress_bar):
        
        def real_click_sat2satconexec_btn():
            progress_bar.start(10)
            logger.info(".......Running inter-satellite contact finder.......")
            start_time = time.time()
            config.mission.execute_intersatellite_contact_finder()
            logger.info(".......Done.......")     
            logger.info('TIme taken is %f secs.' %(time.time()-start_time))            

            progress_bar.stop()            

        # execute inter-satellite contact finder
        threading.Thread(target=real_click_sat2satconexec_btn).start()

    def click_covexec_btn(self, progress_bar):

        def real_click_covexec_btn():
            progress_bar.start(10)
            logger.info(".......Running coverage calculator.......")
            start_time = time.time()
            config.mission.execute_coverage_calculator()
            logger.info(".......Done.......")     
            logger.info('TIme taken is %f secs.' %(time.time()-start_time))            

            progress_bar.stop()            

        # execute coverage calculations
        threading.Thread(target=real_click_covexec_btn).start()

    def click_datametricsexec_btn(self, progress_bar):

        def real_click_datametricsexec_btn():
            progress_bar.start(10)
            logger.info(".......Running data metrics Calculator.......")
            start_time = time.time()
            config.mission.execute_datametrics_calculator()
            logger.info(".......Done.......")     
            logger.info('TIme taken is %f secs.' %(time.time()-start_time))            

            progress_bar.stop()            

        # execute datametrics calculation
        threading.Thread(target=real_click_datametricsexec_btn).start()

      
        

