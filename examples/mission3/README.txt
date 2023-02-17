This is example of a mission in which the MissionSpecs.json file has been configured and needs to be loaded.

This mission simulates DSHIELD mission, which consists of 3 satellites uniformly spaced in the same orbital plane. The imaging operations are over the entire globe except water, wetlands, urban and frozen (according to the IGBP classification system). 
Prior to loading the MissionSpecs.json file, please change the following fields in the file:

"settings" :: "outDir" -> Filepath to the "mission3" folder as present in your computer.

(The paths in the "outputInfo" field need not be changed. They shall be updated when the mission is executed and saved.)

After making the changes, from the EOSim-GUI open (load) the mission3 folder. The mission configuration and settings are loaded in.
Execute propagation calculator and save.
The coverage calculator can also be executed. (TODO: Although to appears to be buggy.)
The commands file within the RUNxx folders can be loaded from the Operations panel, and visualized as a Cesium JS animation.

RUN001 folder contains the commands for the 1st day of mission. cmd1.2.3.4.json file contains the complete set of commands for the 1st, 2nd, 3rd and 4th quarter of the day. cmd1.2.3 contains the complete set of commands for the 1st, 2nd and 3rd quarter of the day. And so on.
It has been found that the cmd1,2,3,4.json cannot be used (due to the huge data size) for the CesiumJS animations. The cmd1.2.3 can be used in the Mozilla Firefoz browser.

RUN002 folder contains the commands for the 2nd day of mission.

RUN003 folder contains the commands for the 3rd day of mission.