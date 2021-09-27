from tkinter import ttk 
import tkinter as tk
from eosim import config
import random
import tkinter.filedialog, tkinter.messagebox
from instrupy.base import Instrument
import os
import eosim.gui.helpwindow as helpwindow
from netCDF4 import Dataset as netCDF4Dataset
import logging

logger = logging.getLogger(__name__)

class CfSensor():
    
    def click_sensor_btn(self):      
        # create and configure child window, parent frame
        sensor_win = tk.Toplevel()
        sensor_win.rowconfigure(0,weight=1)
        sensor_win.columnconfigure(0,weight=1)

        # create a separate tab for each sensor type
        tabControl = ttk.Notebook(sensor_win)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='Basic Sensor')
        tabControl.add(tab2, text='Passive Optical Scanner')
        tabControl.add(tab3, text='Synthetic Aperture Radar')

        tabControl.pack(expand = 1, fill ="both")   

        BasicSensorInputConfigure(sensor_win, tab1)
        PassiveOpticalScanner(sensor_win, tab2)
        SyntheticApertureRadarInputConfigure(sensor_win, tab3)

class NadirOrientation(ttk.Frame):
    """ Class which handles the nadir-pointing orientation frame."""
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        nadirorien_specs_frame = ttk.Frame(self) 
        nadirorien_specs_frame.grid(row=0, column=0)

    def get_specs(self):
        """ Return the orientation specifications as dictionary."""
        return {'referenceFrame': 'NADIR_POINTING', 'convention': 'REF_FRAME_ALIGNED'}

