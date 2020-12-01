# Earth Observation Simulator (EOS)




## Install

Requires: `python 3.8`, `gfortran`, `pip`

1. Navigate to the `eos/` directory and run `make`. 
2. Run tests using the `make runtest` command and get the *OK* message.

Find the documentation in: `instruments/instrupy/docs/_build/html/user_json_desc.html`

### Cesium

No need to install/ download the CesiumJS package. The index.html code within the app page refers to the remote cesium source javascript file.

install node.js
https://github.com/nodesource/distributions/blob/master/README.md#debinstall

Using Ubuntu:
```
curl -sL https://deb.nodesource.com/setup_15.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Workshop code (the basic App directory):
https://github.com/CesiumGS/cesium-workshop/tree/basic-app

From within the worshop folder:

Run 

> npm install
> npm start 

(OR)

> python -m http.server 8080


## Examples



## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)

