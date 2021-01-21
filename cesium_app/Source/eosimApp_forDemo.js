(function () {
  var viewer = new Cesium.Viewer("cesiumContainer", {
    shouldAnimate: true,
  });
  
  var panel = document.getElementById("panel");
  
  // Pre-allocate some memory, so we don't re-allocate 30~60 times per second.
  var scratchCartesian = new Cesium.Cartesian3();
  var scratchCartographic = new Cesium.Cartographic();

  var pos;
  var lla;
  var numObs;
  var numGps;  

  Cesium.CzmlDataSource.load("./Source/SampleData/eosim_data.czml").then(function(dataSource) {
    viewer.dataSources.add(dataSource);
    viewer.clock.multiplier = 1;
    
    var entity1 = dataSource.entities.getById("11");
    var entity2 = dataSource.entities.getById("operations");
    if (entity1) {
      // Track our entity with the camera.
      viewer.trackedEntity = entity1;
      viewer.clock.onTick.addEventListener(function(clock) {
  
        // Get the position of our entity at the current time, if possible (otherwise undefined).
        pos = entity1.position.getValue(clock.currentTime, scratchCartesian);
        numObs = entity2.properties["observationCount"].getValue(clock.currentTime, numObs);
        numGps = entity2.properties["gpCount"].getValue(clock.currentTime, numGps);
        if (pos) {
  
          // If position is valid, convert from Cartesian3 to Cartographic.
          lla = Cesium.Cartographic.fromCartesian(pos, Cesium.Ellipsoid.WGS84, scratchCartographic);
  
          // Finally, convert from radians to degrees.
          panel.innerHTML = 
            "Longitude: " + Cesium.Math.toDegrees(lla.longitude).toFixed(2) + " deg" +  "<br />" +
            "Latitude:   " + Cesium.Math.toDegrees(lla.latitude).toFixed(2) + " deg" +  "<br />" +
            "Number of (3s) Observations: " +  numObs + "<br />" +
            "Number of GPs: "+ numGps ;
  
        }
      });
    }
  });
  


}());