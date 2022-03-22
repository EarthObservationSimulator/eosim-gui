This mission simulates Landsat, SeaHawk1 and SeaHawk2 spacecraft imaging operations over a rectangular grid defined in the US east-coast.
Prior to loading the MissionSpecs.json file, please change the following fields in the file:

"settings" :: "outDir" -> Filepath to the "mission2" folder as present in your computer.
 "grid" :: "covGridFilePath" -> Filepath to the "grid.csv" file as present in your computer.

After making the changes, from the EOSim-GUI open (load) the mission2 folder. The mission configuration and settings are loaded in.
Execute propagation and save.
The commands.json file can be loaded from the Operations panel, and visualized as a Cesium JS animation.
