function createMarker(map, lat, lng, id, label, icon) {
	var point = new YGeoPoint(lat, lng);
	var marker = new YMarker(point, icon);
	marker.setSmartWindowColor("grey");
	YEvent.Capture(marker, EventsList.MouseClick, function() { marker.openSmartWindow(document.getElementById(id).innerHTML);});
	return marker.id;
}

function createMarker2(map, lat, lng, id, label, icon, tooltip) {
	var point = new YGeoPoint(lat, lng);
	var marker = new YMarker(point, icon);
	marker.setSmartWindowColor("grey");
	YEvent.Capture(marker, EventsList.MouseClick, function() { marker.openSmartWindow(tooltip.toString());});
	return marker;
}


function createSimpleMarker(map, lat, lng, label, icon) {
	var point = new YGeoPoint(lat, lng);
	var marker = new YMarker(point, icon);
	marker.setSmartWindowColor("grey");
	marker.addAutoExpand(label);
	map.addOverlay(marker);
}

function getScrollXY() {
	var scrOfX = 0, scrOfY = 0;
	if( typeof( window.pageYOffset ) == 'number' ) {
		//Netscape compliant
		scrOfY = window.pageYOffset;
		scrOfX = window.pageXOffset;
	} else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
		//DOM compliant
		scrOfY = document.body.scrollTop;
		scrOfX = document.body.scrollLeft;
	} else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
		//IE6 standards compliant mode
		scrOfY = document.documentElement.scrollTop;
		scrOfX = document.documentElement.scrollLeft;
	}
	return [scrOfX, scrOfY];
}

function showListEntry(mapid, id) {
	var marker = map.getMarkerObject(mapid);
	map.drawZoomAndCenter(marker.YGeoPoint, 1);
	var scrOfY = getScrollXY()[1];
	if (scrOfY > 220) window.scrollTo(0, 220);
	marker.openSmartWindow(document.getElementById(id).innerHTML);
}
