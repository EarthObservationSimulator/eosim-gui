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
import pickle
import tkinter
from tkinter import ttk 
from eos import config
import logging

logger = logging.getLogger(__name__)

class VisGlobeFrame(ttk.Frame):    

    def __init__(self, win, tab):

        self.http_server_started = False
        

        vis_globe_frame = ttk.Frame(tab)
        vis_globe_frame.pack(expand = True, fill ="both", padx=10, pady=10)
        vis_globe_frame.rowconfigure(0,weight=1)
        vis_globe_frame.columnconfigure(0,weight=1)


        vis_globe_plot_frame = ttk.LabelFrame(vis_globe_frame, text='Cesium powered 3D Visualiation', labelanchor='n')
        vis_globe_plot_frame.grid(row=0, column=0, sticky='nswe', padx=(10,10))

         # plot frame
        ttk.Button(vis_globe_plot_frame, text="Launch", command=self.click_launch).pack(padx=10, pady=10, ipadx=10, ipady=10, expand=True)

    
    def click_launch(self):
        ''' Make CZML file execute the cesium engine '''

        user_dir = config.out_config.get_user_dir()
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
        clk_pkt["clock"]["interval"] = str(epoch.isoformat())+ 'Z'+"/"+str(end_date.isoformat()) + 'Z' #TODO: check Z
        clk_pkt["clock"]["currentTime"] = epoch.isoformat() + 'Z' #TODO: check Z

        czml_pkts = [] # list of packets
        czml_pkts.append(clk_pkt)

        # make the ground-station packets
        with open(curdir+"ground_station_template.json", 'r') as f:
            gndstn_pkt_template = json.load(f)
        
        # get list of ground-stations
        with open(user_dir+ 'comm_param.p', 'rb') as f:
            comm_dir = pickle.load(f)
            gnd_stn_fl = pickle.load(f)
            ground_stn_info = pickle.load(f)
        if(gnd_stn_fl):
            self.gnd_stn_specs = pd.read_csv(gnd_stn_fl, header=0, delimiter=r",")  
        elif(ground_stn_info):
            self.gnd_stn_specs = pd.DataFrame(ground_stn_info)
        else:
            self.gnd_stn_specs = None
        
        if self.gnd_stn_specs is not None:
            for index, row in self.gnd_stn_specs.iterrows():
                _pkt = copy.deepcopy(gndstn_pkt_template)
                _pkt["id"] = row["index"]
                _pkt["name"] = row["name"]
                _pkt["label"]["text"] = row["name"]
                _pkt["position"] = {}
                _pkt["position"]["cartographicDegrees"] = [row["lon[deg]"], row["lat[deg]"], row["alt[km]"]*1e3]
                czml_pkts.append(_pkt)

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
            num_time_indices = len(sat_state_df['TimeIndex']) # TODO: move this elsewhere out of loop
            sat_state_df['Time[s]'] = np.array(sat_state_df['TimeIndex']) * step_size
            sat_state_df['X[m]'] = np.array(sat_state_df['X[km]']) * 1000
            sat_state_df['Y[m]'] = np.array(sat_state_df['Y[km]']) * 1000
            sat_state_df['Z[m]'] = np.array(sat_state_df['Z[km]']) * 1000
            sat_state_df = sat_state_df[['Time[s]','X[m]','Y[m]','Z[m]']]

            _sat_pkt = copy.deepcopy(sat_pkt_template)
            _sat_pkt["id"] = sat_id[k]
            _sat_pkt["name"] = "Sat"+_sat_pkt["id"]
            _sat_pkt["label"]["text"] = _sat_pkt["name"]
            _sat_pkt["position"]["epoch"] = epoch.isoformat() + 'Z' #TODO: check Z
            _sat_pkt["position"]["cartesian"] = sat_state_df.values.flatten().tolist()

            czml_pkts.append(_sat_pkt)
        
        # intersatellite comm packets
        with open(curdir+"contacts_template.json", 'r') as f:
            contacts_pkt = json.load(f)
        
        czml_pkts.append(contacts_pkt[0])

        intersatcomm = config.out_config.get_intersatcomm()        

        for _comm in intersatcomm: 
            sat1_id = _comm["sat1_id"]
            sat2_id = _comm["sat2_id"]
            contact_df = pd.read_csv(_comm["concise_fl"], skiprows=[0,1])
            contacts = []
            is_first_contact = True
            previous_row = False
            for index, row in contact_df.iterrows():
                
                if(is_first_contact):                    
                    if(row['AccessFromIndex']!=0): # interval of no contact during the beginning, add this to the contacts (with boolean = False)
                        time_from = epoch.isoformat() + 'Z' #TODO: check Z
                        time_to = (epoch + datetime.timedelta(0,int(row['AccessFromIndex'] * step_size))).isoformat() + 'Z' #TODO: check Z
                        interval = time_from + "/" + time_to
                        contacts.append({"interval":interval, "boolean":False})                   
                
                time_from = (epoch + datetime.timedelta(0,int(row['AccessFromIndex'] * step_size))).isoformat() + 'Z' #TODO: check Z
                time_to = (epoch + datetime.timedelta(0,int(row['AccessToIndex'] * step_size))).isoformat() + 'Z' #TODO: check Z
                interval = time_from + "/" + time_to
                contacts.append({"interval":interval, "boolean":True})

                if is_first_contact is False:
                    # attach a period of no-contact between the consecutive contact periods
                    time_from = (epoch + datetime.timedelta(0,int(previous_row['AccessToIndex'] * step_size))).isoformat() + 'Z' #TODO: check Z
                    time_to = (epoch + datetime.timedelta(0,int(row['AccessFromIndex'] * step_size))).isoformat() + 'Z' #TODO: check Z
                    interval = time_from + "/" + time_to
                    contacts.append({"interval":interval, "boolean":False})

                previous_row = row
                is_first_contact = False

            # check the time towards the end
            if contacts: # if any contacts exist
                if(previous_row['AccessToIndex']!=num_time_indices):
                    # attach a period of no-contact between the previous interval-end and end-of-simulation
                    time_from = (epoch + datetime.timedelta(0,int(previous_row['AccessToIndex'] * step_size))).isoformat() + 'Z' #TODO: check Z
                    time_to = (epoch + datetime.timedelta(0,num_time_indices * step_size)).isoformat() + 'Z' #TODO: check Z
                    interval = time_from + "/" + time_to
                    contacts.append({"interval":interval, "boolean":False})
                
            _pkt = copy.deepcopy(contacts_pkt[1])
            _pkt["id"] = str(sat1_id) + " to " + str(sat2_id) 
            _pkt["name"] = _pkt["id"]
            _pkt["polyline"]["show"] = contacts if bool(contacts) else False # no contacts throughout the mission case
            _pkt["polyline"]["positions"]["references"] = [sat1_id+"#position",sat2_id+"#position"]
            
            czml_pkts.append(_pkt)

        # write the CZML data file
        cesium_data_dir = curdir+"../../../cesium_app/Source/SampleData/"
        with open(cesium_data_dir+"eos_data.json", 'w') as f: # TODO change the directory where the CZML file is stored
            json.dump(czml_pkts, f, indent=4)
        # rename file to czml extension
        os.rename(cesium_data_dir+'eos_data.json', cesium_data_dir+'eos_data.czml')
        
        # Execute the cesium app
        def start_webserver():
            if(self.http_server_started is False):
                web_dir = os.path.join(os.path.dirname(__file__), '../../../cesium_app/')
                os.chdir(web_dir)          
                self.httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
                self.http_server_started = True
                self.httpd.serve_forever()
            else:
                pass

        # start webserver
        threading.Thread(target=start_webserver).start()

        time.sleep(1) # allow enough time for the server to start

        webbrowser.open('http://localhost:8080/', new=2) # open webbrowser
       

