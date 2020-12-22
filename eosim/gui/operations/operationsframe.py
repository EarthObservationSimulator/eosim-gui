import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import eosim.gui.helpwindow as helpwindow
from eosim import config
from eosim.gui.visualizeframe.visglobeframe import VisGlobeFrame
from eosim.gui.mapprojections import Mercator, EquidistantConic, LambertConformal, Robinson, LambertAzimuthalEqualArea, Gnomonic
from orbitpy.util import EnumEntity
import pandas as pd
import json
import datetime
import numpy as np
import pandas as pd
import time
import copy
import uuid
import logging
logger = logging.getLogger(__name__)

class CommandType(EnumEntity):
    """Enumeration of recoginized command types."""
    TAKEIMAGE = "TAKEIMAGE",
    TRANSMITDATA = "TRANSMITDATA",
    SETTINGS = "SETTINGS"

class MissionEntityType(EnumEntity):
    """Enumeration of recoginized command types."""
    SATELLITE = "SATELLITE",
    GROUNDSTATION = "GROUNDSTATION"

class OperationsFrame(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

        self.commands = list() # initialize list of dictionaries to store user supplied commands
        self.operations = list() # initialize list of dictionaries to store mission-operations (processed user-supplied commands)

        # operations schedule frame
        opschedule_frame = ttk.LabelFrame(self, text="Command", labelanchor='n') 
        opschedule_frame.grid(row=0, column=0, ipadx=20, ipady=20, sticky='nsew')
        opschedule_frame.rowconfigure(0,weight=1)
        opschedule_frame.rowconfigure(1,weight=6)
        opschedule_frame.rowconfigure(2,weight=1)
        opschedule_frame.columnconfigure(0,weight=1)

        obssyn_frame = ttk.LabelFrame(opschedule_frame, text="Synthesize Observations", labelanchor='n') 
        obssyn_frame.grid(row=1, column=0, padx=20, pady=20)

        progress_bar = ttk.Progressbar(opschedule_frame, orient='horizontal', length=300, mode='indeterminate')
        progress_bar.grid(row=2, column=0, padx=20, pady=20, sticky='s')

        # operations visualization frame
        opvisz_frame = ttk.LabelFrame(self, text="Operations Visualization", labelanchor='n') 
        opvisz_frame.grid(row=0, column=1, rowspan=2, ipadx=20, ipady=20, sticky='nsew')
        opvisz_frame.rowconfigure(0,weight=1)
        opvisz_frame.columnconfigure(0,weight=1)
        
        # define the widgets in the opschedule_frame
        tk.Button(opschedule_frame, text="Upload Command File", wraplength=100, width=15, command=self.click_select_command_file).grid(row=0, column=0, pady=20)
        
        # define the widgets in the opexec_frame
        ttk.Button(obssyn_frame, text="Select", state='disabled').grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(obssyn_frame, text="Execute", command=self.click_synobs_plot_btn).grid(row=0, column=1, padx=10, pady=10)
        

        # define widgets for the opvisz_frame
        tabControl = ttk.Notebook(opvisz_frame)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='3D Globe')
        tabControl.add(tab2, text='Synthetic Observations')

        tabControl.pack(expand = True, fill ="both")   

        CesiumGlobeOperationsVisualizationFrame(opvisz_frame, tab1)
        SyntheticObservationsVisualizationFrame(opvisz_frame, tab2)

    def click_synobs_plot_btn(self):
        pass
    
    def click_select_command_file(self):
        # reinitialize operations
        self.operations = list()
        # read in command data
        cmdfile_fp = None
        cmdfile_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the command file:", filetypes=(("All files","*.*"),("json files","*.json")))
        if cmdfile_fp != '':
            with open(cmdfile_fp) as f:
                self.commands = json.load(f)  
            logger.info("Command file successfully is read.")
        
        # build the operations.json file
        #       
        # iterate through the command packets
        for cmd in self.commands:
            cmd_typ = CommandType.get(cmd['@type'])  
            if(cmd_typ==CommandType.TRANSMITDATA):
                # TODO: validate that contact is indeed possible
                self.operations.append(cmd)
            elif(cmd_typ==CommandType.TAKEIMAGE):
                # TODO: validate that observation is indeed possible
                self.operations.append(cmd)

        # write the operations.json file
        user_dir = config.out_config.get_user_dir()
        with open(user_dir+'operations.json', 'w', encoding='utf-8') as f:
            json.dump(self.operations, f, ensure_ascii=False, indent=4)
        logger.info("Operations updated.")
        
