import json
import os
import webbrowser
import time
import copy
import datetime
from eosim import config
import pandas as pd
import numpy as np
from tkinter import ttk 
from eosim import config
import orbitpy
import uuid
import logging

logger = logging.getLogger(__name__)

class VisGlobeFrame(ttk.Frame):    

    def __init__(self, win, tab):

        vis_globe_frame = ttk.Frame(tab)
        vis_globe_frame.pack(expand = True, fill ="both", padx=10, pady=10)
        vis_globe_frame.rowconfigure(0,weight=1)
        vis_globe_frame.columnconfigure(0,weight=1)

        vis_globe_plot_frame = ttk.LabelFrame(vis_globe_frame, text='CesiumJS powered animated visualization', labelanchor='n')
        vis_globe_plot_frame.grid(row=0, column=0, sticky='nswe', padx=(10,10))

        # plot frame
        ttk.Button(vis_globe_plot_frame, text="Launch", command=self.click_launch).pack(padx=10, pady=10, ipadx=10, ipady=10, expand=True)

    
    def click_launch(self):
        """ Make CZML file based on the mission executed results and execute the cesium app. """

        czml_template_dir = os.path.dirname(__file__) + '/czml_templates/'
        
        [epoch, step_size, num_time_indices, czml_pkts] = VisGlobeFrame.build_czmlpkts_for_mission_background(czml_template_dir)

        _czml_pkts = VisGlobeFrame.build_czmlpkts_for_ground_stn_contact_opportunities(czml_template_dir, epoch, step_size, num_time_indices)
        czml_pkts.extend(_czml_pkts)
       

        _czml_pkts = VisGlobeFrame.build_czmlpkts_for_intersat_contact_opportunities(czml_template_dir, epoch, step_size, num_time_indices)
        czml_pkts.extend(_czml_pkts)  

        cesium_data_dir = os.path.dirname(__file__) + "/../../../cesium_app/Source/SampleData/"
        # write the CZML data file        
        with open(cesium_data_dir+"eosim_data.czml", 'w') as f:
            json.dump(czml_pkts, f, indent=4)

        self.execute_cesium_app()       
        
    def execute_cesium_app(self):      
        # Server already started in the `bin/eosimapp.py` script
        webbrowser.open('http://localhost:8080/', new=2) # open webbrowser

    @staticmethod
    def build_czmlpkts_for_mission_background(czml_template_dir):
        """ Make CZML packets corresponding to the mission attributes which are operationally independent such 
            as the mission date, satellite orbits, ground-station positions and coverage grid.
            
            :param czml_template_dir: Directory with the CZML packet json templates.
            :paramtype czml_template_dir: str

            :return: List of the following objects: 
                    
                    * CZML packets corresponding to mission-background information. (List of dictionaries.)
                    * Mission epoch. (:class:`datetime.datetime`)
                    * Propagation (time) step-size in seconds. (float)
                    * umber of time-indices i.e. the number of time-steps over which the mission is simulated. (integer)

            :rtype: list

        """

        # make the clock packet
        with open(czml_template_dir+"clock_template.json", 'r') as f:
            clk_pkt_template = json.load(f) 
        
        # get the mission epoch in Gregorian UTC
        _d = config.mission.epoch.GetGregorianDate().GetRealArray()
        epoch = datetime.datetime(int(_d[0]), int(_d[1]), int(_d[2]), int(_d[3]), int(_d[4]), int(_d[5]))

        duration_s = config.mission.duration* 86400
        end_date = epoch + datetime.timedelta(0,int(duration_s))

        czml_pkts = [] # list of packets

        clk_pkt = copy.deepcopy(clk_pkt_template)
        clk_pkt["clock"]["interval"] = str(epoch.isoformat())+ 'Z'+"/"+str(end_date.isoformat()) + 'Z' # Z implies UTC
        clk_pkt["clock"]["currentTime"] = epoch.isoformat() + 'Z'
        
        czml_pkts.append(clk_pkt)
        
        # make the ground-station packets
        with open(czml_template_dir+"ground_station_template.json", 'r') as f:
            gndstn_pkt_template = json.load(f)
        
        ground_station = config.mission.groundStation # list of orbitpy.util.GroundStation objects in the mission
        if ground_station:
            for gndstn in ground_station:
                _pkt = copy.deepcopy(gndstn_pkt_template)
                _pkt["id"] = gndstn._id
                _pkt["name"] = gndstn.name
                _pkt["label"]["text"] = gndstn.name
                _pkt["position"] = {}
                _pkt["position"]["cartographicDegrees"] = [gndstn.longitude, gndstn.latitude, gndstn.altitude*1e3]
                czml_pkts.append(_pkt)

        # make the satellite packets
        with open(czml_template_dir+"satellite_template.json", 'r') as f:
            sat_pkt_template = json.load(f) 

        # iterate over list of satellites whose orbit-propagation data is available
        for info in config.mission.outputInfo:
            if info._type == orbitpy.util.OutputInfoUtility.OutputInfoType.PropagatorOutputInfo.value:
                sat_id = info.spacecraftId
                sat_state_fp = info.stateCartFile
                # read the time-step size and fix the start and stop indices
                # the epoch and duration are expected to be the same as the mission epoch and duration (and hence same for all the satellites)
                (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(sat_state_fp)
                sat_state_df = pd.read_csv(sat_state_fp, skiprows = [0,1,2,3]) 
                sat_state_df = sat_state_df[['time index','x [km]','y [km]','z [km]']] # velocity information is not needed
                num_time_indices = len(sat_state_df['time index']) # shall be same for all satellites
                # reformat the data to the one expected by Cesium
                sat_state_df['Time[s]'] = np.array(sat_state_df['time index']) * step_size
                sat_state_df['X[m]'] = np.array(sat_state_df['x [km]']) * 1000
                sat_state_df['Y[m]'] = np.array(sat_state_df['y [km]']) * 1000
                sat_state_df['Z[m]'] = np.array(sat_state_df['z [km]']) * 1000
                sat_state_df = sat_state_df[['Time[s]','X[m]','Y[m]','Z[m]']]

                _sat_pkt = copy.deepcopy(sat_pkt_template)
                _sat_pkt["id"] = sat_id
                _sat_pkt["name"] = _sat_pkt["id"]#"Sat"+_sat_pkt["id"]
                _sat_pkt["label"]["text"] = _sat_pkt["name"]
                _sat_pkt["position"]["epoch"] = epoch.isoformat() + 'Z'
                _sat_pkt["position"]["cartesian"] = sat_state_df.values.flatten().tolist()

                czml_pkts.append(_sat_pkt)

        # make packets showing the coverage grid
        with open(czml_template_dir+"covgrid_pkt_template.json", 'r') as f:
            covgrid_pkt_template = json.load(f)
        # iterate over list of grids in the mission
        if config.mission.grid:
            for grid in config.mission.grid:
                (lat, lon) = grid.get_lat_lon() # the latitudes and longitudes (in degrees) are returned in lists
                # each grid-point in the grid is encoded in a separate packet
                for index, val in enumerate(lat):
                    _pkt = copy.deepcopy(covgrid_pkt_template)
                    _pkt["id"] = "Gridpoint/"+ str(grid._id) + "/"+ str(index)
                    _pkt["position"] = {}
                    _pkt["position"]["cartographicDegrees"] = [lon[index], lat[index], 0]
                    czml_pkts.append(_pkt) 

        return [epoch, step_size, num_time_indices, czml_pkts]

    @staticmethod
    def build_czmlpkts_for_ground_stn_contact_opportunities(czml_template_dir, epoch, step_size, num_time_indices):
        """ Build CZML packets with the ground-station contact information.
        
            :param czml_template_dir: Directory with the CZML packet json templates.
            :paramtype czml_template_dir: str

            :param epoch: Mission epoch
            :paramtype epoch: :class:`datetime.datetime`

            :param step_size: propagation (time) step-size in seconds.
            :paramtype step_size: float

            :param num_time_indices: Number of time-indices i.e. the number of time-steps over which the mission is simulated.
            :paramtype num_time_indices: int

            :return: CZML packets corresponding to ground-station contact opportunites. (List of dictionaries.)
            :rtype: list, dict

        """

        czml_pkts = []
        with open(czml_template_dir+"contacts_template.json", 'r') as f:
            contacts_pkt = json.load(f)
        
        contacts_pkt[0]["id"] = str(uuid.uuid4()) # TODO: Not sure if this parent packet is required
        czml_pkts.append(contacts_pkt[0])

        # iterate over all ground-station contact results
        for info in config.mission.outputInfo:
            if info._type == orbitpy.util.OutputInfoUtility.OutputInfoType.ContactFinderOutputInfo.value: # check if outputInfo corresponds to ContactInfo
                if info.entityAtype == "GroundStation" or info.entityBtype == "GroundStation": # check if contact is that with ground-station
                    
                    gndstn_id = info.entityAId if info.entityAtype == "GroundStation" else info.entityBId
                    sat_id = info.entityAId if info.entityAtype == "Spacecraft" else info.entityBId
                    
                    contact_df = pd.read_csv(info.contactFile, skiprows=[0,1,2])

                    # the contacts in the contactFile correspond to contact-intervals. This must be processed to a format (as required by Cesium) in which 
                    # both the contact and no-contact intervals are available. 
                    contacts = []
                    is_first_contact = True
                    previous_row = False
                    for index, row in contact_df.iterrows():
                        
                        if(is_first_contact):                    
                            if(row['start index']!=0): # interval of no contact during the beginning, add this to the contacts (with boolean = False)
                                time_from = epoch.isoformat() + 'Z'
                                time_to = (epoch + datetime.timedelta(0,int(row['start index'] * step_size))).isoformat() + 'Z'
                                interval = time_from + "/" + time_to
                                contacts.append({"interval":interval, "boolean":False})                   
                        
                        time_from = (epoch + datetime.timedelta(0,int(row['start index'] * step_size))).isoformat() + 'Z'
                        time_to = (epoch + datetime.timedelta(0,int(row['end index'] * step_size))).isoformat() + 'Z'
                        interval = time_from + "/" + time_to
                        contacts.append({"interval":interval, "boolean":True})

                        if is_first_contact is False:
                            # attach a period of no-contact between the consecutive contact periods
                            time_from = (epoch + datetime.timedelta(0,int(previous_row['end index'] * step_size))).isoformat() + 'Z'
                            time_to = (epoch + datetime.timedelta(0,int(row['start index'] * step_size))).isoformat() + 'Z'
                            interval = time_from + "/" + time_to
                            contacts.append({"interval":interval, "boolean":False})

                        previous_row = row
                        is_first_contact = False

                    # check the time towards the end
                    if contacts: # if any contacts exist
                        if(previous_row['end index']!=num_time_indices):
                            # attach a period of no-contact between the previous interval-end and end-of-simulation
                            time_from = (epoch + datetime.timedelta(0,int(previous_row['end index'] * step_size))).isoformat() + 'Z'
                            time_to = (epoch + datetime.timedelta(0,num_time_indices * step_size)).isoformat() + 'Z'
                            interval = time_from + "/" + time_to
                            contacts.append({"interval":interval, "boolean":False})
                    
                    _pkt = copy.deepcopy(contacts_pkt[1])
                    _pkt["id"] = str(sat_id) + "-to-" + str(gndstn_id) 
                    _pkt["name"] = _pkt["id"]
                    _pkt["polyline"]["show"] = contacts if bool(contacts) else False # no contacts throughout the mission case
                    _pkt["polyline"]["positions"]["references"] = [str(sat_id)+"#position",str(gndstn_id)+"#position"]
                    
                    czml_pkts.append(_pkt)

        return czml_pkts

    @staticmethod
    def build_czmlpkts_for_intersat_contact_opportunities(czml_template_dir, epoch, step_size, num_time_indices):
        """ Build CZML packets with the inter-satellite contact information.

            :param czml_template_dir: Directory with the CZML packet json templates.
            :paramtype czml_template_dir: str

            :param epoch: Mission epoch
            :paramtype epoch: :class:`datetime.datetime`

            :param step_size: propagation (time) step-size in seconds.
            :paramtype step_size: float

            :param num_time_indices: Number of time-indices i.e. the number of time-steps over which the mission is simulated.
            :paramtype num_time_indices: int

            :return: CZML packets corresponding to inter-satellite contact opportunites. (List of dictionaries.)
            :rtype: list, dict

        """

        czml_pkts = []
        with open(czml_template_dir+"contacts_template.json", 'r') as f:
            contacts_pkt = json.load(f)
        
        contacts_pkt[0]["id"] = str(uuid.uuid4()) # TODO: Not sure if this parent packet is required
        czml_pkts.append(contacts_pkt[0])

        # iterate over all inter-satellite contact results
        for info in config.mission.outputInfo:
            if info._type == orbitpy.util.OutputInfoUtility.OutputInfoType.ContactFinderOutputInfo.value: # check if outputInfo corresponds to ContactInfo
                if info.entityAtype == "Spacecraft" or info.entityBtype == "GroundStation": # check if contact is that between satellites
                    
                    satA_id = info.entityAId
                    satB_id = info.entityBId
                    
                    contact_df = pd.read_csv(info.contactFile, skiprows=[0,1,2])

                    # the contacts in the contactFile correspond to contact-intervals. This must be processed to a format (as required by Cesium) in which 
                    # both the contact and no-contact intervals are available. 
                    contacts = []
                    is_first_contact = True
                    previous_row = False
                    for index, row in contact_df.iterrows():
                        
                        if(is_first_contact):                    
                            if(row['start index']!=0): # interval of no contact during the beginning, add this to the contacts (with boolean = False)
                                time_from = epoch.isoformat() + 'Z'
                                time_to = (epoch + datetime.timedelta(0,int(row['start index'] * step_size))).isoformat() + 'Z'
                                interval = time_from + "/" + time_to
                                contacts.append({"interval":interval, "boolean":False})                   
                        
                        time_from = (epoch + datetime.timedelta(0,int(row['start index'] * step_size))).isoformat() + 'Z'
                        time_to = (epoch + datetime.timedelta(0,int(row['end index'] * step_size))).isoformat() + 'Z'
                        interval = time_from + "/" + time_to
                        contacts.append({"interval":interval, "boolean":True})

                        if is_first_contact is False:
                            # attach a period of no-contact between the consecutive contact periods
                            time_from = (epoch + datetime.timedelta(0,int(previous_row['end index'] * step_size))).isoformat() + 'Z'
                            time_to = (epoch + datetime.timedelta(0,int(row['start index'] * step_size))).isoformat() + 'Z'
                            interval = time_from + "/" + time_to
                            contacts.append({"interval":interval, "boolean":False})

                        previous_row = row
                        is_first_contact = False

                    # check the time towards the end
                    if contacts: # if any contacts exist
                        if(previous_row['end index']!=num_time_indices):
                            # attach a period of no-contact between the previous interval-end and end-of-simulation
                            time_from = (epoch + datetime.timedelta(0,int(previous_row['end index'] * step_size))).isoformat() + 'Z'
                            time_to = (epoch + datetime.timedelta(0,num_time_indices * step_size)).isoformat() + 'Z'
                            interval = time_from + "/" + time_to
                            contacts.append({"interval":interval, "boolean":False})
                    
                    _pkt = copy.deepcopy(contacts_pkt[1])
                    _pkt["id"] = str(satA_id) + "-to-" + str(satB_id) 
                    _pkt["name"] = _pkt["id"]
                    _pkt["polyline"]["show"] = contacts if bool(contacts) else False # no contacts throughout the mission case
                    _pkt["polyline"]["positions"]["references"] = [str(satA_id)+"#position",str(satB_id)+"#position"]
                    
                    czml_pkts.append(_pkt)

        return czml_pkts

    

        