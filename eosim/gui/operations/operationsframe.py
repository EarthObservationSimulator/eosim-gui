""" 
.. module:: operationsframe

:synopsis: *Module to execute building of synthetic observations (visualization with plots) and 
            visualization of observation-locations in the CesiumJS globe.*

The module is named as 'operationsframe' since it is used to initiate computation and visualization of 'operations' of a satellite 
during the mission. Is consists of mainly two parts:
*   Initiating synthesization of satellite imagery, corresponding to times during the mission at which the observations are made.
*   Illustrating the operations on the CesiumJS globe. 

    Operations visualized on the CesiumJS are:

    *   TAKEIMAGE: Lights up the ground-location (a point) with a user-supplied color.
    *   TRANSMITDATA: Draws line b/w the communicating entities (sat/ground-station or sat/sat) during the time of communication.

The module differentiates between ‘commands’ and ‘operations’, in that commands are supplied by user, while operations are the ones 
actually executed by the spacecraft after seeing the validity of the commands. 
Currently though there are no validity checks performed and hence commands = operations.


"""

import tkinter as tk
import tkinter.filedialog
from tkinter import ttk 
import os
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from eosim import config
from eosim.gui.visualize.visglobeframe import VisGlobeFrame
from eosim.gui.mapprojections import Mercator, EquidistantConic, LambertConformal, Robinson, LambertAzimuthalEqualArea, Gnomonic
from orbitpy.util import EnumEntity
# from orbitpy.sensorfovprojection import SensorFOVProjection, PixelShapelyPolygon TODO REV_TEST
import pandas as pd
import json
import datetime
import numpy as np
import pandas as pd
import time
import copy
import uuid
import shutil
import pickle
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs

import logging
logger = logging.getLogger(__name__)

class CommandType(EnumEntity):
    """Enumeration of recognized command types."""
    TAKEIMAGE = "TAKEIMAGE",
    TRANSMITDATA = "TRANSMITDATA"
