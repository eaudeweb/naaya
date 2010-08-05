var map = null;
var mapMarker = null;
var mapCenterLat = "%s", mapCenterLng = "%s", mapCenterZoom = %s;
function handlerLoad() {
	map = new YMap(document.getElementById("map"), %s, new YSize(%s, %s));
	map.drawZoomAndCenter(new YGeoPoint(mapCenterLat, mapCenterLng), mapCenterZoom);
	map.addTypeControl(mapType=[%s]);
	var zp = new YCoordPoint(15,30);
	zp.translate('right','top');
	map.addZoomLong(zp);
	//markers
	mapMarker = new YImage();
	mapMarker.src = "%s";
	mapMarker.size = new YSize(22, 22);
	mapMarker.offsetSmartWindow = new YCoordPoint(6, 11)
	loadXMLDoc('%s/xrjs_simple_feed?key=%s&show=%s', processRequest);
}
function processRequest() {
	var data = xmlhttp.responseText;
	var arrMarkers = trim(data).split('\n');
	for (var i = 0; i < arrMarkers.length; i++) {
		var b = trim(arrMarkers[i]);
		if (b != '') {
			var m = b.split('|');
			lat=parseFloat(m[0]);lng=parseFloat(m[1]);label=m[2].toString();
			createSimpleMarker(map,lat,lng,label,mapMarker);
		}
	}
}
window.onload = handlerLoad;
