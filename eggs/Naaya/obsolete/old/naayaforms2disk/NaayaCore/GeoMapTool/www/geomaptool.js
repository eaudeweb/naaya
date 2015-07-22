/**
 * Initialize and display the map in engine independent way.
 * @return Nothing
 */
function showMap() {
	checkConfig( "showMap" );
	if( map_engine == "yahoo" ) {
		mapTool = new YGeoMapTool;
	}
	if( map_engine == "google" ) {
		mapTool = new GGeoMapTool;
	}
	mapTool.showMap(center_address, initial_zoom, enableScrollZoom, map_types, initial_map_type);
	for( symbol in symbolImageURLPairArray ) {
		symbolIcons[ "mk_" + symbol ] = mapTool.createIconSymbol( symbolImageURLPairArray[ symbol ] );
	}
}

/**
 * Verifies if the mapping system configuration is correct
 * @param callerMethodName Callee name, to identify in debugging the script
 * @return
 */
function checkConfig( callerMethodName ) {
	if( map_engine != "yahoo" && map_engine != "google" ) {
		throw callerMethodName + ".checkConfig: map_engine does not point to neither 'google' not 'yahoo'";
	}
}


var isSelected = true;
function toggleSelect()
{
  var frm = document.frmFilterMap;
  if(frm != null) {
	  var i;
	  for(i=0; i<frm.elements.length; i++)
	    if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'geo_types:list')
	      frm.elements[i].checked = !isSelected;
	  isSelected = !isSelected;
  }
}

/**
 * Handle the XmlHttpRequest event, parse the result and add the markers on map.
 * Map engine independent.
 * @param req XmlHttpRequest object
 * @return Nothing
 */
function httpDocumentHandler(req) {
	checkConfig( "httpDocumentHandler" );
	try {
		var data = req.responseText;
		var arrMarkers = data.split('$$');
		var num_records = 0;
		for (var i = 0; i < arrMarkers.length; i++) {
			var b = arrMarkers[i];
			if (b != '') {
				var m = b.split('##');
				lat = parseFloat(m[0]);
				lng = parseFloat(m[1]);
				id = m[2].toString();
				label = m[3].toString();
				mapMarker = m[4].toString();
				tooltip = m[5].toString();
				var marker = mapTool.createMarker(lat, lng, tooltip, label, symbolIcons[mapMarker]);
				if( mapTool.markerHash[ mapMarker ] == null ) mapTool.markerHash[ mapMarker ] = new Array();
				mapTool.markerHash[ mapMarker ].push( marker );
				mapTool.addMarkerOnMap(marker);
				num_records++;
			}
		}
	} catch(e) { 
		alert( "Naaya GeoMapTool: Error drawing markers on map:" + e.message)
	};
	mapTool.updateRecordCounter();
	document.body.style.cursor = "default";
}

/**
 * Show on map selected types of locations.
 * Map engine independent.
 * @return Nothing
 */
function showMapLocations() {
	checkConfig( "showMapLocations" );
	mapTool.clearMap();
	mapTool.markerHash = {};
	document.body.style.cursor = "wait";	
	doHttpRequest( server_base_url + "/xrjs_getGeoPoints?" + encodeForm("frmFilterMap"), httpDocumentHandler);
}

function setRecordCounter( value ) {
	document.getElementById('record_counter').innerHTML = value.toString();	
}