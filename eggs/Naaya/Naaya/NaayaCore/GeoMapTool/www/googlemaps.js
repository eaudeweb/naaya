/**
 * class GGeoMapTool
 * Description: Wrapper class around the Google Maps implementation.
 */

function GGeoMapTool() {
	this.description = "GeoMap Tool implementation wrapper for Yahoo maps";
	this.geocoder = null;
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
GGeoMapTool.prototype.createMarker = function(lat, lng, html, title, icon) {
	var p = new GLatLng(lat, lng);
    var marker = new GMarker(p, {title:title, icon:icon});
    GEvent.addListener(marker, "click", function() {
      marker.openInfoWindowHtml(html);
    });
    return marker;
}


/**
 * Clear all the markers (and elements) from the map.
 */
GGeoMapTool.prototype.clearMap = function() {
	map.clearOverlays();
}


/**
 * Create a new symbol (icon) to be displayed for markers.
 * @param imageURL URL for the image icon
 * @return an initialized icon symbol.
 */
GGeoMapTool.prototype.createIconSymbol = function(imageURL) {
	var icon = new GIcon(G_DEFAULT_ICON);
	icon.image = imageURL;
	icon.iconSize = new GSize(17, 17);
	icon.iconAnchor = new GPoint(1, 25);
	icon.shadow = "misc_/NaayaCore/shadow.png";
	icon.shadowSize = new GSize(26, 17);
	icon.infoWindowAnchor = new GPoint(5, 1);
	return icon;
}


/**
 * Add a new marker on the map.
 * @param marker Marker to be added on map (created with createMarker)
 */
GGeoMapTool.prototype.addMarkerOnMap = function(marker) {
	map.addOverlay(marker);
}


/**
 * Initialize (if required) and retrieve the geocoder object.
 * @return Geocoder object initialized
 */
GGeoMapTool.prototype.getGeocoder = function() {
	if(!this.geocoder) {
		this.geocoder = new GClientGeocoder();
	}
	return this.geocoder;
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
GGeoMapTool.prototype.showMap = function(center, zoom, enableScrollWheelZoom, map_types, initial_map_type) {
	var arrLayers = [];
	for( i = 0; i < map_types.length; i++) {
		if( "hybrid" == map_types[ i ] ) { arrLayers[arrLayers.length] = G_HYBRID_MAP; }
		if( "map" == map_types[ i ] ) { arrLayers[arrLayers.length] = G_NORMAL_MAP; }
		if( "satellite" == map_types[ i ] ) { arrLayers[arrLayers.length] = G_SATELLITE_MAP; }
	}
	map = new GMap2(document.getElementById("map"), {mapTypes:arrLayers});
	mapNavCtrl = new GSmallMapControl();
	map.addControl( mapNavCtrl )
	if( arrLayers.length > 1 ) {
		mapTypeCtrl = new GMenuMapTypeControl();
		map.addControl( mapTypeCtrl )
	}
	init_type = G_NORMAL_MAP;
	if( "hybrid" == initial_map_type ) { init_type = G_HYBRID_MAP; }
	if( "satellite" == initial_map_type ) { init_type = G_SATELLITE_MAP; }
	map.setMapType( init_type );
	var coord = this.getGeocoder().getLatLng(center, function(point) {
		if(!point) {
			map.setCenter(new GLatLng(45.4419, 1.1419), zoom);
		} else {
			map.setCenter(point, zoom);
		}
	});
	if(enableScrollWheelZoom) {
		map.enableScrollWheelZoom();
	}
}