class SideLookOrientation(ttk.Frame):
    """ Class which handles the side-look orientation frame."""
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        sidelookorien_specs_frame = ttk.Frame(self) 
        sidelookorien_specs_frame.grid(row=0, column=0)

        # define the widgets
         # define the widgets inside the frame
        ttk.Label(sidelookorien_specs_frame, text="Reference Frame", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.ref_frame_combobox = ttk.Combobox(sidelookorien_specs_frame, values=['NADIR_POINTING'])
        self.ref_frame_combobox.grid(row=0, column=1)
        self.ref_frame_combobox.current(0)
        
        ttk.Label(sidelookorien_specs_frame, text="Side Look Angle [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.sla_entry = ttk.Entry(sidelookorien_specs_frame, width=10)
        self.sla_entry.insert(0,10)
        self.sla_entry.bind("<FocusIn>", lambda args: self.sla_entry.delete('0', 'end'))
        self.sla_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)     
    
    def get_specs(self):
        """ Return the orientation specifications as dictionary."""
        return { 'referenceFrame': str(self.ref_frame_combobox.get()), 'convention': float(self.sla_entry.get())}

class SyntheticDataConfigurationFrame(ttk.Frame):
    """ Class to handle the synthetic data configuration."""
    def __init__(self, parent, controller):
        
        ttk.Frame.__init__(self, parent)
        sdc_frame = ttk.Frame(self) 
        sdc_frame.grid(row=0, column=0)

        def click_sel_envdata_src_btn(): 
            self.envdata_fp = None               
            self.envdata_fp = tkinter.filedialog.askopenfilenames(initialdir=os.getcwd(), title="Please select the environment data file:", filetypes=(("All files","*.*"),("NetCDF files","*.nc")))
            self.envdata_fp = list(self.envdata_fp)
            if self.envdata_fp[0] != '':                    
                envdata = netCDF4Dataset(self.envdata_fp[0], "r", format="NETCDF4")                    
                for key, value in envdata.variables.items():
                    self.env_vars.append(key)
                self.env_vars_combobox['values'] = self.env_vars
                self.env_vars_combobox.current(0)
        
        self.envdata_fp = None
        self.env_vars = []
        ttk.Button(sdc_frame, text="Select science data file", command=click_sel_envdata_src_btn).grid(row=0,column=0, padx=10, pady=10)
        self.env_vars_combobox = ttk.Combobox(sdc_frame, values=self.env_vars)
        self.env_vars_combobox.grid(row=1, column=0)

        ttk.Label(sdc_frame, text="Select interpolation method").grid(row=2,column=0, padx=10, pady=10)
        self.interpl_method_combobox = ttk.Combobox(sdc_frame, values=['scipy Linear', 'metpy Linear', 'metpy Nearest Neighbor', 'mepy Cubic', 'metpy Radial Basis', 'metpy Natural Newighbour 2D', 'metpy Barnes 2D', 'metpy Cressman 2D'])
        self.interpl_method_combobox.grid(row=3, column=0)
        self.interpl_method_combobox.current(0)
    
    def get_specs(self):
        """Return the synthetic data configuration."""
        return { "sourceFilePaths": str(self.envdata_fp), 
                 "geophysicalVar": str(self.env_vars_combobox.get()), 
                 "interpolMethod": 'scipy.interpolate.linear' # self.interpl_method_combobox.get() TODO
                }

class XYZOrientation(ttk.Frame):
    """ Class which handles the XYZ orientation frame."""
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        xyzorien_specs_frame = ttk.Frame(self) 
        xyzorien_specs_frame.grid(row=0, column=0)

         # define the widgets inside the frame
        ttk.Label(xyzorien_specs_frame, text="Reference Frame", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.ref_frame_combobox = ttk.Combobox(xyzorien_specs_frame, values=['NADIR_POINTING'])
        self.ref_frame_combobox.grid(row=0, column=1)
        self.ref_frame_combobox.current(0)

        ttk.Label(xyzorien_specs_frame, text="X rotation [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.xorien_entry = ttk.Entry(xyzorien_specs_frame, width=10)
        self.xorien_entry.insert(0,10)
        self.xorien_entry.bind("<FocusIn>", lambda args: self.xorien_entry.delete('0', 'end'))
        self.xorien_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        
        ttk.Label(xyzorien_specs_frame, text="Y rotation [deg]", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.yorien_entry = ttk.Entry(xyzorien_specs_frame, width=10)
        self.yorien_entry.insert(0,20)
        self.yorien_entry.bind("<FocusIn>", lambda args: self.yorien_entry.delete('0', 'end'))
        self.yorien_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(xyzorien_specs_frame, text="Z rotation [deg]", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.zorien_entry = ttk.Entry(xyzorien_specs_frame, width=10)
        self.zorien_entry.insert(0,20)
        self.zorien_entry.bind("<FocusIn>", lambda args: self.zorien_entry.delete('0', 'end'))
        self.zorien_entry.grid(row=3, column=1, sticky='w', padx=10, pady=10)
    
    def get_specs(self):
        """ Return the orientation specifications as dictionary."""
        return {'referenceFrame': str(self.ref_frame_combobox.get()), 
                'convention': 'XYZ',
                'xRotation': float(self.xorien_entry.get()), 
                'yRotation': float(self.yorien_entry.get()), 
                'zRotation': float(self.zorien_entry.get())
               }
class CircularFOVGeometry(ttk.Frame):
    """ Class which handles the circular FOV geometry frame."""
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        confov_specs_frame = ttk.Frame(self) 
        confov_specs_frame.grid(row=0, column=0)

        # define the widgets 
        ttk.Label(confov_specs_frame, text="diameter [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.fca_entry = ttk.Entry(confov_specs_frame, width=10)
        self.fca_entry.insert(0,30)
        self.fca_entry.bind("<FocusIn>", lambda args: self.fca_entry.delete('0', 'end'))
        self.fca_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

    def get_specs(self):
        """ Return the fov geometry specifications as dictionary."""
        return {'shape': 'CIRCULAR', 'diameter': float(self.fca_entry.get())}

class RectangularFOVGeometry(ttk.Frame):
    def __init__(self, parent, controller):
        """ Class which handles the rectangular FOV geometry frame."""
        ttk.Frame.__init__(self, parent)
        rectfov_specs_frame = ttk.Frame(self) 
        rectfov_specs_frame.grid(row=0, column=0)

        # define the widgets
        ttk.Label(rectfov_specs_frame, text="Angle Height [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.atfov_entry = ttk.Entry(rectfov_specs_frame, width=10)
        self.atfov_entry.insert(0,10)
        self.atfov_entry.bind("<FocusIn>", lambda args: self.atfov_entry.delete('0', 'end'))
        self.atfov_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        
        ttk.Label(rectfov_specs_frame, text="Angle Width [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.ctfov_entry = ttk.Entry(rectfov_specs_frame, width=10)
        self.ctfov_entry.insert(0,20)
        self.ctfov_entry.bind("<FocusIn>", lambda args: self.ctfov_entry.delete('0', 'end'))
        self.ctfov_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(rectfov_specs_frame, text="Angle height/ width correspond to along/ cross -track FOV when sensor is aligned in nadir-pointing frame.", wraplength=250).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='w')
    
    def get_specs(self):
        """ Return the fov geometry specifications as dictionary."""
        return {'shape': 'RECTANGULAR', 'angleHeight': float(self.atfov_entry.get()), 'angleWidth': float(self.ctfov_entry.get())}

class FixedManeuver(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        fixedmanuv_specs_frame = ttk.Frame(self) 
        fixedmanuv_specs_frame.grid(row=0, column=0)

    def get_specs(self):
        return None

class CircularManeuver(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        circmanuv_specs_frame = ttk.Frame(self) 
        circmanuv_specs_frame.grid(row=0, column=0)

        # define the widgets 
        ttk.Label(circmanuv_specs_frame, text="Diameter [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.circmanuv_fca_entry = ttk.Entry(circmanuv_specs_frame, width=10)
        self.circmanuv_fca_entry.insert(0,50)
        self.circmanuv_fca_entry.bind("<FocusIn>", lambda args: self.circmanuv_fca_entry.delete('0', 'end'))
        self.circmanuv_fca_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

    def get_specs(self):
        return {'maneuverType': 'CIRCULAR', 'diameter': float(self.circmanuv_fca_entry.get())}

class RollOnlyManeuver(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        rollmanuv_specs_frame = ttk.Frame(self) 
        rollmanuv_specs_frame.grid(row=0, column=0)

        # define the widgets
        ttk.Label(rollmanuv_specs_frame, text="Minimum Roll [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.manuv_minroll_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
        self.manuv_minroll_entry.insert(0,-30)
        self.manuv_minroll_entry.bind("<FocusIn>", lambda args: self.manuv_minroll_entry.delete('0', 'end'))
        self.manuv_minroll_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)                   

        ttk.Label(rollmanuv_specs_frame, text="Maximum Roll [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.manuv_maxroll_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
        self.manuv_maxroll_entry.insert(0,30)
        self.manuv_maxroll_entry.bind("<FocusIn>", lambda args: self.manuv_maxroll_entry.delete('0', 'end'))
        self.manuv_maxroll_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)          
            
    def get_specs(self):
        return {'maneuverType':'Single_Roll_Only', 'A_rollMin': float(self.manuv_minroll_entry.get()), 'A_rollMax': float(self.manuv_maxroll_entry.get())}
class DoubleRollOnlyManeuver(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        rollmanuv_specs_frame = ttk.Frame(self) 
        rollmanuv_specs_frame.grid(row=0, column=0)

        # define the widgets
        ttk.Label(rollmanuv_specs_frame, text="Minimum Roll A [deg]", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.manuv_minrollA_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
        self.manuv_minrollA_entry.insert(0,-30)
        self.manuv_minrollA_entry.bind("<FocusIn>", lambda args: self.manuv_minrollA_entry.delete('0', 'end'))
        self.manuv_minrollA_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)                   

        ttk.Label(rollmanuv_specs_frame, text="Maximum Roll A [deg]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.manuv_maxrollA_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
        self.manuv_maxrollA_entry.insert(0,30)
        self.manuv_maxrollA_entry.bind("<FocusIn>", lambda args: self.manuv_maxrollA_entry.delete('0', 'end'))
        self.manuv_maxrollA_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)          

        ttk.Label(rollmanuv_specs_frame, text="Minimum Roll B [deg]", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.manuv_minrollB_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
        self.manuv_minrollB_entry.insert(0,-30)
        self.manuv_minrollB_entry.bind("<FocusIn>", lambda args: self.manuv_minrollB_entry.delete('0', 'end'))
        self.manuv_minrollB_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)                   

        ttk.Label(rollmanuv_specs_frame, text="Maximum Roll B [deg]", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.manuv_maxrollB_entry = ttk.Entry(rollmanuv_specs_frame, width=10)
        self.manuv_maxrollB_entry.insert(0,30)
        self.manuv_maxrollB_entry.bind("<FocusIn>", lambda args: self.manuv_maxrollB_entry.delete('0', 'end'))
        self.manuv_maxrollB_entry.grid(row=3, column=1, sticky='w', padx=10, pady=10)   
            
    def get_specs(self):
        return {'maneuverType':'Double_Roll_Only', 
                'A_rollMin': float(self.manuv_minrollA_entry.get()), 
                'A_rollMax': float(self.manuv_maxrollA_entry.get()),
                'B_rollMin': float(self.manuv_minrollB_entry.get()), 
                'B_rollMax': float(self.manuv_maxrollB_entry.get())
                }

class PointingOptionsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)         
        popts_frame = ttk.Frame(self) 
        popts_frame.grid(row=0, column=0, ipadx=5, ipady=5)    
        self.popts = None

        def click_popts_data_file_path_btn():
            self.popts_data_fp = tkinter.filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select the pointing-options json file:", filetypes=(("All files","*.*"), ("json files","*.json")))  
            popts_data_fp_entry.configure(state='normal')
            popts_data_fp_entry.delete(0,'end')
            popts_data_fp_entry.insert(0,self.popts_data_fp)
            popts_data_fp_entry.configure(state='disabled')
            # load the data onto a dictionary
            with open(self.popts_data_fp, 'r') as f:
                self.popts = json.load(f)            

        ttk.Button(popts_frame, text="Select Data File", command=click_popts_data_file_path_btn).grid(row=0, column=0, padx=10, pady=5, columnspan=2)
        popts_data_fp_entry=tk.Entry(popts_frame, state='disabled')
        popts_data_fp_entry.grid(row=1,column=0, padx=10, pady=5, sticky='ew', columnspan=2)

    def get_specs(self):
        """ Return the list of imported pointing-options. """           
        return self.popts
class BasicSensorInputConfigure():
    
    def __init__(self, win, tab):
        # parent frame
        specs_frame = ttk.Frame(tab)
        specs_frame.grid(row=0, column=0, padx=10, pady=10)
        specs_frame.rowconfigure(0,weight=1)
        specs_frame.rowconfigure(1,weight=1)
        specs_frame.columnconfigure(0,weight=1)
        specs_frame.columnconfigure(1,weight=1)
        specs_frame.columnconfigure(2,weight=1)
        specs_frame.columnconfigure(3,weight=1)

        # define all child frames

        # other specs frame
        other_specs_frame = ttk.LabelFrame(specs_frame) # specifications other then FOV, maneuver, orientation, synthetic-data frame
        other_specs_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        other_specs_frame.bind('<Enter>',lambda event, widget_id="basicsensor": helpwindow.update_help_window(event, widget_id))
        
        # fov specs frame
        fov_specs_frame = ttk.LabelFrame(specs_frame, text="(Scene) Field-Of-View geometry") # field-of-view (FOV) specifications frame            
        fov_specs_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n') 

        fov_type_frame = ttk.Frame(fov_specs_frame)
        fov_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
        fov_type_frame.columnconfigure(0,weight=1)
        fov_type_frame.rowconfigure(0,weight=1)

        fov_specs_container = ttk.Frame(fov_specs_frame)
        fov_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
        fov_specs_container.columnconfigure(0,weight=1)
        fov_specs_container.rowconfigure(0,weight=1)            

        # select data source frame        
        syndataconfig_frame = ttk.LabelFrame(specs_frame, text="Synthetic Data Configuration") # synthetic data configuration frame
        syndataconfig_frame.grid(row=1, column=1, padx=10, pady=10, sticky='n') 

        # orientation frame
        orien_frame = ttk.LabelFrame(specs_frame, text="Orientation") # sensor orientation frame
        orien_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky='n')

        orien_type_frame = ttk.Frame(orien_frame)
        orien_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
        orien_type_frame.columnconfigure(0,weight=1)
        orien_type_frame.rowconfigure(0,weight=1)

        orien_specs_container = ttk.Frame(orien_frame)
        orien_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
        orien_specs_container.columnconfigure(0,weight=1)
        orien_specs_container.rowconfigure(0,weight=1)

        # manuever frame
        maneuver_frame = ttk.LabelFrame(specs_frame, text="Manuever") # manuver specs frame
        maneuver_frame.grid(row=0, column=3,rowspan=2, padx=10, pady=10, sticky='n')
        maneuver_frame.bind('<Enter>',lambda event, widget_id="maneuver": helpwindow.update_help_window(event, widget_id))

        maneuver_type_frame = ttk.Frame(maneuver_frame)
        maneuver_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
        maneuver_type_frame.columnconfigure(0,weight=1)
        maneuver_type_frame.rowconfigure(0,weight=1)

        maneuver_specs_container = ttk.Frame(maneuver_frame)
        maneuver_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
        maneuver_specs_container.columnconfigure(0,weight=1)
        maneuver_specs_container.rowconfigure(0,weight=1)         

        # pointing-options frame
        popts_frame = ttk.LabelFrame(specs_frame, text="Pointing Options") # manuver specs frame
        popts_frame.grid(row=1, column=2,rowspan=2, padx=10, pady=10, sticky='n')  

        # ok cancel frame
        okcancel_frame = ttk.Frame(specs_frame)
        okcancel_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10) 

        ############### Other Specs ###############
        # define the widgets in other_specs_frame
        ttk.Label(other_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        uid_entry = ttk.Entry(other_specs_frame, width=10)
        uid_entry.insert(0, random.randint(0,100))
        uid_entry.bind("<FocusIn>", lambda args: uid_entry.delete('0', 'end'))
        uid_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Name", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        name_entry = ttk.Entry(other_specs_frame, width=10)
        name_entry.insert(0,"Atom")
        name_entry.bind("<FocusIn>", lambda args: name_entry.delete('0', 'end'))
        name_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Mass [kg]", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        mass_entry = ttk.Entry(other_specs_frame, width=10)
        mass_entry.insert(0,28)
        mass_entry.bind("<FocusIn>", lambda args: mass_entry.delete('0', 'end'))
        mass_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Volume [m3]", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        vol_entry = ttk.Entry(other_specs_frame, width=10)
        vol_entry.insert(0,0.12)
        vol_entry.bind("<FocusIn>", lambda args: vol_entry.delete('0', 'end'))
        vol_entry.grid(row=3, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Power [W]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        pow_entry = ttk.Entry(other_specs_frame, width=10)
        pow_entry.insert(0,32)
        pow_entry.bind("<FocusIn>", lambda args: pow_entry.delete('0', 'end'))
        pow_entry.grid(row=4, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Bits per pixel", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        bpp_entry = ttk.Entry(other_specs_frame, width=10)
        bpp_entry.insert(0,8)
        bpp_entry.bind("<FocusIn>", lambda args: bpp_entry.delete('0', 'end'))
        bpp_entry.grid(row=5, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Data Rate [Megabits-per-sec]", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
        dr_entry = ttk.Entry(other_specs_frame, width=10)
        dr_entry.insert(0,250)
        dr_entry.bind("<FocusIn>", lambda args: dr_entry.delete('0', 'end'))
        dr_entry.grid(row=6, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Number of detector rows", wraplength=150).grid(row=7, column=0, padx=10, pady=10, sticky='w')
        numdetrows_entry = ttk.Entry(other_specs_frame, width=10)
        numdetrows_entry.insert(0,5)
        numdetrows_entry.bind("<FocusIn>", lambda args: numdetrows_entry.delete('0', 'end'))
        numdetrows_entry.grid(row=7, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(other_specs_frame, text="Number of detector columns", wraplength=150).grid(row=8, column=0, padx=10, pady=10, sticky='w')
        numdetcols_entry = ttk.Entry(other_specs_frame, width=10)
        numdetcols_entry.insert(0,5)
        numdetcols_entry.bind("<FocusIn>", lambda args: numdetcols_entry.delete('0', 'end'))
        numdetcols_entry.grid(row=8, column=1, sticky='w', padx=10, pady=10)

        ############### Synthetic Data Configuration ###############
        # define the widgets in syndataconfig_frame
        self.sdc_fr = SyntheticDataConfigurationFrame(parent=syndataconfig_frame, controller=self)
        self.sdc_fr.grid(row=0, column=0, sticky="nsew")

        ############### Pointing Options ###############
        # define the widgets in popts_frame
        self.po_fr = PointingOptionsFrame(parent=popts_frame, controller=self)
        self.po_fr.grid(row=0, column=0, sticky="nsew")

        ############### FOV ###############
        # define the widgets in fov_specs_container frame
        fov_specs_container_frames = {}
        for F in (CircularFOVGeometry, RectangularFOVGeometry):
            page_name = F.__name__
            fov_sc_frame = F(parent=fov_specs_container, controller=self)
            fov_specs_container_frames[page_name] = fov_sc_frame
            fov_sc_frame.grid(row=0, column=0, sticky="nsew")
        
        FOV_MODES = [
            ("Circular FOV", "CircularFOVGeometry"),
            ("Rectangular FOV", "RectangularFOVGeometry")
        ]

        # define the widgets in fov_type_frame frame
        self._sen_fov_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._sen_fov_type.set("CircularFOVGeometry") # initialize

        def senfov_type_rbtn_click():
            if self._sen_fov_type.get() == "CircularFOVGeometry":
                self.fov_sc_frame = fov_specs_container_frames["CircularFOVGeometry"]
            elif self._sen_fov_type.get() == "RectangularFOVGeometry":
                self.fov_sc_frame = fov_specs_container_frames["RectangularFOVGeometry"]
            self.fov_sc_frame.tkraise()

        for text, mode in FOV_MODES:
            fov_type_rbtn = ttk.Radiobutton(fov_type_frame, text=text, command=senfov_type_rbtn_click,
                            variable=self._sen_fov_type, value=mode)
            fov_type_rbtn.pack(anchor='w')

        self.fov_sc_frame = fov_specs_container_frames[self._sen_fov_type.get()]
        self.fov_sc_frame.tkraise()      

        ############### Maneuver ###############
        # define the widgets in maneuver_specs_container
        manuv_specs_container_frames = {}
        for F in (FixedManeuver, CircularManeuver, RollOnlyManeuver, DoubleRollOnlyManeuver):
            page_name = F.__name__
            manuv_sc_frame = F(parent=maneuver_specs_container, controller=self)
            manuv_specs_container_frames[page_name] = manuv_sc_frame
            manuv_sc_frame.grid(row=0, column=0, sticky="nsew")
                        
        # maneuver types child frame
        MANUV_MODES = [
            ("Fixed", "FixedManeuver"),
            ("Circular", "CircularManeuver"),
            ("Roll-only", "RollOnlyManeuver"),
            ("Double Roll-only", "DoubleRollOnlyManeuver")
        ]

        # define the widgets in maneuver_type_frame
        self._sen_manuv_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._sen_manuv_type.set("FixedManeuver") # initialize

        def senmanuv_type_rbtn_click():
            if self._sen_manuv_type.get() == "FixedManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["FixedManeuver"]
            elif self._sen_manuv_type.get() == "CircularManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["CircularManeuver"]
            elif self._sen_manuv_type.get() == "RollOnlyManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["RollOnlyManeuver"]
            elif self._sen_manuv_type.get() == "DoubleRollOnlyManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["DoubleRollOnlyManeuver"]
            self.manuv_sc_frame.tkraise()

        ttk.Label(maneuver_type_frame, text="(All maneuvers specified in NADIR_POINTING frame.)", wraplength=250).pack(anchor='w')

        for text, mode in MANUV_MODES:
            senmanuv_type_rbtn = ttk.Radiobutton(maneuver_type_frame, text=text, command=senmanuv_type_rbtn_click,
                            variable=self._sen_manuv_type, value=mode)
            senmanuv_type_rbtn.pack(anchor='w')        

        self.manuv_sc_frame = manuv_specs_container_frames[self._sen_manuv_type.get()]
        self.manuv_sc_frame.tkraise()    

        ############### Orientation ###############
        # define the widgets in orien_specs_container frame
        orien_specs_container_frames = {}
        for F in (NadirOrientation, SideLookOrientation, XYZOrientation):
            page_name = F.__name__
            orien_sc_frame = F(parent=orien_specs_container, controller=self)
            orien_specs_container_frames[page_name] = orien_sc_frame
            orien_sc_frame.grid(row=0, column=0, sticky="nsew")
                    
        # define widgets in orien_type_frame 
        ORIEN_MODES = [
            ("Nadir-pointing", "NadirOrientation"),
            ("Side-look", "SideLookOrientation"),
            ("X->Y->Z rotations", "XYZOrientation")
        ]

        self._sen_orien_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._sen_orien_type.set("NadirOrientation") # initialize

        def senorien_type_rbtn_click():
            if self._sen_orien_type.get() == "NadirOrientation":
                self.orien_sc_frame = orien_specs_container_frames["NadirOrientation"]
            elif self._sen_orien_type.get() == "SideLookOrientation":
                self.orien_sc_frame = orien_specs_container_frames["SideLookOrientation"]
            elif self._sen_orien_type.get() == "XYZOrientation":
                self.orien_sc_frame = orien_specs_container_frames["XYZOrientation"]
            self.orien_sc_frame.tkraise()

        for text, mode in ORIEN_MODES:
            senorien_type_rbtn = ttk.Radiobutton(orien_type_frame, text=text, command=senorien_type_rbtn_click,
                            variable=self._sen_orien_type, value=mode)
            senorien_type_rbtn.pack(anchor='w')

        self.orien_sc_frame = orien_specs_container_frames[self._sen_orien_type.get()]
        self.orien_sc_frame.tkraise()      

        ############### OK-CANCEL ###############
        # define the widgets in okcancel_frame
        # okcancel frame
        def add_sensor_click():  
            # create window to ask which satellites to attach the sensor to
            select_sat_win = tk.Toplevel()
            select_sat_win_frame = ttk.LabelFrame(select_sat_win, text='Select Satellite(s)')
            select_sat_win_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10) 
            okcancel_frame_2 = ttk.Label(select_sat_win)
            okcancel_frame_2.grid(row=1, column=0, columnspan=2, padx=10, pady=10) 

            orb_specs = config.mission.get_spacecraft_orbit_specs()  # get all available sats in the configuration              

            sat_tree_scroll = ttk.Scrollbar(select_sat_win_frame)
            sat_tree_scroll.grid(row=0, column=1, sticky='nsw')
            sat_tree = ttk.Treeview(select_sat_win_frame, yscrollcommand=sat_tree_scroll.set)
            sat_tree.grid(row=0, column=0, sticky='e')
            sat_tree_scroll.config(command=sat_tree.yview)

            sat_tree['columns'] = ("ID", "Alt", "Inc", "RAAN", "AOP", "TA")
            sat_tree.column('#0', width=0, stretch="no")
            sat_tree.column("ID", width = 80)        
            sat_tree.column("Alt",  width = 80)     
            sat_tree.column("Inc", width = 80)     
            sat_tree.column("RAAN", width = 80)     
            sat_tree.column("AOP",  width = 80)     
            sat_tree.column("TA", width = 80)            

            sat_tree.heading("#0", text="", anchor="w")
            sat_tree.heading("ID", text="ID", anchor="w")
            sat_tree.heading("Alt", text="Altitude [km]", anchor="w")
            sat_tree.heading("Inc", text="Inclination [deg]", anchor="w")
            sat_tree.heading("RAAN", text="RAAN [deg]", anchor="w")
            sat_tree.heading("AOP", text="AOP [deg]", anchor="w")
            sat_tree.heading("TA", text="TA [deg]", anchor="w")

            for k in range(0,len(orb_specs)):
                sat_tree.insert(parent='', index='end', iid=orb_specs[k][0], text="", values=(orb_specs[k][0], orb_specs[k][1], orb_specs[k][2], orb_specs[k][3], orb_specs[k][4], orb_specs[k][5], orb_specs[k][6]))

            def ok_click_2():
                """ Actions upon the click add Sensor followed by selection of satellites. The mission configuration file is updated with the sensors
                    attached to the respective satellites.
                """
                specs = {} 
                specs['name'] = name_entry.get() 
                specs['@id'] = uid_entry.get()
                specs['@type'] = "Basic Sensor"
                specs['volume'] = vol_entry.get()
                specs['mass'] = mass_entry.get()
                specs['power'] = pow_entry.get()
                specs['bitsPerPixel'] = bpp_entry.get()                    
                specs['dataRate'] = dr_entry.get()  
                specs['numberDetectorRows'] = numdetrows_entry.get() 
                specs['numberDetectorCols'] = numdetcols_entry.get()                 
                specs['fieldOfViewGeometry'] = self.fov_sc_frame.get_specs() 
                specs['maneuver'] = self.manuv_sc_frame.get_specs()                
                specs['orientation'] = self.orien_sc_frame.get_specs()
                specs['syntheticDataConfig'] = self.sdc_fr.get_specs() 
                specs['pointingOptions'] = self.po_fr.get_specs() 

                sensor = Instrument.from_dict(specs)
                
                config.mission.add_instrument_to_spacecraft(new_instru=sensor, sensor_to_spc=sat_tree.selection())
                logger.info("Sensor added to spacecraft(s).")
                select_sat_win.destroy()

            ok_btn_2 = ttk.Button(okcancel_frame_2, text="Ok", command=ok_click_2, width=15)
            ok_btn_2.grid(row=0, column=0, sticky ='e')

            cancel_btn_2 = ttk.Button(okcancel_frame_2, text="Exit", command=select_sat_win.destroy, width=15)
            cancel_btn_2.grid(row=0, column=1, sticky ='w') 

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=add_sensor_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=win.destroy, width=15)
        cancel_btn.grid(row=0, column=1) 

class SinglePolarization(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        _frame = ttk.Frame(self) 
        _frame.grid(row=0, column=0)

        # define the widgets 
        ttk.Label(_frame, text="Transmit Pol", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.txpol_entry = ttk.Entry(_frame, width=10)
        self.txpol_entry.insert(0,'H')
        self.txpol_entry.bind("<FocusIn>", lambda args: self.txpol_entry.delete('0', 'end'))
        self.txpol_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(_frame, text="Receive Pol", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.rxpol_entry = ttk.Entry(_frame, width=10)
        self.rxpol_entry.insert(0,'V')
        self.rxpol_entry.bind("<FocusIn>", lambda args: self.rxpol_entry.delete('0', 'end'))
        self.rxpol_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

    def get_specs(self):
        return {"txPol": self.txpol_entry.get(), "rxPol": self.rxpol_entry.get()}

class CompactPolarization(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        _frame = ttk.Frame(self) 
        _frame.grid(row=0, column=0)

        # define the widgets 
        ttk.Label(_frame, text="Transmit Pol", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.txpol_entry = ttk.Entry(_frame, width=10)
        self.txpol_entry.insert(0,'RHCP')
        self.txpol_entry.bind("<FocusIn>", lambda args: self.txpol_entry.delete('0', 'end'))
        self.txpol_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(_frame, text="Receive Pol", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.rxpol_entry = ttk.Entry(_frame, width=10)
        self.rxpol_entry.insert(0,'H,V')
        self.rxpol_entry.bind("<FocusIn>", lambda args: self.rxpol_entry.delete('0', 'end'))
        self.rxpol_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

    def get_specs(self):
        return {"txPol": self.txpol_entry.get(), "rxPol": self.rxpol_entry.get()}

class DualPolarization(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        _frame = ttk.Frame(self) 
        _frame.grid(row=0, column=0)

        # define the widgets 
        ttk.Label(_frame, text="Transmit Pol", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.txpol_entry = ttk.Entry(_frame, width=10)
        self.txpol_entry.insert(0,'H,V')
        self.txpol_entry.bind("<FocusIn>", lambda args: self.txpol_entry.delete('0', 'end'))
        self.txpol_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        ttk.Label(_frame, text="Receive Pol", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.rxpol_entry = ttk.Entry(_frame, width=10)
        self.rxpol_entry.insert(0,'H,V')
        self.rxpol_entry.bind("<FocusIn>", lambda args: self.rxpol_entry.delete('0', 'end'))
        self.rxpol_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

        def pulse_config_rbtn_click():
            if(self.pulseconfigvar.get()==2):
                self.pulsesep_entry.config(state='normal') # SMAP dual-pol pulse-config chosen
            else:
                self.pulsesep_entry.config(state='disabled')

        self.pulseconfigvar = tk.IntVar()
        ttk.Label(_frame, text="Pulse Config", wraplength=150).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        ttk.Radiobutton(_frame, text="AIRSAR", value=1, variable=self.pulseconfigvar, command=pulse_config_rbtn_click).grid(row=3, column=0, padx=10, pady=10,)
        ttk.Radiobutton(_frame, text="SMAP", value=2, variable=self.pulseconfigvar, command=pulse_config_rbtn_click).grid(row=3, column=1, padx=10, pady=10,)
        ttk.Label(_frame, text="Pulse Seperation [us]").grid(row=4, column=0)
        self.pulsesep_entry = ttk.Entry(_frame, width=10)
        self.pulsesep_entry.grid(row=4, column=1)
        self.pulsesep_entry.insert(0,9)
        self.pulsesep_entry.bind("<FocusIn>", lambda args: self.pulsesep_entry.delete('0', 'end'))
        self.pulsesep_entry.config(state='disabled')

    def get_specs(self):
        if(self.pulseconfigvar.get()==2):
            return {"txPol": self.txpol_entry.get(), "rxPol": self.rxpol_entry.get(), "pulseConfig": 'SMAP', "pulseSeparation": self.pulsesep_entry.get()}
        else:
            return {"txPol": self.txpol_entry.get(), "rxPol": self.rxpol_entry.get(), "pulseConfig": 'AIRSAR'}

class SyntheticApertureRadarInputConfigure():

    def __init__(self, win, tab):
        # parent frame
        specs_frame = ttk.Frame(tab)
        specs_frame.grid(row=0, column=0, padx=10, pady=10)
        specs_frame.rowconfigure(0,weight=1)
        specs_frame.rowconfigure(1,weight=1)
        specs_frame.columnconfigure(0,weight=1)
        specs_frame.columnconfigure(1,weight=1)
        specs_frame.columnconfigure(2,weight=1)
        specs_frame.columnconfigure(3,weight=1)

        # define all child frames

        # other specs frame
        other_specs_frame = ttk.LabelFrame(specs_frame) # specifications other then polarization, swath, maneuver, orientation frame
        other_specs_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        other_specs_frame.bind('<Enter>',lambda event, widget_id="basicsensor": helpwindow.update_help_window(event, widget_id))
        
        # pol specs frame
        pol_specs_frame = ttk.LabelFrame(specs_frame, text="Polarization") # Polarization specifications frame            
        pol_specs_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n') 

        pol_type_frame = ttk.Frame(pol_specs_frame)
        pol_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
        pol_type_frame.columnconfigure(0,weight=1)
        pol_type_frame.rowconfigure(0,weight=1)

        pol_specs_container = ttk.Frame(pol_specs_frame)
        pol_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
        pol_specs_container.columnconfigure(0,weight=1)
        pol_specs_container.rowconfigure(0,weight=1)            

        # swath config frame        
        swath_specs_frame = ttk.LabelFrame(specs_frame, text="Swath Configuration") # Swath Configuration frame            
        swath_specs_frame.grid(row=1, column=1, padx=10, pady=10, sticky='n') 

        # orientation frame
        orien_frame = ttk.LabelFrame(specs_frame, text="Orientation") # sensor orientation frame
        orien_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky='n')

        orien_type_frame = ttk.Frame(orien_frame)
        orien_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
        orien_type_frame.columnconfigure(0,weight=1)
        orien_type_frame.rowconfigure(0,weight=1)

        orien_specs_container = ttk.Frame(orien_frame)
        orien_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
        orien_specs_container.columnconfigure(0,weight=1)
        orien_specs_container.rowconfigure(0,weight=1)

        # manuver frame
        maneuver_frame = ttk.LabelFrame(specs_frame, text="Manuever") # manuver specs frame
        maneuver_frame.grid(row=0, column=3,rowspan=2, padx=10, pady=10, sticky='n')
        maneuver_frame.bind('<Enter>',lambda event, widget_id="maneuver": helpwindow.update_help_window(event, widget_id))

        maneuver_type_frame = ttk.Frame(maneuver_frame)
        maneuver_type_frame.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)
        maneuver_type_frame.columnconfigure(0,weight=1)
        maneuver_type_frame.rowconfigure(0,weight=1)

        maneuver_specs_container = ttk.Frame(maneuver_frame)
        maneuver_specs_container.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)
        maneuver_specs_container.columnconfigure(0,weight=1)
        maneuver_specs_container.rowconfigure(0,weight=1)            

        # ok cancel frame
        okcancel_frame = ttk.Frame(specs_frame)
        okcancel_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10) 

        # define the widgets in the child frames

        # define the widgets in pol frame
        pol_specs_container_frames = {}
        for F in (SinglePolarization, CompactPolarization, DualPolarization):
            page_name = F.__name__
            pol_sc_frame = F(parent=pol_specs_container, controller=self)
            pol_specs_container_frames[page_name] = pol_sc_frame
            pol_sc_frame.grid(row=0, column=0, sticky="nsew")

        POL_MODES = [
            ("Single", "SinglePolarization"),
            ("Compact", "CompactPolarization"),
            ("Dual", "DualPolarization")
        ]

        self._sen_pol_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._sen_pol_type.set("SinglePolarization") # initialize

        def senpol_type_rbtn_click():
            if self._sen_pol_type.get() == "SinglePolarization":
                self.pol_sc_frame = pol_specs_container_frames["SinglePolarization"]
            elif self._sen_pol_type.get() == "CompactPolarization":
                self.pol_sc_frame = pol_specs_container_frames["CompactPolarization"]
            elif self._sen_pol_type.get() == "DualPolarization":
                self.pol_sc_frame = pol_specs_container_frames["DualPolarization"]
            self.pol_sc_frame.tkraise()

        for text, mode in POL_MODES:
            pol_type_rbtn = ttk.Radiobutton(pol_type_frame, text=text, command=senpol_type_rbtn_click,
                            variable=self._sen_pol_type, value=mode)
            pol_type_rbtn.pack(anchor='w')

        self.pol_sc_frame = pol_specs_container_frames[self._sen_pol_type.get()]
        self.pol_sc_frame.tkraise()   

        # define the widgets in swathconfig frame           
        def swath_config_rbtn_click():
            if(self.swathconfigvar.get()==2):
                self.fixedswathwidth_entry.config(state='normal') # SMAP dual-pol pulse-config chosen
            else:
                self.fixedswathwidth_entry.config(state='disabled')

        self.swathconfigvar = tk.IntVar()
        ttk.Radiobutton(swath_specs_frame, text="Full", value=1, variable=self.swathconfigvar, command=swath_config_rbtn_click).grid(row=0, column=0, padx=10, pady=10)
        ttk.Radiobutton(swath_specs_frame, text="Fixed", value=2, variable=self.swathconfigvar, command=swath_config_rbtn_click).grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(swath_specs_frame, text="Fixed Swath Width [km]").grid(row=1, column=0, padx=10, pady=10)
        self.fixedswathwidth_entry = ttk.Entry(swath_specs_frame, width=10)
        self.fixedswathwidth_entry.grid(row=1, column=1)
        self.fixedswathwidth_entry.insert(0,25)
        self.fixedswathwidth_entry.bind("<FocusIn>", lambda args: self.fixedswathwidth_entry.delete('0', 'end'))
        self.fixedswathwidth_entry.config(state='disabled')

         # define the widgets in maneuver_frame
        manuv_specs_container_frames = {}
        for F in (FixedManeuver, CircularManeuver, RollOnlyManeuver, DoubleRollOnlyManeuver):
            page_name = F.__name__
            manuv_sc_frame = F(parent=maneuver_specs_container, controller=self)
            manuv_specs_container_frames[page_name] = manuv_sc_frame
            manuv_sc_frame.grid(row=0, column=0, sticky="nsew")
                        
        # constellation types child frame
        MANUV_MODES = [
            ("Fixed", "FixedManeuver"),
            ("Circular", "CircularManeuver"),
            ("Roll-only", "RollOnlyManeuver"),
            ("Double Roll-only", "DoubleRollOnlyManeuver")
        ]

        self._sen_manuv_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._sen_manuv_type.set("FixedManeuver") # initialize

        def senmanuv_type_rbtn_click():
            if self._sen_manuv_type.get() == "FixedManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["FixedManeuver"]
            elif self._sen_manuv_type.get() == "CircularManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["CircularManeuver"]
            elif self._sen_manuv_type.get() == "RollOnlyManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["RollOnlyManeuver"]
            elif self._sen_manuv_type.get() == "DoubleRollOnlyManeuver":
                self.manuv_sc_frame = manuv_specs_container_frames["DoubleRollOnlyManeuver"]
            self.manuv_sc_frame.tkraise()

        for text, mode in MANUV_MODES:
            senmanuv_type_rbtn = ttk.Radiobutton(maneuver_type_frame, text=text, command=senmanuv_type_rbtn_click,
                            variable=self._sen_manuv_type, value=mode)
            senmanuv_type_rbtn.pack(anchor='w')

        self.manuv_sc_frame = manuv_specs_container_frames[self._sen_manuv_type.get()]
        self.manuv_sc_frame.tkraise()    

        # define the widgets in orien_frame
        orien_specs_container_frames = {}
        for F in (NadirOrientation, SideLookOrientation, XYZOrientation):
            page_name = F.__name__
            orien_sc_frame = F(parent=orien_specs_container, controller=self)
            orien_specs_container_frames[page_name] = orien_sc_frame
            orien_sc_frame.grid(row=0, column=0, sticky="nsew")
            
        # define the widgets inside the child frames
        
        # constellation types child frame
        ORIEN_MODES = [
            ("Nadir", "NadirOrientation"),
            ("Side-look", "SideLookOrientation"),
            ("X->Y->Z rotations", "XYZOrientation")
        ]

        self._sen_orien_type = tk.StringVar() # using self so that the variable is retained even after exit from the function
        self._sen_orien_type.set("NadirOrientation") # initialize

        def senorien_type_rbtn_click():
            if self._sen_orien_type.get() == "NadirOrientation":
                self.orien_sc_frame = orien_specs_container_frames["NadirOrientation"]
            elif self._sen_orien_type.get() == "SideLookOrientation":
                self.orien_sc_frame = orien_specs_container_frames["SideLookOrientation"]
            elif self._sen_orien_type.get() == "XYZOrientation":
                self.orien_sc_frame = orien_specs_container_frames["XYZOrientation"]
            self.orien_sc_frame.tkraise()

        for text, mode in ORIEN_MODES:
            senorien_type_rbtn = ttk.Radiobutton(orien_type_frame, text=text, command=senorien_type_rbtn_click,
                            variable=self._sen_orien_type, value=mode)
            senorien_type_rbtn.pack(anchor='w')

        self.orien_sc_frame = orien_specs_container_frames[self._sen_orien_type.get()]
        self.orien_sc_frame.tkraise()      
        
        ok_btn = ttk.Button(okcancel_frame, text="Add",  width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=win.destroy, width=15)
        cancel_btn.grid(row=0, column=1) 



class PassiveOpticalScanner():

    def __init__(self, win, tab):
        ttk.Label(tab,  text ="Under dev").grid(column = 0, row = 0, padx = 30, pady = 30)   