var map = null;
var mapMarker = null;
var defaultLocality = "%s", defaultZoom = %s;
map = new YMap(document.getElementById("map"), %s, new YSize(%s, %s));
// Display the map centered on given address 
map.addTypeControl(mapType=[%s]);
map.addPanControl();
map.addZoomLong();

function setLatLonValues(lat, lon){
	// set the value of the form fields
	document.getElementById("longitude").value = lon;
	document.getElementById("latitude").value = lat;
}

function handlerLoad() {
	PointLon = document.getElementById('longitude').value;
	PointLat = document.getElementById('latitude').value;
	if (PointLat != '' && PointLon != '') {
		map.drawZoomAndCenter(new YGeoPoint(PointLat, PointLon), 6);
		mcenter = map.getCenterLatLon();
		map.addMarker(mcenter);
		setLatLonValues(mcenter.Lat, mcenter.Lon);
	}else {
		map.drawZoomAndCenter(defaultLocality, defaultZoom);
	}

	YEvent.Capture(map, EventsList.MouseClick, reportPosition);
	function reportPosition(_e, _c){
		var currentGeoPoint = new YGeoPoint( _c.Lat, _c.Lon );
		map.removeMarkersAll();
		map.addMarker(currentGeoPoint);
		setLatLonValues(_c.Lat, _c.Lon);
	}
}

function findAddress() {
	mapCenterLoc = document.getElementById('address').value;
	if (mapCenterLoc != '') {
		map.drawZoomAndCenter(mapCenterLoc, 5);
		YEvent.Capture(map, map.getEventsList().endMapDraw, addCenterMarker);
	}
	function addCenterMarker() {
		map.removeMarkersAll();
		var mcenter = map.getCenterLatLon();
		map.addMarker(mcenter);
		setLatLonValues(mcenter.Lat, mcenter.Lon);
	}
}
window.onload = handlerLoad;