class MissionEntityType(EnumEntity):
    """Enumeration of recognized mission-entities types."""
    SPACECRAFT = "SPACECRAFT",
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
        command_frame = ttk.LabelFrame(self, text="Command", labelanchor='n') 
        command_frame.grid(row=0, column=0, ipadx=20, ipady=20, sticky='nsew')
        command_frame.rowconfigure(0,weight=1)
        command_frame.rowconfigure(1,weight=6)
        command_frame.rowconfigure(2,weight=1)
        command_frame.columnconfigure(0,weight=1)

        obssyn_frame = ttk.LabelFrame(command_frame, text="Synthesize Observations", labelanchor='n') 
        obssyn_frame.grid(row=1, column=0, padx=20, pady=20)

        progress_bar = ttk.Progressbar(command_frame, orient='horizontal', length=300, mode='indeterminate')
        progress_bar.grid(row=2, column=0, padx=20, pady=20, sticky='s')

        # operations visualization frame
        opvisz_frame = ttk.LabelFrame(self, text="Operations Visualization", labelanchor='n') 
        opvisz_frame.grid(row=0, column=1, rowspan=2, ipadx=20, ipady=20, sticky='nsew')
        opvisz_frame.rowconfigure(0,weight=1)
        opvisz_frame.columnconfigure(0,weight=1)
        
        # define the widgets in the command_frame
        tk.Button(command_frame, text="Upload Command File", wraplength=100, width=15, command=self.click_select_command_file).grid(row=0, column=0, pady=20)
        
        # define the widgets in the obssyn_frame
        ttk.Button(obssyn_frame, text="Select", state='disabled').grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(obssyn_frame, text="Execute", command=lambda:self.click_synobsexec_btn(progress_bar)).grid(row=0, column=1, padx=10, pady=10)
        
        # define widgets for the opvisz_frame
        tabControl = ttk.Notebook(opvisz_frame)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='3D Globe')
        tabControl.add(tab2, text='Synthetic Observations')

        tabControl.pack(expand = True, fill ="both")   

        CesiumGlobeOperationsVisualizationFrame(opvisz_frame, tab1)
        SyntheticObservationsVisualizationFrame(opvisz_frame, tab2)

    def click_select_command_file(self):
        """ Read in the user-supplied command-file which is a list of json packets, where each packet indicates a single satellite command."""
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
        user_dir = config.mission.settings.outDir
        with open(user_dir+'operations.json', 'w', encoding='utf-8') as f:
            json.dump(self.operations, f, ensure_ascii=False, indent=4)
        logger.info("Operations updated.")

    def click_synobsexec_btn(self, progress_bar):
        """ Synthesize the observations indicated in the operation file.
            NOT ACTIVE, NEEDS REVISION
        """

        def real_click_sat2satconexec_btn():
            user_dir = config.out_config.get_user_dir()
            with open(user_dir+"operations.json", 'r') as f:
                operations = json.load(f)
            
            # prepare synthetic data result dir
            syn_data_dir = user_dir+'synthetic_data/'
            config.out_config.update_syndatadir(syn_data_dir)
            if os.path.exists(syn_data_dir):
                shutil.rmtree(syn_data_dir)
            os.makedirs(syn_data_dir) 
            
            progress_bar.start(10)  
            for oper in operations:   
                if(CommandType.get(oper['@type']) == CommandType.TAKEIMAGE):

                    cmd_id = oper["@id"]
                    logger.info('Observation corresponding to command id ' + str(cmd_id))

                    # get the satellite state file and state corresponding to the middle to the imaging interval
                    sat_id = oper["spacecraftId"]
                    sat_state_fp = config.out_config.get_satellite_state_fp()[config.out_config.get_satellite_ids().index(sat_id)]

                    epoch_JDUT1 = pd.read_csv(sat_state_fp, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
                    epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[2])

                    step_size = pd.read_csv(sat_state_fp, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
                    step_size = float(step_size[0][0].split()[4])

                    imaging_time_index = int(oper["timeIndexStart"] + np.floor(0.5*(oper["timeIndexEnd"] - oper["timeIndexStart"])))

                    date_JDUt1 = epoch_JDUT1 + imaging_time_index*step_size/(24*3600)

                    sat_state_df = pd.read_csv(sat_state_fp,skiprows = [0,1,2,3]) 
                    sat_state_df.set_index('TimeIndex', inplace=True)
                    sat_state = sat_state_df.iloc[imaging_time_index]
                    state_eci = str(sat_state['X[km]']) + ","  + str(sat_state['Y[km]']) + ","  + str(sat_state['Z[km]']) + ","  + str(sat_state['VX[km/s]']) + ","  + str(sat_state['VY[km/s]']) + ","  + str(sat_state['VZ[km/s]'])

                    # get the satellite and instrument orientations
                    sat_orien = "1,2,3," + oper['satelliteOrientation'] # 1,2,3 indicate the euler sequence
                    sen_orien = "1,2,3," + oper['instrumentOrientation']

                    # get the instrument fov,pixel configuration
                    instru = config.miss_specs.get_sensor_specs(oper["instrumentId"])
                    #print(sensor_specs)
                    #instru = Instrument.from_dict(sensor_specs)

                    [angleHeight, angleWidth] = instru.get_fov().get_ATCT_fov() #TODO: check that angleHeight==ATFOV
                    [heightDetectors, widthDetectors] = instru.get_pixel_config()

                    # compute the pixel position data (center, edges, poles)
                    logger.info("...start computation of pixel positions...")
                    # TODO REV_TEST
                    # pixel_pos_data = SensorFOVProjection.get_pixel_position_data(user_dir, date_JDUt1, state_eci, sat_orien, sen_orien, angleWidth, angleHeight, heightDetectors, widthDetectors)
                    logger.info("...stop computation of pixel positions...")

                    # compute the pixel polygons
                    # TODO REV_TEST
                    # pixels = PixelShapelyPolygon(pixel_pos_data)
                    logger.info("...start computation of pixel polygons...")
                    [pixel_poly, pixel_center_pos] = pixels.make_all_pixel_polygon()
                    logger.info("...stop computation of pixel polygons...")

                    # compute the synthetic data from the instrument
                    logger.info("...start interpolation ...")
                    [pixel_center_pos, interpl_var_data, env_var] = instru.synthesize_observation(time_JDUT1=date_JDUt1, pixel_center_pos=pixel_center_pos)
                    logger.info("...stop interpolation...")

                    # store the results (pixel position data, shapely polygons, interpolated data) inside a pickle object with the name same as the cmd_id
                    syn_data_dir = config.out_config.get_syndatadir()
                    syndata_fp = syn_data_dir+"syndata_cmd" + str(cmd_id)+".p"
                    with open(syndata_fp, "wb") as f:
                        pickle.dump(env_var, f)
                        pickle.dump(pixel_poly, f)
                        pickle.dump(pixel_center_pos, f)
                        pickle.dump(interpl_var_data, f)
                    config.out_config.update_syndata(cmd_id, syndata_fp)
                    # update the output.json file inside user-dir
                    ocf = user_dir + 'output.json'
                    with open(ocf, 'w', encoding='utf-8') as f:
                        json.dump(config.out_config.to_dict(), f, ensure_ascii=False, indent=4)
            progress_bar.stop()
        
        logger.info('Start synthesize observations.')
        threading.Thread(target=real_click_sat2satconexec_btn).start()
        logger.info('Finished synthesizing observations.')        
class CesiumGlobeOperationsVisualizationFrame:
    def __init__(self, win, tab):

        globe_visz_frame = ttk.Frame(tab)
        globe_visz_frame.pack( expand=True) 

        tk.Button(globe_visz_frame, text="Launch \n (CesiumJS powered Globe visualization)", wraplength=150, width=20, command=self.click_launch_globe_visz).pack(padx=10, pady=10, ipadx=10, ipady=10, expand=True)

    def click_launch_globe_visz(self):

        czml_template_dir = os.path.dirname(__file__) + '/../visualize/czml_templates/'
        
        [epoch, step_size, num_time_indices, czml_pkts] = VisGlobeFrame.build_czmlpkts_for_mission_background(czml_template_dir)

        # TODO REV NOS DEMO
        #_czml_pkts = VisGlobeFrame.build_czmlpkts_for_ground_stn_contact_opportunities(czml_template_dir, epoch, step_size, num_time_indices)
        #czml_pkts.extend(_czml_pkts)
       
        # TODO REV NOS DEMO
        #_czml_pkts = VisGlobeFrame.build_czmlpkts_for_intersat_contact_opportunities(czml_template_dir, epoch, step_size, num_time_indices)
        #czml_pkts.extend(_czml_pkts)

        user_dir = config.mission.settings.outDir
        with open(user_dir+"operations.json", 'r') as f:
            operations = json.load(f)

        _czml_pkts = self.build_czmlpkts_for_operational_contacts(operations, czml_template_dir, epoch, step_size, num_time_indices)
        czml_pkts.extend(_czml_pkts)

        cesium_data_dir = os.path.dirname(__file__) + "/../../../cesium_app/Source/SampleData/"
         # write the CZML data file        
        with open(cesium_data_dir+"eosim_data.czml", 'w') as f:
            json.dump(czml_pkts, f, indent=4)
        # rename file to czml extension
        #os.rename(cesium_data_dir+'eosim_data.json', cesium_data_dir+'eosim_data.czml')

        self.execute_cesium_app()       
        
    def execute_cesium_app(self):      
        # Server already started  in the cesium_app directory by the `bin/eosimapp.py` script
        os.chdir(os.path.join(os.path.dirname(__file__), '../../../cesium_app')) # change directory to examples
        webbrowser.open('http://localhost:8080/', new=2) # open webbrowser

    @staticmethod
    def build_czmlpkts_for_operational_contacts(operations, czml_template_dir, epoch, step_size, num_time_indices):
        
        czml_pkts = []

        # observed position packet
        with open(czml_template_dir+"observed_gp_template.json", 'r') as f:
            observ_pkt = json.load(f)

        # ground-station, inter-satellite comm packets
        with open(czml_template_dir+"contacts_template.json", 'r') as f:
            contacts_pkt = json.load(f)
        
        contacts_pkt[0]["id"] = str(uuid.uuid4()) # TODO: Not sure if this parent packet is required
        czml_pkts.append(contacts_pkt[0])

        miss_time_from = epoch.isoformat() + 'Z'
        miss_time_to = (epoch + datetime.timedelta(0,int(num_time_indices* step_size))).isoformat() + 'Z'
        mission_interval = miss_time_from + "/" + miss_time_to

        # initialize communication between every pair of entities to "no-contact". 
        # Note that these packets have to appear strictly before the packets showing the contacts.
        
        # satellite with ground-station        
        satellites = config.mission.spacecraft # list of orbitpy.util.Spacecraft objects in the mission
        ground_station = config.mission.groundStation # list of orbitpy.util.GroundStation objects in the mission

        sat_with_gs_comm_ids = []
        if satellites:
            if ground_station:
                for sat in satellites: 
                    sat_id = sat._id
                    for gndstn in ground_station:
                        gndstn_id = gndstn._id
                        _pkt = copy.deepcopy(contacts_pkt[1])
                        _pkt["id"] = str(sat_id) + "-with-" + str(gndstn_id) # record the ids stored. the order (i.e. sat_id-to-gndstn_id or gndstn_id-to-sat_id) is important
                        sat_with_gs_comm_ids.append(_pkt["id"])
                        _pkt["name"] = _pkt["id"]
                        _pkt["polyline"]["show"] =  {"interval":mission_interval, "boolean":False} # initialization of no-contacts throughout the mission-interval
                        _pkt["polyline"]["positions"]["references"] = [str(sat_id)+"#position",str(gndstn_id)+"#position"]                    
                        czml_pkts.append(_pkt)

        # between satellite and satellite
        intersatcomm_ids = []
        if satellites:
            for j in range(0,len(satellites)):
                sat1_id = satellites[j]._id
                for k in range(j+1,len(satellites)):                
                    sat2_id = satellites[k]._id
                    _pkt = copy.deepcopy(contacts_pkt[1])
                    _pkt["id"] = str(sat1_id) + "-with-" + str(sat2_id) 
                    intersatcomm_ids.append(_pkt["id"]) # record the ids stored. the order (i.e. sat1_id-to-sat2_id or sat2_id-to-sat1_id) is important
                    _pkt["name"] = _pkt["id"]
                    _pkt["polyline"]["show"] =  {"interval":mission_interval, "boolean":False}  # initialization of no contacts throughout the mission case
                    _pkt["polyline"]["positions"]["references"] = [str(sat1_id)+"#position",str(sat2_id)+"#position"]
                    czml_pkts.append(_pkt)

        # iterate over each operation in the list of operations. If they correspond to ground-station communications or intersatellite communications,
        # or taking images, make the corresponding czml packet
        for oper in operations:            
            if(CommandType.get(oper['@type']) == CommandType.TRANSMITDATA):                
                
                tx_entity_id = oper["txEntityId"]
                rx_entity_id = oper["rxEntityId"]

                #time_from = (epoch + datetime.timedelta(0, oper['startTime'])).isoformat() + 'Z'# old version
                #time_to = (epoch + datetime.timedelta(0, oper['endTime'])).isoformat() + 'Z' # old version
                time_from = oper['startTime']
                time_to = oper['endTime']
                interval = time_from + "/" + time_to
                contact = {"interval":interval, "boolean":True}

                _pkt = copy.deepcopy(contacts_pkt[1])
                
                if(MissionEntityType.get(oper["txEntityType"])==MissionEntityType.SPACECRAFT and MissionEntityType.get(oper["rxEntityType"])==MissionEntityType.SPACECRAFT):
                    if(str(tx_entity_id) + "-with-" + str(rx_entity_id) in intersatcomm_ids):                
                        _pkt["id"] = str(tx_entity_id) + "-with-" + str(rx_entity_id) 
                        _pkt["polyline"]["positions"]= [str(tx_entity_id)+"#position",str(rx_entity_id)+"#position"]   
                    else:                       
                        _pkt["id"] = str(rx_entity_id) + "-with-" + str(tx_entity_id) # note the change in order
                        _pkt["polyline"]["positions"]= [str(rx_entity_id)+"#position",str(tx_entity_id)+"#position"]   
                else: # satellite with ground-station communications
                    if(str(tx_entity_id) + "-with-" + str(rx_entity_id) in sat_with_gs_comm_ids):                
                        _pkt["id"] = str(tx_entity_id) + "-with-" + str(rx_entity_id) 
                        _pkt["polyline"]["positions"]= [str(tx_entity_id)+"#position",str(rx_entity_id)+"#position"]   
                    else:                       
                        _pkt["id"] = str(rx_entity_id) + "-with-" + str(tx_entity_id) # note the change in order
                        _pkt["polyline"]["positions"]= [str(rx_entity_id)+"#position",str(tx_entity_id)+"#position"]   
                    
                _pkt["name"] = _pkt["id"]
                _pkt["polyline"]["show"] = contact if bool(contact) else False
                             
                czml_pkts.append(_pkt)
                            
            elif(CommandType.get(oper['@type']) == CommandType.TAKEIMAGE):

                time_from = oper['startTime']
                #time_from = (epoch + datetime.timedelta(0, offset + oper['timeIndexStart'])).isoformat() + 'Z' # TODO Rich version
                #time_to = (epoch + datetime.timedelta(0,offset + oper['endTime'])).isoformat() + 'Z'
                time_to = miss_time_to # TODO:  This make the imaged-locations be highlighted until the end of the animation.
                interval = time_from + "/" + time_to
                initialize_interval = {"interval": mission_interval, "boolean":False} # this is necessary, else the point is shown over entire mission interval 
                obs_interval = {"interval":interval, "boolean":True} 

                '''
                # TODO Rich version, can be removed
                if(not isinstance(oper["observedPosition"]["cartographicDegrees"][0],list)): 
                    oper["observedPosition"]["cartographicDegrees"] = [oper["observedPosition"]["cartographicDegrees"]]
                k = 0
                for obs_pos in oper["observedPosition"]["cartographicDegrees"]: # iterate over possibly multiple points seen over the same time-interval
                    _pkt = copy.deepcopy(observ_pkt)
                    _pkt["id"] = "ObservedGroundPointSat" + str(oper["satelliteId"]) + str(time_from) + "_" + str(k) # only one czml packet per (sat, instru, time-start). multiple ground-points encoded in the single packet.
                    _pkt["point"]["show"] = [initialize_interval, obs_interval]
                    _pkt["position"]["cartographicDegrees"]= obs_pos # [longitude[deg], latitude[deg], height[m]]
                    
                    if(oper["observationValue"] <= 0.3333):
                        _pkt["point"]["color"] = {"rgba": [255,0,0,255]}
                    elif(oper["observationValue"] > 0.333 and oper["observationValue"] <= 0.66666):
                        _pkt["point"]["color"] = {"rgba": [255,255,0,255]}
                    elif(oper["observationValue"] > 0.66666):
                        _pkt["point"]["color"] = {"rgba": [0,255,17,255]}

                    czml_pkts.append(_pkt)
                    k = k + 1

                '''
                # TODO Correct version
                if(not isinstance(oper["observedPosition"]["cartographicDegrees"][0],list)):
                    oper["observedPosition"]["cartographicDegrees"] = [oper["observedPosition"]["cartographicDegrees"]]
                k = 0
                for obs_pos in oper["observedPosition"]["cartographicDegrees"]: # iterate over possibly multiple points seen over the same time-interval
                    _pkt = copy.deepcopy(observ_pkt)
                    _pkt["id"] = "ObservedGroundPointSat" + str(oper["spacecraftId"]) + str(time_from) + "_" + str(k) # only one czml packet per (sat, instru, time-start). multiple ground-points encoded in the single packet.
                    _pkt["point"]["show"] = [initialize_interval, obs_interval]
                    _pkt["position"]["cartographicDegrees"]= obs_pos # [longitude[deg], latitude[deg], height[m]]
                    _pkt["point"]["color"] = oper["color"]

                    czml_pkts.append(_pkt)
                    k = k + 1              
                
        return czml_pkts

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
        
        def updtcblist():
            available_images= config.out_config.get_syndata()  # get all available sats for which outputs are available
            self.available_images_ids = [x['@id'] for x in available_images] if available_images is not None else None
            self.select_img_combo_box['values'] = self.available_images_ids
            self.select_img_combo_box.current(0)
        self.select_img_combo_box = ttk.Combobox(synobsvis_choose_image_frame, postcommand = updtcblist)        
        self.select_img_combo_box.grid(row=0, column=0)
        
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
        self.autocrop_var = tk.IntVar(value=1)
        self.autocrop_chkbtn = ttk.Checkbutton(synobsvis_map_plot_frame, text="Auto crop", onvalue=1, offvalue=0, variable=self.autocrop_var).grid(row=0, column=0)
        ttk.Button(synobsvis_map_plot_frame, text="Plot", command=self.click_plot_btn).grid(row=0, column=1, columnspan=2, padx=20)

    def click_plot_btn(self):
        """ 
        """        
        # get the relevant data
        syn_img_id = self.select_img_combo_box.get()
        syn_img_fp = config.out_config.get_syndata_filepath(syn_img_id)

        with open(syn_img_fp, 'rb') as f:
            env_var = pickle.load(f)
            pixel_poly = pickle.load(f)
            pixel_center_pos = pickle.load(f)
            interpl_var_data = pickle.load(f)            

        # make the plot
        fig_win = tk.Toplevel()
        fig = Figure(figsize=(6,6), dpi=100)

        proj = self._prj_typ_frame.get_specs()

        ax = fig.add_subplot(1,1,1,projection=proj) 
        ax.stock_img()        

        cmap=plt.cm.get_cmap("jet")
        norm=plt.Normalize(min(interpl_var_data),max(interpl_var_data))

        for k in range(0,len(pixel_poly)):
            color=cmap(norm(interpl_var_data[k]))
            ax.add_geometries((pixel_poly[k],), crs=cartopy.crs.PlateCarree(), facecolor=color)
        ax.coastlines()  

        if(self.autocrop_var.get() == 1):
            lon = []
            lat = []
            for _pix_p in pixel_center_pos:
                lon.append(_pix_p['lon[deg]'])
                lat.append(_pix_p['lat[deg]'])
            # limite the plotted geographical area
            max_lon = max(lon) + 5 
            min_lon = min(lon) - 5 
            max_lat = max(lat) + 5 
            min_lat = min(lat) - 5 
            ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        #colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(interpl_var_data)        
        cb = fig.colorbar(sm, ax=ax)   
        cb.set_label(str(env_var))   

        canvas = FigureCanvasTkAgg(fig, master=fig_win)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, fig_win)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)



    
    