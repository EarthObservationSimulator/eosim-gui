from tkinter import ttk 
import tkinter as tk       
import cartopy.crs as ccrs
import eosim.gui.helpwindow as helpwindow

class Mercator(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)  
        mercator_proj_frame = ttk.Frame(self) 
        mercator_proj_frame.grid(row=0, column=0, ipadx=5, ipady=5)
        mercator_proj_frame.bind('<Enter>',lambda event, widget_id="mercator_proj": helpwindow.update_help_window(event, widget_id))

        ttk.Label(mercator_proj_frame, text="Central Longitude [deg]", wraplength=150).grid(row=0, column=0, padx=10, sticky='w')
        self.central_longitude_entry = ttk.Entry(mercator_proj_frame, width=10)
        self.central_longitude_entry.insert(0,0)
        self.central_longitude_entry.bind("<FocusIn>", lambda args: self.central_longitude_entry.delete('0', 'end'))
        self.central_longitude_entry.grid(row=0, column=1, sticky='w')

        ttk.Label(mercator_proj_frame, text="Minimum Latitude [deg]", wraplength=150).grid(row=1, column=0, padx=10, sticky='w')
        self.min_latitude_entry = ttk.Entry(mercator_proj_frame, width=10)
        self.min_latitude_entry.insert(0,-80)
        self.min_latitude_entry.bind("<FocusIn>", lambda args: self.min_latitude_entry.delete('0', 'end'))
        self.min_latitude_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(mercator_proj_frame, text="Maximum Latitude [deg]", wraplength=150).grid(row=2, column=0, padx=10, sticky='w')
        self.max_latitude_entry = ttk.Entry(mercator_proj_frame, width=10)
        self.max_latitude_entry.insert(0,84)
        self.max_latitude_entry.bind("<FocusIn>", lambda args: self.max_latitude_entry.delete('0', 'end'))
        self.max_latitude_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(mercator_proj_frame, text="Latitude True Scale [deg]", wraplength=150).grid(row=3, column=0, padx=10, sticky='w')
        self.lat_true_scale_entry = ttk.Entry(mercator_proj_frame, width=10)
        self.lat_true_scale_entry.insert(0,0)
        self.lat_true_scale_entry.bind("<FocusIn>", lambda args: self.lat_true_scale_entry.delete('0', 'end'))
        self.lat_true_scale_entry.grid(row=3, column=1, sticky='w')

        ttk.Label(mercator_proj_frame, text="False Easting [m]", wraplength=150).grid(row=4, column=0, padx=10, sticky='w')
        self.false_easting_entry = ttk.Entry(mercator_proj_frame, width=10)
        self.false_easting_entry.insert(0,0)
        self.false_easting_entry.bind("<FocusIn>", lambda args: self.false_easting_entry.delete('0', 'end'))
        self.false_easting_entry.grid(row=4, column=1, sticky='w')

        ttk.Label(mercator_proj_frame, text="False Northing [m]", wraplength=150).grid(row=5, column=0, padx=10, sticky='w')
        self.false_northing_entry = ttk.Entry(mercator_proj_frame, width=10)
        self.false_northing_entry.insert(0,0)
        self.false_northing_entry.bind("<FocusIn>", lambda args: self.false_northing_entry.delete('0', 'end'))
        self.false_northing_entry.grid(row=5, column=1, sticky='w')

    def get_specs(self):
        return ccrs.Mercator(central_longitude=float(self.central_longitude_entry.get()), 
                                min_latitude=float(self.min_latitude_entry.get()), 
                                max_latitude=float(self.max_latitude_entry.get()), 
                                latitude_true_scale=float(self.lat_true_scale_entry.get()), 
                                false_easting=float(self.false_easting_entry.get()), 
                                false_northing=float(self.false_northing_entry.get()))

class EquidistantConic(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)  
        equidistconic_proj_frame = ttk.Frame(self) 
        equidistconic_proj_frame.grid(row=0, column=0, ipadx=5, ipady=5)
        
        ttk.Label(equidistconic_proj_frame, text="Central Longitude [deg]", wraplength=150).grid(row=0, column=0, padx=10, sticky='w')
        self.central_longitude_entry = ttk.Entry(equidistconic_proj_frame, width=10)
        self.central_longitude_entry.insert(0,0)
        self.central_longitude_entry.bind("<FocusIn>", lambda args: self.central_longitude_entry.delete('0', 'end'))
        self.central_longitude_entry.grid(row=0, column=1, sticky='w')

        ttk.Label(equidistconic_proj_frame, text="Central Latitude [deg]", wraplength=150).grid(row=1, column=0, padx=10, sticky='w')
        self.central_latitude_entry = ttk.Entry(equidistconic_proj_frame, width=10)
        self.central_latitude_entry.insert(0,0)
        self.central_latitude_entry.bind("<FocusIn>", lambda args: self.central_latitude_entry.delete('0', 'end'))
        self.central_latitude_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(equidistconic_proj_frame, text="False Easting [m]", wraplength=150).grid(row=2, column=0, padx=10, sticky='w')
        self.false_easting_entry = ttk.Entry(equidistconic_proj_frame, width=10)
        self.false_easting_entry.insert(0,0)
        self.false_easting_entry.bind("<FocusIn>", lambda args: self.false_easting_entry.delete('0', 'end'))
        self.false_easting_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(equidistconic_proj_frame, text="False Northing [m]", wraplength=150).grid(row=3, column=0, padx=10, sticky='w')
        self.false_northing_entry = ttk.Entry(equidistconic_proj_frame, width=10)
        self.false_northing_entry.insert(0,0)
        self.false_northing_entry.bind("<FocusIn>", lambda args: self.false_northing_entry.delete('0', 'end'))
        self.false_northing_entry.grid(row=3, column=1, sticky='w')

        ttk.Label(equidistconic_proj_frame, text="Standard Parallel(s) [deg]", wraplength=150).grid(row=4, column=0, padx=10, sticky='w')
        self.standard_parallels_entry = ttk.Entry(equidistconic_proj_frame, width=10)
        self.standard_parallels_entry.insert(0,"20,50")
        self.standard_parallels_entry.bind("<FocusIn>", lambda args: self.standard_parallels_entry.delete('0', 'end'))
        self.standard_parallels_entry.grid(row=4, column=1, sticky='w')
    
    def get_specs(self):
        return ccrs.EquidistantConic(central_longitude=float(self.central_longitude_entry.get()), 
                                        central_latitude=float(self.central_latitude_entry.get()), 
                                        false_easting=float(self.false_easting_entry.get()), 
                                        false_northing=float(self.false_northing_entry.get()),
                                        standard_parallels=tuple(map(float, self.standard_parallels_entry.get().split(','))))

