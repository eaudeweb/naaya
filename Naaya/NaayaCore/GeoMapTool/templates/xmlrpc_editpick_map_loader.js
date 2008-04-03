var map = null;
var mapMarker = null;
var PointLat = "%s", PointLon = "%s", PointZoom = %s, MapLoc = "%s", MapZoom = %s;
map = new YMap(document.getElementById("map"), %s, new YSize(%s, %s));
map.addTypeControl(mapType=[%s]);
map.addZoomLong();
map.addPanControl();

function handlerLoad() {
	if (PointLat == 0.0 || PointLon == 0.0) {
		map.drawZoomAndCenter(MapLoc, MapZoom);
	} else {
		map.drawZoomAndCenter(new YGeoPoint(PointLat, PointLon), PointZoom);
		map.addMarker(map.getCenterLatLon());
	}

	YEvent.Capture(map, EventsList.MouseClick, reportPosition);
	function reportPosition(_e, _c){
		//map.removeMarkersAll();
		var mapCoordCenter = map.convertLatLonXY(map.getCenterLatLon());
		map.removeMarkersAll();
		var currentGeoPoint = new YGeoPoint( _c.Lat, _c.Lon );
		map.addMarker(currentGeoPoint);
		document.getElementById("longitude").value = _c.Lon;
		document.getElementById("latitude").value = _c.Lat;
	}
}

function findAddress() {
	mapCenterLoc = document.getElementById('address').value;
	if (mapCenterLoc != '') {
		map.drawZoomAndCenter(mapCenterLoc, PointZoom);
		YEvent.Capture(map, map.getEventsList().endMapDraw, addCenterMarker);
	}
	function addCenterMarker() {
		map.removeMarkersAll();
		var mcenter = map.getCenterLatLon();
		map.addMarker(mcenter);
		document.getElementById("longitude").value = mcenter.Lon;
		document.getElementById("latitude").value = mcenter.Lat;
	}
}
window.onload = handlerLoad;
