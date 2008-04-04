var map = null;
var mapMarker = null;
var mapCenterLoc = %s, mapCenterZoom = %s;

function window_onload() {
	map = new YMap(document.getElementById("map"), %s, new YSize(%s, %s));
	// Display the map centered on given address 
	map.drawZoomAndCenter(mapCenterLoc, mapCenterZoom);
	map.addTypeControl(mapType=[%s]);
	var zp = new YCoordPoint(40,30);
	zp.translate('right','top');
	map.addPanControl(zp);
	var zp = new YCoordPoint(20,30);
	zp.translate('right','top');
	map.addZoomLong(zp);
	//markers
	%s
	showSelectedLocations();
}

function showSelectedLocations_request_handler()
{
	map.removeMarkersAll();
	var data = xmlhttp.responseText.split('\n\n'), b = '';
	b = trim(data[1]);
	if (b != '') document.getElementById('map_markers').innerHTML = b;
	var arrMarkers = trim(data[0]).split('\n');
	for (var i = 0; i < arrMarkers.length; i++) {
		var b = trim(arrMarkers[i]);
		if (b != '') {
			var m = b.split('|');
			lat = parseFloat(m[0]);
			lng = parseFloat(m[1]);
			id = m[2].toString();
			label = m[3].toString();
			mapMarker = m[4].toString();
			mapid = createMarker(map, lat, lng, id, label, eval(mapMarker));
		}
	}
}

function showSelectedLocations()
{
	ajaxPost('%s/xrjs_getGeoPoints', showSelectedLocations_request_handler, encodeForm('frmFilterMap'));
}

window.onload = window_onload;
