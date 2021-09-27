from tkinter import ttk 
import tkinter as tk
from eosim import config
import orbitpy
import random
import eosim.gui.helpwindow as helpwindow
import logging

logger = logging.getLogger(__name__)

class CfSatellite():

    def click_satellite_btn(self):      

        # create and configure child window, parent frame
        sat_win = tk.Toplevel()

        sat_win.rowconfigure(0,weight=1)
        sat_win.rowconfigure(1,weight=1)
        sat_win.columnconfigure(0,weight=1)

        sat_win_frame =ttk.LabelFrame(sat_win, text="Add Satellite")
        sat_win_frame.grid(row=0, column=0, padx=10, pady=10)

        # define all child frames
        sat_kep_specs_frame = ttk.Frame(sat_win_frame)
        sat_kep_specs_frame.grid(row=0, column=0)
        sat_kep_specs_frame.columnconfigure(0,weight=1)
        sat_kep_specs_frame.columnconfigure(1,weight=1)
        sat_kep_specs_frame.rowconfigure(0,weight=1)
        sat_kep_specs_frame.rowconfigure(1,weight=1)
        sat_kep_specs_frame.rowconfigure(2,weight=1)
        sat_kep_specs_frame.rowconfigure(3,weight=1)
        sat_kep_specs_frame.rowconfigure(4,weight=1)
        sat_kep_specs_frame.rowconfigure(5,weight=1) 
        sat_kep_specs_frame.rowconfigure(6,weight=1)
        sat_kep_specs_frame.rowconfigure(7,weight=1)

        okcancel_frame = ttk.Frame(sat_win_frame)
        okcancel_frame.grid(row=1, column=0)  

        # define the widgets inside the child frames
        ttk.Label(sat_kep_specs_frame, text="Unique ID", wraplength=150).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        uid_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        uid_entry.insert(0, random.randint(0,1000))
        uid_entry.bind("<FocusIn>", lambda args: uid_entry.delete('0', 'end'))
        uid_entry.grid(row=0, column=1, sticky='w')

        ttk.Label(sat_kep_specs_frame, text="Altitude [km]", wraplength=150).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        alt_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        alt_entry.insert(0,500)
        alt_entry.bind("<FocusIn>", lambda args: alt_entry.delete('0', 'end'))
        alt_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(sat_kep_specs_frame, text="Eccentricity", wraplength=150).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.ecc_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        self.ecc_entry.insert(0,0.001)
        self.ecc_entry.bind("<FocusIn>", lambda args: self.ecc_entry.delete('0', 'end'))
        self.ecc_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(sat_kep_specs_frame, text="Inclination [deg]", wraplength=150).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.inc_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        self.inc_entry.insert(0,45)
        self.inc_entry.bind("<FocusIn>", lambda args: self.inc_entry.delete('0', 'end'))
        self.inc_entry.grid(row=3, column=1, sticky='w')
        
        ttk.Label(sat_kep_specs_frame, text="RAAN [deg]", wraplength=150).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        raan_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        raan_entry.insert(0,270)
        raan_entry.bind("<FocusIn>", lambda args: raan_entry.delete('0', 'end'))
        raan_entry.grid(row=4, column=1, sticky='w')

        tk.Label(sat_kep_specs_frame, text="AOP[deg]", wraplength=150).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        aop_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        aop_entry.insert(0,270)
        aop_entry.bind("<FocusIn>", lambda args: aop_entry.delete('0', 'end'))
        aop_entry.grid(row=5, column=1, sticky='w')

        tk.Label(sat_kep_specs_frame, text="TA [deg]", wraplength=150).grid(row=6, column=0, padx=10, pady=10, sticky='w')
        ta_entry = ttk.Entry(sat_kep_specs_frame, width=10)
        ta_entry.insert(0,10)
        ta_entry.bind("<FocusIn>", lambda args: ta_entry.delete('0', 'end'))
        ta_entry.grid(row=6, column=1, sticky='w')

        def checked_sso():
            if(self.cir_sso_alt_fix_var.get() == 1):
                self.ecc_entry.delete('0','end')
                self.ecc_entry.insert(0,0)
                self.ecc_entry.configure(state="disabled")
                self.inc_entry.delete('0','end')
                self.inc_entry.configure(state="disabled")
            else:
                self.ecc_entry.configure(state="normal")
                self.inc_entry.configure(state="normal")
                
        self.cir_sso_alt_fix_var = tk.IntVar()
        circularSSOAltitudeFixed_chkbox= ttk.Checkbutton(sat_kep_specs_frame, text='Circular SSO, Altitude Fixed',variable=self.cir_sso_alt_fix_var, onvalue=1, offvalue=0, command=checked_sso)
        circularSSOAltitudeFixed_chkbox.grid(row=7, column=0, sticky='w')

        # okcancel frame
        def ok_click():            
            if(self.cir_sso_alt_fix_var.get() == 1):
                inc = orbitpy.util.calculate_inclination_circular_SSO(float(alt_entry.get()))                
                self.inc_entry.configure(state="normal")
                self.inc_entry.delete('0','end')
                self.inc_entry.insert(0,inc)
                self.inc_entry.configure(state="disabled")
                logger.info("SSO with circular orbit, fixed altitude was enabled.")
                logger.info("Inclination of the SSO orbit is: " + str(inc) + "deg")

            try:
                date_dict = orbitpy.util.OrbitState.date_to_dict(config.mission.epoch)
            except:
                logger.info("Please set the mission date before adding satellite.")
                return
            orbitState_dict = {'date': date_dict,
                               'state': {'@type': 'KEPLERIAN_EARTH_CENTERED_INERTIAL', 
                                         'sma': float(alt_entry.get())+orbitpy.util.Constants.radiusOfEarthInKM,
                                         'ecc': float(self.ecc_entry.get()), 
                                         'inc': float(self.inc_entry.get()),
                                         'raan': float(raan_entry.get()), 
                                         'aop': float(aop_entry.get()), 
                                         'ta': float(ta_entry.get())
                                        }
                              }
            satellite_dict = {'name': None, '@id':uid_entry.get(), 'orbitState': orbitState_dict,
                              'spacecraftBus': None, 'instrument': None}

            config.mission.add_spacecraft_from_dict(satellite_dict)
            logger.info("Satellite added.")
            

        ok_btn = ttk.Button(okcancel_frame, text="Add", command=ok_click, width=15)
        ok_btn.grid(row=0, column=0)

        cancel_btn = ttk.Button(okcancel_frame, text="Exit", command=sat_win.destroy, width=15)
        cancel_btn.grid(row=0, column=1)