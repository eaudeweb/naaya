#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "YahooMapTool"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA). Portions created by Eau de Web are Copyright (C) 
#2007 by European Environment Agency. All Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#Special thanks to Dragos Chirila (fourhooks.com)

__doc__ = """ """

TEMPLATE_XMLRPC_LOCATIONS_MAP_LOADER = """<script type="text/javascript">
	<!--
	var map = null;
	var mapMarker = null;
	var mapCenterLoc = "%s", mapCenterZoom = %s;
	function handlerLoad() {
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
		loadXMLDoc('%s/xrjs_feed?key=%s&show=%s&query=%s&path=%s', processRequest);
	}
	function processRequest() {
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
				var data = xmlhttp.responseText.split('\\n\\n'), b = '';
				b = trim(data[1]);
				if (b != '') document.getElementById('map_markers').innerHTML = b;
				var arrMarkers = trim(data[0]).split('\\n');
				for (var i = 0; i < arrMarkers.length; i++) {
					var b = trim(arrMarkers[i]);
					if (b != '') {
						var m = b.split('|');
						lat=parseFloat(m[0]);lng=parseFloat(m[1]);id=m[2].toString();label=m[3].toString();mapMarker=m[4].toString();
						mapid = createMarker(map,lat,lng,id,label,eval(mapMarker));
					}
				}
				return true;
			} else {
				alert('There was a problem retrieving the XML data:\\n' + xmlhttp.statusText);
				return false;
			}
		}
	}
	window.onload = handlerLoad;
	// -->
	</script>"""

TEMPLATE_XMLRPC_SIMPLE_MAP_LOADER = """<script type="text/javascript">
	<!--
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
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
				var data = xmlhttp.responseText;
				var arrMarkers = trim(data).split('\\n');
				for (var i = 0; i < arrMarkers.length; i++) {
					var b = trim(arrMarkers[i]);
					if (b != '') {
						var m = b.split('|');
						lat=parseFloat(m[0]);lng=parseFloat(m[1]);label=m[2].toString();
						createSimpleMarker(map,lat,lng,label,mapMarker);
					}
				}
				return true;
			} else {
				alert('There was a problem retrieving the XML data:\\n' + xmlhttp.statusText);
				return false;
			}
		}
	}
	window.onload = handlerLoad;
	// -->
	</script>"""

TEMPLATE_XMLRPC_ADDPICK_MAP_LOADER = """<script type="text/javascript">
	<!--
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
	// -->
	</script>"""

TEMPLATE_XMLRPC_EDITPICK_MAP_LOADER = """<script type="text/javascript">
	<!--
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
	// -->
	</script>"""