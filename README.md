# Earth Observation Simulator (EOSim)

## Install

Requires: Unix-like operating system (requirement of `orbitpy`), `python 3.8`, `pip`, `orbitpy`, `instrupy`, `cartopy`, `metpy`, `scipy` and `astropy`.

Run the application using the following command from terminal:
```
python bin/eosimapp.py
```

## Cesium App 
The Cesium JavaScript app is based on the showcased example of Cesium features in the *cesium-workshop* repository. It is contained in the `.\cesium_app\` folder. 

The original `index.html` file has been modified, while the original cesium-workshop `index.html` file has been retained under the name 
`workshop_index.html`.

A new `eosimApp.js` javascript source file has been added (based on the available `App.js` source file). This source file is the one being executed. (Refer to `<script src="Source/eosimApp.js"></script>` in the `index.html` file.)

The interface with this app is through CZML files. A new CZML file is produced based on the mission processed in EOSim. This file is saved in the
location `cesium_app/Source/SampleData/`. 

The `simple.czml` file in `cesium_app/Source/SampleData/` is a new addition which was not there in the cesium-workshop repo. 

**Note:** The cesium-app needs to be updated each time a new version is released by updating the `<script src=>` and the `<link href=>` 
tags in the 'cesium_app/index.html` file. 

- [ ] TODO: Add facility to input user Access-token. Current version relies on the default Cesium token.

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

