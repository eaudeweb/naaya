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
	//Disable key controls zoom/pan
	%s
	//markers
	%s
	showSelectedLocations();
}

var markerHash = new Array();

function showSelectedLocations_request_handler()
{
	document.body.style.cursor = "default";

	map.removeMarkersAll();

	var data = xmlhttp.responseText;
	var p = new Array();
	// put GeoPoints on map
	var arrMarkers = trim(data).split('$$');
	var num_records = 0;
	for (var i = 0; i < arrMarkers.length; i++) {
		var b = trim(arrMarkers[i]);
		if (b != '') {
			var m = b.split('##');
			lat = parseFloat(m[0]);
			lng = parseFloat(m[1]);
			id = m[2].toString();
			label = m[3].toString();
			mapMarker = m[4].toString();
			tooltip = m[5].toString();
			marker = createMarker2(map, lat, lng, id, label, eval(mapMarker), tooltip);
			markerHash[ marker.id ] = mapMarker;
			p.push(marker);
			num_records++;
		}
	}
	for( i = 0; i < p.length; i++)
		map.addOverlay(p[i]);
	document.getElementById('record_counter').innerHTML = num_records.toString();
}

function showCategory( idCategory )
{
	var fullCat = 'mk_' + idCategory;
	var markerArr = map.getMarkerIDs();
	for( i = 0; i < markerArr.length; i++ )
	{
		var marker = map.getMarkerObject(markerArr[ i ]);
		var markerCat = markerHash[ marker.id ];
		if( markerCat == fullCat )
		{
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
}

function showSelectedLocations()
{
	loadXMLDoc('%s/xrjs_getGeoClusters?' + encodeForm('frmFilterMap'), showSelectedLocations_request_handler);
}

window.onload = window_onload;
