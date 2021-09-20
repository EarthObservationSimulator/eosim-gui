from tkinter import ttk 
import os

from orbitpy.mission import Mission

import logging
logger = logging.getLogger(__name__)

""" This variable is used to the workspace directory where the output files of EOSim shall be saved.  
    This object is imported and referenced over all the EOSim modules and hence acts as a sort of global 
    variable for the entire EOSim software."""
workspace_dir = None

""" A MissionConfig instance to be used to store the mission configuration. This 
    object is imported and referenced over all the EOSim modules and hence
    acts as a sort of global variable for the entire EOSim software.
"""
mission_specs = Mission() 
class GuiStyle():
    main_win_width = 900
    main_win_height = int(main_win_width*9/21) # 21:9 aspect ratio
    main_window_geom = str(main_win_width)+"x"+str(main_win_height) 
    child_window_geom = "500x500"
    
    def __init__(self):     
        gui_style = ttk.Style()
        gui_style.configure('My.TButton', foreground='#334353')
        gui_style.configure('messagearea.TFrame', background='white',  relief='sunken')
        gui_style.configure('lsidebar.TFrame', background='light grey',  relief='groove')
        gui_style.configure('lsidebar.TButton')
        # Create style for the frames used within the help window
        gui_style.configure('helpHeading.TFrame', background='#87ceeb')
        gui_style.configure('helpHeading.Label', background='#87ceeb', foreground='white', font=('Times New Roman',18,'bold'))
        
        gui_style.configure('helpDescription.TFrame', background='white')
        gui_style.configure('helpDescription.Label', background='white', foreground='black', font=('Times New Roman',16))

        gui_style.configure('helpMoreHelp.TFrame', background='light grey') 
        gui_style.configure('helpMoreHelp.Label', background='light grey', foreground='dark blue', font=('Times New Roman',12))

class MissionConfig:
    """ Class which holds all the mission configuration parameters """
    def __init__(self, epoch=None, duration=None, satellite=None, sensor=None, sat_to_sensor_map=None, prop=None, 
                 cov_grid=None, pnt_opts=None, gnd_stns = None, intersatcomm=None):
        self.epoch = epoch if epoch is not None else None
        self.duration = duration if duration is not None else None
        self.satellite = list(satellite) if satellite is not None else list() # satellite is the same as orbit
        self.sensor = list(sensor) if sensor is not None else list()
        self.sat_to_sensor_map = list(sat_to_sensor_map) if sat_to_sensor_map is not None else list()
        self.prop = prop if prop is not None else None
        self.cov_grid =  cov_grid if cov_grid is not None else None
        self.pnt_opts =  pnt_opts if pnt_opts is not None else None
        self.gnd_stns =  gnd_stns if gnd_stns is not None else None
        self.intersatcomm =  intersatcomm if intersatcomm is not None else None
    
    def clear(self):
        self.epoch = None
        self.duration = None
        self.satellite = list()
        self.sensor = list()
        self.sat_to_sensor_map = list()
        self.prop = None
        self.cov_grid = None
        self.pnt_opts = None
        self.gnd_stns = None
        self.intersatcomm = None
    
    def update_epoch(self, epoch):
        self.epoch = epoch

    def update_intersatcomm(self, opaque_atmos_height = None):
        self.intersatcomm = {"opaqueAtmosphericHeight": opaque_atmos_height}

    def update_duration(self, duration):
        self.duration = duration

    def add_satellite(self, sat):
        if isinstance(sat,list):
            self.satellite.extend(sat) 
        else:
            self.satellite.append(sat) 
    
    def add_propagator(self, prop):
        self.prop = prop

    def add_sensor(self, sensor, sensor_to_sat):
        """ Add sensor to the given list of satellites.

            :param sensor: Sensor 
            :paramtype sensor: :class:`instrupy.`

            :param sensor_to_sat: Unique IDs of satellites to which the sensor is to be attached. 
            :paramtype sensor_to_sat: list

        """
        if isinstance(sensor,list):
            self.sensor.extend(sensor) 
        else:
            self.sensor.append(sensor) 
        
        sensor_id = sensor.get_id() # get the unique instrument id
        # note that the self.sat_to_sensor_map index is tied to the index of self.sensor
        self.sat_to_sensor_map.append((sensor_id, sensor_to_sat)) # tuple of sensor-id and *list* of satetllites to which the sensor is attached

    def add_coverage_grid(self, data):
        self.cov_grid = data

    def add_pointing_options(self, data):
        self.pnt_opts = data
    
    def add_ground_stations(self, data):
        self.gnd_stns = data

    def get_satellite_kepl_specs(self):
        # parse out the satellite ids (orbit ids)
        orb_specs = []
        if(len(self.satellite) == 0):
            return False
        for _sat in self.satellite:
            orb_specs.append([_sat._id, _sat.sma, _sat.ecc, _sat.inc, _sat.raan, _sat.aop, _sat.ta])        
        return orb_specs 

    def get_sensor_specs(self, sensor_id=None):        
        
        # get the specifications of all sensors
        # get the sensors (primary specs) in the mission config
        sensor_specs = []
        if(len(self.sensor) == 0):
            return False
        k = 0 # note that the self.sat_to_sensor_map index is tied to the index of self.sensor
        for _sen in self.sensor:
            sensor_specs.append([_sen.get_id(), _sen.get_type(), self.sat_to_sensor_map[k]])   
            k = k + 1   

        if(sensor_id is not None): # return the specifications of the sensor with the corresponding id
            for _sen in self.sensor:
                if(sensor_id == _sen.get_id()):
                    return _sen
            logger.info("Sensor with the input id was not found")
            return False
          
        return sensor_specs          

    def to_dict(self):
        """ Format the MissionConfig object into a dictionary (so it may later be exported as JSON file)."""
        sat_dict = []
        for sat in self.satellite:
            sat_sensor = [] # list of sensors in the satellite
            for k in range(0, len(self.sensor)): # note that the self.sat_to_sensor_map index is tied to the index of self.sensor
                if sat._id in self.sat_to_sensor_map[k][1]:
                    sat_sensor.append(self.sensor[k])
            t = [x.to_dict() for x in sat_sensor]
            flat_list = [item for sublist in t for item in sublist]
            sat_dict.append({"orbit":sat.to_dict(), "instrument": flat_list}) 

        miss_specs_dict = dict({"epoch":self.epoch,
                                "duration": self.duration,
                                "satellite": sat_dict,
                                "propagator": self.prop,
                                "grid": self.cov_grid,
                                "pointingOptions": self.pnt_opts,
                                "groundStations": self.gnd_stns,
                                "interSatelliteComm": self.intersatcomm
                               }) 
        return miss_specs_dict