class LambertConformal(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)  
        lambertconformal_proj_frame = ttk.Frame(self) 
        lambertconformal_proj_frame.grid(row=0, column=0, ipadx=5, ipady=5)

        ttk.Label(lambertconformal_proj_frame, text="Central Longitude [deg]", wraplength=150).grid(row=0, column=0, padx=10, sticky='w')
        self.central_longitude_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
        self.central_longitude_entry.insert(0,-96)
        self.central_longitude_entry.bind("<FocusIn>", lambda args: self.central_longitude_entry.delete('0', 'end'))
        self.central_longitude_entry.grid(row=0, column=1, sticky='w')

        ttk.Label(lambertconformal_proj_frame, text="Central Latitude [deg]", wraplength=150).grid(row=1, column=0, padx=10, sticky='w')
        self.central_latitude_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
        self.central_latitude_entry.insert(0,39)
        self.central_latitude_entry.bind("<FocusIn>", lambda args: self.central_latitude_entry.delete('0', 'end'))
        self.central_latitude_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(lambertconformal_proj_frame, text="False Easting [m]", wraplength=150).grid(row=2, column=0, padx=10, sticky='w')
        self.false_easting_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
        self.false_easting_entry.insert(0,0)
        self.false_easting_entry.bind("<FocusIn>", lambda args: self.false_easting_entry.delete('0', 'end'))
        self.false_easting_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(lambertconformal_proj_frame, text="False Northing [m]", wraplength=150).grid(row=3, column=0, padx=10, sticky='w')
        self.false_northing_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
        self.false_northing_entry.insert(0,0)
        self.false_northing_entry.bind("<FocusIn>", lambda args: self.false_northing_entry.delete('0', 'end'))
        self.false_northing_entry.grid(row=3, column=1, sticky='w')

        ttk.Label(lambertconformal_proj_frame, text="Standard Parallel(s) [deg]", wraplength=150).grid(row=4, column=0, padx=10, sticky='w')
        self.standard_parallels_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
        self.standard_parallels_entry.insert(0,"33,45")
        self.standard_parallels_entry.bind("<FocusIn>", lambda args: self.standard_parallels_entry.delete('0', 'end'))
        self.standard_parallels_entry.grid(row=4, column=1, sticky='w')

        ttk.Label(lambertconformal_proj_frame, text="Cutoff [deg]", wraplength=150).grid(row=5, column=0, padx=10, sticky='w')
        self.cutoff_entry = ttk.Entry(lambertconformal_proj_frame, width=10)
        self.cutoff_entry.insert(0,-30)
        self.cutoff_entry.bind("<FocusIn>", lambda args: self.cutoff_entry.delete('0', 'end'))
        self.cutoff_entry.grid(row=5, column=1, sticky='w')

    def get_specs(self):
        return ccrs.LambertConformal(central_longitude=float(self.central_longitude_entry.get()), 
                                        central_latitude=float(self.central_latitude_entry.get()), 
                                        false_easting=float(self.false_easting_entry.get()), 
                                        false_northing=float(self.false_northing_entry.get()),
                                        standard_parallels=tuple(map(float, self.standard_parallels_entry.get().split(','))),
                                        cutoff=float(self.cutoff_entry.get()))

class Robinson(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)  
        f = ttk.Frame(self) 
        f.grid(row=0, column=0, ipadx=5, ipady=5)
        ttk.Label(f, text="Robinson Under development").pack() 

class LambertAzimuthalEqualArea(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)  
        f = ttk.Frame(self) 
        f.grid(row=0, column=0, ipadx=5, ipady=5)
        ttk.Label(f, text="LambertAzimuthalEqualArea Under development").pack() 

class Gnomonic(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)  
        f = ttk.Frame(self) 
        f.grid(row=0, column=0, ipadx=5, ipady=5)
        ttk.Label(f, text="Gnomonic Under development").pack() 