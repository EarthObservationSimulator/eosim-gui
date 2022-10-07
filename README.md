# Earth Observation Simulator Graphical User Interface (EOSim-GUI)

A Graphical User Interface to the OrbitPy and InstruPy packages.

## Install

Requires: Unix-like operating system (requirement of `orbitpy`), `python 3.8`, `pip`, `orbitpy`, `instrupy`, `cartopy`, `metpy` and `scipy`.

CartoPy must be first installed separately. Note that CartoPy has several dependencies whose installation procedure may be different depending on the underlying operating system. Please check [here](https://scitools.org.uk/cartopy/docs/latest/installing.html)

If `conda` is being utilized, then CartoPy installation is simple and can be done using the command:
```
conda install -c conda-forge cartopy
```

After CartoPy installation, run the following command in the main repo directory:
```
make
```

Run the application using the following command from terminal:
```
python bin/eosimapp.py
```

CesiumJs is used for producing 3D animations. Please see the 'Cesium App' for details on updating access token and the link to the Cesium script.
### Troubleshooting
In some cases, *runtime* errors involving the numpy package such as the one below may ensue:
```
module compiled against API version 0xf but this version of numpy is 0xe
```

This may be due to incompatile numpy package installation.
Please run the below command to fix it:
```
pip install numpy --upgrade --ignore-installed
```

The following error is also related to the `numpy` error described above:
```
ImportError: you must compile the Fortran code first. f2py -m lowtran7 -c lowtran7.f  numpy.core.multiarray failed to import
```
It occurs when `eosim-gui` tries to import the `instrupy` package. 
Further the `instrupy` package tests also fail after the `eosim-gui` package installation.
The error can be fixed by re-installing `numpy` with the command given above.

### Known Issues
If Windows Subsystem for Linux 2 (WSL2) is being used, the animation display using CesiumJs does not work properly. The following error is displayed:
```
tcgetpgrp failed: Not a tty
```

Running the following command removes the error (atleast from display) (See [here](https://pythonshowcase.com/question/using-plotly-in-wsl-changes-the-font-console-window-changes-to-raster-and-wont-work-at-all-in-vscode)).
```
export BROWSER="/mnt/c/path/to/browser.exe"
```

Example:
```
export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
```

## Cesium App 
The Cesium JavaScript app is based on the showcased example of Cesium features in the [cesium-workshop repository](https://github.com/CesiumGS/cesium-workshop). It is contained in the `.\cesium_app\` folder. 

The original `index.html` file has been modified, while the original cesium-workshop `index.html` file has been retained under the name 
`workshop_index.html`.

A new `eosimApp.js` javascript source file has been added (based on the available `App.js` source file). This source file is the one being executed. (Refer to `<script src="Source/eosimApp.js"></script>` in the `index.html` file.)

The interface with this app is through CZML files. A new CZML file is produced based on the mission processed in EOSim. This file is saved in the
location `cesium_app/Source/SampleData/`. 

The `simple.czml` file in `cesium_app/Source/SampleData/` is a new addition which was not there in the cesium-workshop repo. 

**Note:** The cesium-app needs to be updated each time a new version is released by updating the `<script src=>` and the `<link href=>` 
tags in the 'cesium_app/index.html` file. 

**Note:** A access token must be specified in the `eosimApp.js` file. A free token can be obtained by registering at https://cesium.com

- [ ] TODO: Add facility to input user Access-token. Current version relies on the default Cesium token.

## Documentation 

Documentation about the code base is available in the `docs/eosim-gui_codebase.pptx` presentation.

The `Commands File Schema.docx` contains the schema definition for the commands file which can be used to animate spacecraft operations.

The file structure is as below:

```
│   .gitignore
│   debug.log
│   LICENSE
│   Makefile
│   README.md
│   setup.py
│
│
├───bin
│        eosimapp.py
│
├───cesium_app
│   │   .gitignore
│   │   index.css
│   │   index.html
│   │   LICENSE.md
│   │   package-lock.json
│   │   package.json
│   │   README.md
│   │   server.js
│   │   workshop_index.html
│   │
│   └───Source
│       │   App.js
│       │   AppSkeleton.js
│       │   eosimApp.js
│       │
│       ├───Images
│       │       ajax-loader.gif
│       │
│       └───SampleData
│           │   eosim_data.czml
│           │   sampleFlight.czml
│           │   sampleGeocacheLocations.kml
│           │   sampleNeighborhoods.geojson
│           │   simple.czml
│           │   testdata.czml
│           │
│           └───Models
│                   CesiumDrone.gltf
│
├───docs
│      codebase_description.pptx
│	   Commands File Schema.docx
│
├───eosim
    │   config.py
    │   __init__.py
    │
    ├───gui
	    │   executeframe.py
	    │   helpwindow.py
	    │   mainapplication.py
	    │   mapprojections.py
	    │   welcomeframe.py
	    │   __init__.py
	    │
	    ├───configure
	    │   │   cfconstellation.py
	    │   │   cfcoverage.py
	    │   │   cfframe.py
	    │   │   cfgroundstation.py
	    │   │   cfintersatellitecomm.py
	    │   │   cfmission.py
	    │   │   cfpropagate.py
	    │   │   cfsatellite.py
	    │   │   cfsensor.py
	    │   │   __init__.py
	    │
	    ├───help
	    │       cone_maneuver.png
	    │       help_database.json
	    │       mercator_proj.png
	    │       rollonly_maneuver.png
	    │
	    ├───operations
	    │   │   operationsframe.py
	    │   │   __init__.py
	    │   
	    │
	    ├───visualize
	        │   insightsframe.py
	        │   vis2dframe.py
	        │   visglobeframe.py
	        │   vismapframe.py
	        │   visualizeframe.py
	        │   __init__.py
	        │
	        ├───czml_templates
	        │       clock_template.json
	        │       contacts_template.json
	        │       covgrid_pkt_template.json
	        │       ground_station_template.json
	        │ 		observed_gp_template.json
	        │       satellite_template.json
```

## License and Copyright

Copyright 2021 Bay Area Environmental Research Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Credits and Acknowledgments

This work has been funded by grants from the National Aeronautics and Space Administration (NASA) Earth Science Technology Office (ESTO) through the Advanced Information Systems Technology (AIST) Program.

EOSim uses:

- CesiumJS (https://cesium.com/cesiumjs/)
- cesium-workshop (https://github.com/CesiumGS/cesium-workshop)

## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)