class OutputConfig:
    """ A class to allow handling of the produced results of the various functionalities of EOSim (propagation, coverage, etc).
        The class is updated with file-locations of the resultant data files as and when a new result is produced. 
        This class would be referenced by the various plotting functions in EOSim. 
        Using this class, a JSON file called 'output.json' would be written in the user directory.    
    """
    def __init__(self, prop_done=None, cov_done=None, sat_out=None, user_dir=None, gnd_stn_comm_done=None, 
                        intersat_comm_done=None, intersat_comm=None, syn_data=None):
        self.prop_done = prop_done if prop_done is not None else bool(False)
        self.cov_done = cov_done if cov_done is not None else bool(False)
        self.sat_out = list(sat_out) if sat_out is not None else list()
        self.user_dir = user_dir if user_dir is not None else os.path.join(os.path.dirname(__file__), '../output/')
        self.gnd_stn_comm_done = gnd_stn_comm_done if gnd_stn_comm_done is not None else bool(False)
        self.intersat_comm_done = intersat_comm_done if intersat_comm_done is not None else bool(False)
        self.intersat_comm = list(intersat_comm) if intersat_comm is not None else list()
        self.syn_data= syn_data if syn_data is not None else dict() # dictionary with syn data dir and subdir paths

    @staticmethod
    def from_dict(d):
        return OutputConfig(prop_done=d.get('propDone', None),
                            cov_done=d.get('covDone', None),
                            sat_out=d.get('satOut', None),
                            user_dir=d.get('user_dir', None),
                            gnd_stn_comm_done=d.get('gnd_stn_comm_done', None),
                            intersat_comm_done=d.get('intersat_comm_done', None),
                            intersat_comm=d.get('interSatComm',None)) 

    def update_syndatadir(self, syn_data_dir):
        self.syn_data = {} # reinitialize
        self.syn_data['dir'] = syn_data_dir
        self.syn_data['data'] = list()

    def get_syndatadir(self):
        return self.syn_data['dir']

    def update_syndata(self, syndata_id, syndata_fp):
        self.syn_data['data'].append({'@id':syndata_id, 'filePath': syndata_fp})

    def get_syndata(self):
        if 'data' in self.syn_data:
            return self.syn_data['data']
        else:
            return None
    
    def get_syndata_filepath(self, syndata_id):
        if not isinstance(self.syn_data['data'], list):
            self.syn_data['data'] = [self.syn_data['data']]
        for x in self.syn_data['data']:
            if(x['@id']==syndata_id or x['@id']==str(syndata_id) or str(x['@id'])==syndata_id):
                return x['filePath']


    def update_prop_out(self, sat_id, sat_eci_state_fp, sat_kep_state_fp):
        self.prop_done = True
        self.sat_out = list() # erase any previous entries
        for k in range(0,len(sat_id)):
            self.sat_out.append({"@id":sat_id[k], "StateFilePath":sat_eci_state_fp[k], "KepStateFilePath":sat_kep_state_fp[k]})

    def update_cov_out(self, sat_id, sat_acc_fl):
        self.cov_done = True
        for k in range(0,len(self.sat_out)):
            indx = sat_id.index(self.sat_out[k]["@id"]) # match the sat_id to the list of satellites in the output config object
            if indx is not None:
                self.sat_out[k].update({"AccessFilePath":sat_acc_fl[indx]})
            else:
                raise Exception("Satellite id not found.")

    def update_ground_stns_comm(self, sat_id, gnd_stn_id, gndstncomm_concise_fls, gndstncomm_detailed_fls): 
        ''' sat_id is a single value, the rest of the parameters are lists, i.e. multiple ground-stations per satellite
        '''
        self.gnd_stn_comm_done = True
        internal_index = self.get_satellite_ids().index(sat_id)
        if internal_index is not None:
            gs = []
            if not isinstance(gnd_stn_id, list): 
                gnd_stn_id = [gnd_stn_id]

            for k in range(0,len(gnd_stn_id)): # iterate through ground stations accessed by the satellite
                gs.append({"@id": gnd_stn_id[k], "concise_fl":gndstncomm_concise_fls[k], "detailed_fl":gndstncomm_detailed_fls[k]})

            self.sat_out[internal_index].update({"GroundStationComm":gs})
        else:
            raise Exception("Satellite id not found.")

    def get_satout(self):
        return self.sat_out

    def update_calc_obsmetrics(self, sat_id, ssid, obsMetrics_fl):
        # TBD
        pass

    def update_intersatcomm(self, sat1_ids, sat2_ids, intersatcomm_concise_fls, intersatcomm_detailed_fls):
        self.intersat_comm_done = True
        for k in range(0,len(sat1_ids)):
            self.intersat_comm.append({"sat1_id": sat1_ids[k], "sat2_id":sat2_ids[k], "concise_fl": intersatcomm_concise_fls[k], "detailed_fl":intersatcomm_detailed_fls[k]})
        
    def get_intersatcomm(self):
        return self.intersat_comm
        
    def set_user_dir(self,user_dir):
        self.user_dir = user_dir

    def get_satellite_ids(self):
        return [x["@id"] for x in self.sat_out]

    def get_satellite_state_fp(self):
        return [x["StateFilePath"] for x in self.sat_out]

    def get_satellite_kepstate_fp(self):
        return [x["KepStateFilePath"] for x in self.sat_out]

    def get_user_dir(self):
        return self.user_dir

    def to_dict(self):
        """ Format the OutputConfig object into a dictionary (so it may later be exported as JSON file)."""

        output_config_dict = dict({"propDone":self.prop_done,
                                   "covDone": self.cov_done,
                                   "satOut": self.sat_out,
                                   "user_dir": self.user_dir,
                                   "gnd_stn_comm_done": self.gnd_stn_comm_done,
                                   "intersat_comm_done": self.intersat_comm_done,
                                   "interSatComm": self.intersat_comm,
                                   "syndata": self.syn_data
                                  }) 
        return output_config_dict

""" A OutputConfig instance to be used to store the output meta-data. This 
    object is imported and referenced over all the EOSim modules and hence
    acts as a sort of global variable for the entire EOSim software.
"""
out_config = OutputConfig()  