class CesiumGlobeOperationsVisualizationFrame:
    def __init__(self, win, tab):

        globe_visz_frame = ttk.Frame(tab)
        globe_visz_frame.pack( expand=True) 

        self.http_server_started = False

        tk.Button(globe_visz_frame, text="Launch \n (Cesium powered Globe visualization)", wraplength=150, width=20, command=self.click_launch_globe_visz).pack(padx=10, pady=10, ipadx=10, ipady=10, expand=True)

    def click_launch_globe_visz(self):

        user_dir = config.out_config.get_user_dir()
        czml_template_dir = os.path.dirname(__file__) + "/../visualizeframe/"
        
        [epoch, step_size, num_time_indices, czml_pkts] = VisGlobeFrame.build_czmlpkts_for_mission_background(user_dir, czml_template_dir)

        _czml_pkts = CesiumGlobeOperationsVisualizationFrame.build_czmlpkts_for_operational_contacts(user_dir, czml_template_dir, epoch, step_size, num_time_indices)
        czml_pkts.extend(_czml_pkts)

        cesium_data_dir = os.path.dirname(__file__) + "/../../../cesium_app/Source/SampleData/"        
        self.execute_cesium_engine(cesium_data_dir, czml_pkts)       

    @staticmethod
    def build_czmlpkts_for_operational_contacts(user_dir, czml_template_dir, epoch, step_size, num_time_indices):
        
        with open(user_dir+"operations.json", 'r') as f:
            operations = json.load(f)

        czml_pkts = []

        # observed powition packet
        with open(czml_template_dir+"observed_gp_template.json", 'r') as f:
            oberv_pkt = json.load(f)

        # ground-station, inter-satellite comm packets
        with open(czml_template_dir+"contacts_template.json", 'r') as f:
            contacts_pkt = json.load(f)
        
        contacts_pkt[0]["id"] = str(uuid.uuid4()) # TODO: Not sure if this parent packet is required
        czml_pkts.append(contacts_pkt[0])

        # initialize communication between every pair of entities to "no-contact". Note that these packets have to appear strictly before the packets showing the contacts.
        # between satellite and ground-station
        sat_out = config.out_config.get_satout()  
        time_from = epoch.isoformat() + 'Z' #TODO: check Z
        time_to = (epoch + datetime.timedelta(0,int(num_time_indices* step_size))).isoformat() + 'Z' #TODO: check Z
        mission_interval = time_from + "/" + time_to
        for _sat in sat_out: 
            sat_id = _sat["@id"]
            if _sat.get("GroundStationComm", None) is not None:
                for _gs in _sat["GroundStationComm"]:
                    groundstn_id = _gs["@id"]

                    _pkt = copy.deepcopy(contacts_pkt[1])
                    _pkt["id"] = str(sat_id) + "-to-" + str(groundstn_id) 
                    _pkt["name"] = _pkt["id"]
                    _pkt["polyline"]["show"] =  {"interval":mission_interval, "boolean":False} # initialization of no contacts throughout the mission case
                    _pkt["polyline"]["positions"]["references"] = [str(sat_id)+"#position",str(groundstn_id)+"#position"]                    
                    czml_pkts.append(_pkt)

        # between satellite and satellite
        for j in range(0,len(sat_out)):
            sat1_id = sat_out[j]["@id"]
            for k in range(j+1,len(sat_out)):                
                sat2_id = sat_out[k]["@id"]
                _pkt = copy.deepcopy(contacts_pkt[1])
                _pkt["id"] = str(sat1_id) + "-to-" + str(sat2_id) 
                _pkt["name"] = _pkt["id"]
                _pkt["polyline"]["show"] =  {"interval":mission_interval, "boolean":False}  # initialization of no contacts throughout the mission case
                _pkt["polyline"]["positions"]["references"] = [str(sat1_id)+"#position",str(sat2_id)+"#position"]
                czml_pkts.append(_pkt)

        # get the coverage grid file-path
        for oper in operations:
            if(CommandType.get(oper['@type']) == CommandType.SETTINGS):
                covgrid_fp = oper["covGridFilePath"]

        # iterate over each operation in the list of operations. If they correspond to ground-station communications or intersatellite communications,
        # make the corresponding czml packet
        for oper in operations:            
            if(CommandType.get(oper['@type']) == CommandType.TRANSMITDATA):                
                # TODO: Perform validation checks below
                if(MissionEntityType.get(oper["txEntityType"])==MissionEntityType.SATELLITE):
                    pass
                elif(MissionEntityType.get(oper["txEntityType"])==MissionEntityType.GROUNDSTATION):
                    pass

                if(MissionEntityType.get(oper["rxEntityType"])==MissionEntityType.SATELLITE):
                    pass
                elif(MissionEntityType.get(oper["rxEntityType"])==MissionEntityType.GROUNDSTATION):
                    pass

                tx_entity_id = oper["txEntityId"]
                rx_entity_id = oper["rxEntityId"]

                time_from = (epoch + datetime.timedelta(0,int(oper['timeIndexStart'] * step_size))).isoformat() + 'Z' #TODO: check Z
                time_to = (epoch + datetime.timedelta(0,int(oper['timeIndexEnd'] * step_size))).isoformat() + 'Z' #TODO: check Z
                interval = time_from + "/" + time_to
                contact = {"interval":interval, "boolean":True}

                _pkt = copy.deepcopy(contacts_pkt[1])
                _pkt["id"] = str(tx_entity_id) + "-to-" + str(rx_entity_id) 
                _pkt["name"] = _pkt["id"]
                _pkt["polyline"]["show"] = contact if bool(contact) else False # no (valid) contacts throughout the mission case
                _pkt["polyline"]["positions"]= [str(tx_entity_id)+"#position",str(rx_entity_id)+"#position"]                
                czml_pkts.append(_pkt)
            
            elif(CommandType.get(oper['@type']) == CommandType.TAKEIMAGE):

                time_from = (epoch + datetime.timedelta(0,int(oper['timeIndexStart'] * step_size))).isoformat() + 'Z' #TODO: check Z
                time_to = (epoch + datetime.timedelta(0,int(oper['timeIndexEnd'] * step_size))).isoformat() + 'Z' #TODO: check Z
                interval = time_from + "/" + time_to
                initialize_interval = {"interval":mission_interval, "boolean":False} # this is necessary, else the point is shown over entire mission interval 
                obs_interval = {"interval":interval, "boolean":True} 

                for obs_pos in oper["observedPosition"]["cartographicDegrees"]: # iterate over possibly multiple points seen over the same time-interval
                    _pkt = copy.deepcopy(oberv_pkt)
                    _pkt["id"] = "ObservedGroundPointSat" + str(oper["satelliteId"]) + "Instru" + str(oper["instrumentId"]) + str(time_from) # only one czml packet per (sat, instru, time-start)
                    _pkt["point"]["show"] = [initialize_interval, obs_interval]
                    _pkt["position"]["cartographicDegrees"]= obs_pos
                    czml_pkts.append(_pkt)

        return czml_pkts

    def execute_cesium_engine(self, cesium_data_dir, czml_pkts):
        # write the CZML data file        
        with open(cesium_data_dir+"eosim_data.json", 'w') as f: # TODO change the directory where the CZML file is stored
            json.dump(czml_pkts, f, indent=4)
        # rename file to czml extension
        os.rename(cesium_data_dir+'eosim_data.json', cesium_data_dir+'eosim_data.czml')
        
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

