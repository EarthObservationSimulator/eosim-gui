import json
import os
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
from eos.config import OutputConfig
import copy
import datetime
import pandas as pd
import numpy as np
from eos import config
import instrupy
import pandas as pd
import numpy as np
import tkinter
from tkinter import ttk 
import logging

logger = logging.getLogger(__name__)

class VisGlobeFrame(ttk.Frame):    

    def __init__(self, win, tab):
        vis_globe_frame = ttk.Frame(tab)
        vis_globe_frame.pack(expand = True, fill ="both", padx=10, pady=10)
        vis_globe_frame.rowconfigure(0,weight=1)
        vis_globe_frame.columnconfigure(0,weight=1)
        vis_globe_frame.columnconfigure(1,weight=1)  

        vis_globe_time_frame = ttk.LabelFrame(vis_globe_frame, text='Set Time Interval', labelanchor='n')
        vis_globe_time_frame.grid(row=0, column=0, sticky='nswe', padx=(10,10))
        vis_globe_time_frame.rowconfigure(0,weight=1)
        vis_globe_time_frame.rowconfigure(1,weight=1)
        vis_globe_time_frame.rowconfigure(2,weight=1)
        vis_globe_time_frame.columnconfigure(0,weight=1)
        vis_globe_time_frame.columnconfigure(1,weight=1)

        vis_globe_plot_frame = ttk.LabelFrame(vis_globe_frame, text='Cesium powered 3D Visualiation', labelanchor='n')
        vis_globe_plot_frame.grid(row=0, column=1, sticky='nswe', padx=(10,10))

        # time interval frame
        ttk.Label(vis_globe_time_frame, text="Time (hh:mm:ss) from mission-epoch", wraplength="110", justify='center').grid(row=0, column=0,columnspan=2,ipady=5)
        ttk.Label(vis_globe_time_frame, text="From").grid(row=1, column=0, sticky='ne')

        self.vis_globe_time_from_entry = ttk.Entry(vis_globe_time_frame, width=10, takefocus = False)
        self.vis_globe_time_from_entry.grid(row=1, column=1, sticky='nw', padx=10)
        self.vis_globe_time_from_entry.insert(0,'00:00:00')
        self.vis_globe_time_from_entry.bind("<FocusIn>", lambda args: self.vis_globe_time_from_entry.delete('0', 'end'))
        
        ttk.Label(vis_globe_time_frame, text="To").grid(row=2, column=0, sticky='ne')
        self.vis_globe_time_to_entry = ttk.Entry(vis_globe_time_frame, width=10, takefocus = False)
        self.vis_globe_time_to_entry.grid(row=2, column=1, sticky='nw', padx=10)
        self.vis_globe_time_to_entry.insert(0,'10:00:00')
        self.vis_globe_time_to_entry.bind("<FocusIn>", lambda args: self.vis_globe_time_to_entry.delete('0', 'end'))

        # plot frame
        ttk.Button(vis_globe_plot_frame, text="Launch", command=self.click_launch).pack(padx=10, pady=10, ipadx=10, ipady=10, expand=True)

    def click_launch(self):
        ''' Make CZML file execute the cesium engine '''

        user_dir = os.getcwd() + '/'
        curdir = os.path.dirname(__file__) + '/'

        # make the clock packet
        with open(curdir+"clock_template.json", 'r') as f:
            clk_pkt_template = json.load(f) 
        
        # read the epoch in Gregorian UTC and duration in days from the MissionSpecs.json
        with open(user_dir + "MissionSpecs.json", 'r') as f:
            miss_specs = json.load(f) 
        _e = str(miss_specs["epoch"]).split(",")
        epoch = datetime.datetime(int(_e[0]), int(_e[1]), int(_e[2]), int(_e[3]), int(_e[4]), int(_e[5]))

        duration_s =  float(miss_specs["duration"]) * 86400
        end_date = epoch + datetime.timedelta(0,int(duration_s)) 

        clk_pkt = copy.deepcopy(clk_pkt_template)
        clk_pkt["clock"]["interval"] = str(epoch.isoformat())+"/"+str(end_date.isoformat())
        clk_pkt["clock"]["currentTime"] = epoch.isoformat()

        czml_pkts = [] # list of packets
        czml_pkts.append(clk_pkt)

        # make the satellite packets
        with open(curdir+"satellite_template.json", 'r') as f:
            sat_pkt_template = json.load(f) 

        sat_id = config.out_config.get_satellite_ids()  
        sat_state_fp = config.out_config.get_satellite_state_fp()

        for k in range(0,len(sat_id)):
            step_size = pd.read_csv(sat_state_fp[k], skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
            step_size = float(step_size[0][0].split()[4])

            sat_state_df = pd.read_csv(sat_state_fp[k],skiprows = [0,1,2,3]) 
            sat_state_df = sat_state_df[['TimeIndex','X[km]','Y[km]','Z[km]']]
            sat_state_df['Time[s]'] = np.array(sat_state_df['TimeIndex']) * step_size
            sat_state_df['X[m]'] = np.array(sat_state_df['X[km]']) * 1000
            sat_state_df['Y[m]'] = np.array(sat_state_df['Y[km]']) * 1000
            sat_state_df['Z[m]'] = np.array(sat_state_df['Z[km]']) * 1000
            sat_state_df = sat_state_df[['Time[s]','X[m]','Y[m]','Z[m]']]

            _sat_pkt = copy.deepcopy(sat_pkt_template)
            _sat_pkt["id"] = sat_id[k]
            _sat_pkt["name"] = "Sat"+_sat_pkt["id"]
            _sat_pkt["label"]["text"] = _sat_pkt["name"]
            _sat_pkt["position"]["epoch"] = epoch.isoformat()
            _sat_pkt["position"]["cartesian"] = sat_state_df.values.flatten().tolist()

            czml_pkts.append(_sat_pkt)

        # write the CZML data file
        cesium_data_dir = curdir+"../../../cesium_app/Source/SampleData/"
        with open(cesium_data_dir+"eos_data.json", 'w') as f: # TODO change the directory where the CZML file is stored
            json.dump(czml_pkts, f, indent=4)
        # rename file to czml extension
        os.rename(cesium_data_dir+'eos_data.json', cesium_data_dir+'eos_data.czml')

        
        # Execute the cesium app

        def start_webserver():
            web_dir = os.path.join(os.path.dirname(__file__), '../../../cesium_app/')
            os.chdir(web_dir)

            httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
            httpd.serve_forever()

        # start webserver
        threading.Thread(target=start_webserver).start()

        time.sleep(1) # allow enough time for the server to start

        webbrowser.open('http://localhost:8080/', new=2) # open webbrowser
       

