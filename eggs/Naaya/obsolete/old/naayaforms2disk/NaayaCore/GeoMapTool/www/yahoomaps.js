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


//TODO CLEANUP UPPER CODE
/**
 * class YGeoMapTool
 * Description: Wrapper class around the Yahoo Maps implementation.
 */

function YGeoMapTool() {
	this.description = "GeoMap Tool implementation wrapper for Yahoo maps";
	this.markerHash = {};
}

/**
 * Create a marker to be displayed on the map with given attributes.
 * @param lat Geographical latitude
 * @param lng Geographical longitude
 * @param html HTML text that appears in the body of the tooltip ballon
 * @param title Title that appears in the tooltip baloon (like title HTML tag)
 * @param icon Icon symbol for the marker
 * @return Initialized marker
 */
YGeoMapTool.prototype.createMarker = function(lat, lng, html, title, icon) {
	var point = new YGeoPoint(lat, lng);
	var marker = new YMarker(point, icon);
	marker.setSmartWindowColor( "grey" );
	YEvent.Capture(marker, EventsList.MouseClick, function() {
		marker.openSmartWindow(html);
	});
	return marker;
}

/**
 * Clear all the markers (and elements) from the map.
 */
YGeoMapTool.prototype.clearMap = function() {
	map.removeMarkersAll();
}


/**
 * Create a new symbol (icon) to be displayed for markers.
 * @param imageURL URL for the image icon
 * @return an initialized icon symbol.
 */
YGeoMapTool.prototype.createIconSymbol = function(imageURL) {
	icon = new YImage();
	icon.src = imageURL;
	icon.size = new YSize(17, 17);
	icon.offsetSmartWindow = new YCoordPoint(6, 11);
	return icon;
}


/**
 * Add a new marker on the map.
 * @param marker Marker to be added on map (created with createMarker)
 */
YGeoMapTool.prototype.addMarkerOnMap = function(marker) {
	map.addOverlay(marker);
}


/**
 * Initialize and display the map in the page.
 * @param center A location (address type) to center the map on,
 * ex.: Frankfurt, Germany
 * @param zoom Zoom factor for the map
 * @param enableScrollWheelZoom Enable/Disable zooming using mouse scroll wheel
 * and keyboard controls
 * @param map_types An array of map types available for the map.
 * Possible values in array: {"hybrid", "map", satellite"}
 */
YGeoMapTool.prototype.showMap = function(center, zoom, enableScrollWheelZoom, map_types, initial_map_type) {
	map = new YMap(document.getElementById("map"));
	map.drawZoomAndCenter(center, zoom);

	var zp = new YCoordPoint(40,30); zp.translate('right','top');
	map.addPanControl(zp);
	var zp = new YCoordPoint(20,30); zp.translate('right','top');
	map.addZoomLong(zp);

	init_type = YAHOO_MAP_REG;
	if( "hybrid" == initial_map_type ) { init_type = YAHOO_MAP_HYB; }
	if( "satellite" == initial_map_type ) { init_type = YAHOO_MAP_SAT; }
	map.setMapType( init_type );

	var arrLayers = [];
	for( i = 0; i < map_types.length; i++) {
		if( "hybrid" == map_types[ i ] ) { arrLayers[arrLayers.length] = YAHOO_MAP_HYB; }
		if( "map" == map_types[ i ] ) { arrLayers[arrLayers.length] = YAHOO_MAP_REG; }
		if( "satellite" == map_types[ i ] ) { arrLayers[arrLayers.length] = YAHOO_MAP_SAT; }
	}
	if( arrLayers.length > 1 ) {
		map.addTypeControl(mapType=arrLayers);
	}


	if(!enableScrollWheelZoom) {
		map.disableKeyControls();
	}
}

/**
 * Load category from server doing an XMLHTTPRequest to retrieve the points.
 */
YGeoMapTool.prototype.showCategoryServer = function(idCategory, show)
{
	var category = 'mk_' + idCategory;
	// Look first into the cache to see if we didn't already loaded the
	// points for this category
	if( show && this.markerHash[ category ] == null ) {
		// Cache miss, load points from server
		document.body.style.cursor = "wait";
		doHttpRequest( server_base_url + "/xrjs_getGeoPoints?geo_types%3Alist=" + idCategory, httpDocumentHandler);
	} else {
		// We have a cache hit, show them
		this.showCategory(idCategory);
	}
}


/**
 * Show a category, client side. Assumes that markers for this category are
 * already loaded on the client side and are taken directly from marker cache.
 */
YGeoMapTool.prototype.showCategory = function(idCategory)
{
	var category = 'mk_' + idCategory;
	if( this.markerHash[ category ] != null ) {
		markerArr = this.markerHash[ category ];
		for( i = 0; i < markerArr.length; i++ ) {
			var marker = markerArr[ i ];
			if( marker.ishidden() )
			{
				marker.unhide();
			}
			else
			{
				marker.hide();
			}
		}
	}
	this.updateRecordCounter();
}

YGeoMapTool.prototype.updateRecordCounter = function () {
	counter = 0;
	for( key in mapTool.markerHash) {
		var markerArr = mapTool.markerHash[ key ];
		for( i = 0; i < markerArr.length; i++ ) {
			var marker = markerArr[ i ];
			if( !marker.ishidden() ) counter++;
		}
	}
	setRecordCounter( counter );
}



