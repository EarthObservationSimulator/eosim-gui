This mission simulates Landsat, SeaHawk1 and SeaHawk2 spacecraft imaging operations over a rectangular grid defined in the US east-coast.

This is example of a mission in which the MissionSpecs.json file has been configured and needs to be loaded.

Prior to loading the MissionSpecs.json file, please change the following fields in the file:

"settings" :: "outDir" -> Filepath to the "mission2" folder as present in your computer.
 "grid" :: "covGridFilePath" -> Filepath to the "grid.csv" file as present in your computer.

(The paths in the "outputInfo" field need not be changed. They shall be updated when the mission is executed and saved.)

After making the changes, from the EOSim-GUI open (load) the mission2 folder. The mission configuration and settings are loaded in.
Execute propagation and save.
The commands.json file can be loaded from the Operations panel, and visualized as a Cesium JS animation.
