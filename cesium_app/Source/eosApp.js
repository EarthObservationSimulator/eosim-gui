(function () {
    "use strict";

    // TODO: Add your ion access token from cesium.com/ion/
    // Cesium.Ion.defaultAccessToken = '<YOUR ACCESS TOKEN HERE>';

    //////////////////////////////////////////////////////////////////////////
    // Creating the Viewer
    //////////////////////////////////////////////////////////////////////////

    var viewer = new Cesium.Viewer('cesiumContainer', {
        scene3DOnly: true,
        selectionIndicator: false,
        baseLayerPicker: false
    });
	
    var czml = new Cesium.CzmlDataSource();
    czml.load("./Source/SampleData/eos_data.czml")


    viewer.dataSources.add(
      czml
    );


	  viewer.camera.flyHome(0);
	


}());