class SyntheticObservationsVisualizationFrame:
    def __init__(self, win, tab):

        synobsvis_frame = ttk.Frame(tab) 
        synobsvis_frame.pack(expand=True) # if grid was used and the child frames directly defined on 'tab', 
                                          # then the widgets within the child-frames cannot be aligned to the center for some unknown reason.

        synobsvis_choose_image_frame = ttk.Frame(synobsvis_frame)
        synobsvis_choose_image_frame.grid(row=0, column=0, sticky='nswe') 
        synobsvis_choose_image_frame.columnconfigure(0,weight=1)
        synobsvis_choose_image_frame.rowconfigure(0,weight=1)

        synobsvis_map_proj_frame = ttk.LabelFrame(synobsvis_frame, text='Set Map Projection', labelanchor='n')
        synobsvis_map_proj_frame.grid(row=1, column=0, sticky='nswe', padx=10)
        synobsvis_map_proj_frame.columnconfigure(0,weight=1)
        synobsvis_map_proj_frame.rowconfigure(0,weight=1)
        synobsvis_map_proj_frame.rowconfigure(1,weight=1)

        synobsvis_map_proj_type_frame = ttk.Frame(synobsvis_map_proj_frame)
        synobsvis_map_proj_type_frame.grid(row=0, column=0)       
        proj_specs_container = ttk.Frame(synobsvis_map_proj_frame)
        proj_specs_container.grid(row=1, column=0, sticky='nswe')
        proj_specs_container.columnconfigure(0,weight=1)
        proj_specs_container.rowconfigure(0,weight=1)

        proj_specs_container_frames = {}
        for F in (Mercator, EquidistantConic, LambertConformal,Robinson,LambertAzimuthalEqualArea,Gnomonic):
            page_name = F.__name__
            self._prj_typ_frame = F(parent=proj_specs_container, controller=self)
            proj_specs_container_frames[page_name] = self._prj_typ_frame
            self._prj_typ_frame.grid(row=0, column=0, sticky="nsew")
        self._prj_typ_frame = proj_specs_container_frames['Mercator'] # default projection type
        self._prj_typ_frame.tkraise()

        synobsvis_map_plot_frame = ttk.Frame(synobsvis_frame)
        synobsvis_map_plot_frame.grid(row=2, column=0, sticky='nswe') 
        synobsvis_map_plot_frame.columnconfigure(0,weight=1)
        synobsvis_map_plot_frame.columnconfigure(1,weight=1)
        synobsvis_map_plot_frame.columnconfigure(2,weight=1)
        synobsvis_map_plot_frame.rowconfigure(0,weight=1)

        ttk.Button(synobsvis_choose_image_frame, text="Choose images to plot").grid(row=0, column=0)
        
        # projection  
        PROJ_TYPES = ['Mercator', 'EquidistantConic', 'LambertConformal', 'Robinson', 'LambertAzimuthalEqualArea', 'Gnomonic']   
             
        self._proj_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._proj_type.set("Mercator") # initialize

        def proj_type_combobox_change(event=None):
            if self._proj_type.get() == "Mercator":
                self._prj_typ_frame = proj_specs_container_frames['Mercator']
            elif self._proj_type.get() == "EquidistantConic":
                self._prj_typ_frame = proj_specs_container_frames['EquidistantConic']
            elif self._proj_type.get() == "LambertConformal":
                self._prj_typ_frame = proj_specs_container_frames['LambertConformal']
            elif self._proj_type.get() == "Robinson":
                self._prj_typ_frame = proj_specs_container_frames['Robinson']
            elif self._proj_type.get() == "LambertAzimuthalEqualArea":
                self._prj_typ_frame = proj_specs_container_frames['LambertAzimuthalEqualArea']
            elif self._proj_type.get() == "Gnomonic":
                self._prj_typ_frame = proj_specs_container_frames['Gnomonic']
            self._prj_typ_frame.tkraise()

        projtype_combo_box = ttk.Combobox(synobsvis_map_proj_type_frame, 
                                        values=PROJ_TYPES, textvariable = self._proj_type, width=25)
        projtype_combo_box.current(0)
        projtype_combo_box.grid(row=0, column=0)
        projtype_combo_box.bind("<<ComboboxSelected>>", proj_type_combobox_change)
        
        # plot frame
        ttk.Checkbutton(synobsvis_map_plot_frame, text="Auto crop").grid(row=0, column=0)
        ttk.Button(synobsvis_map_plot_frame, text="Plot").grid(row=0, column=1, columnspan=2, padx=20)
    
    