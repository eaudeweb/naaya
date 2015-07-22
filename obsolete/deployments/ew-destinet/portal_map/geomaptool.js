$(document).ready(function() {
	$(".category_child").toggle();
	$(".category_title, .category_img").click(function(){
		var img = $(this).parent().children('.category_img');
		if (img.attr('src') == 'misc_/Naaya/plus.gif'){
			img.attr('src', 'misc_/Naaya/minus.gif');
		}
		else {
			img.attr('src', 'misc_/Naaya/plus.gif')
		}
		$(this).siblings('.category_child').toggle();
	});
	$('#master_check_all').click(function(){
		$('.administrative_list input:checkbox, .landscape_list input:checkbox,.map_legend input:checkbox').attr('checked', this.checked);
	})
	$('#geo_query').autocomplete(autocomplete_data, {multiple: true});
});

var map_needs_refresh = false;
var map_refresh_in_progress = false;
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
	mapTool.onMapMove(startMapRefresh);
	cluster_re = /^cluster_\d+$/
	for( symbol in symbolImageURLPairArray ) {
		if (cluster_re.test(symbol)) {
			symbolIcons[ "mk_" + symbol ] = mapTool.createIconSymbol( symbolImageURLPairArray[ symbol ], 32, 32);
		} else {
			symbolIcons[ "mk_" + symbol ] = mapTool.createIconSymbol( symbolImageURLPairArray[ symbol ], 16, 16);
		}
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
  var btn = document.getElementById('checkall');
  if (btn.innerHTML == 'Check All') {btn.innerHTML = 'Uncheck All'}
  else {btn.innerHTML = 'Check All'}
  }
  startMapRefresh();
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
				if (label === 'cluster') {
					var m = /(\d+) location\(s\) inside/.exec(tooltip);
					if (m === null) {
						num_records++;
					} else {
						num_records += parseInt(m[1]);
					}
				} else {
					num_records++;
				}
			}
		}
	} catch(e) {
		alert( "Naaya GeoMapTool: Error drawing markers on map:" + e.message)
	};
	setRecordCounter(num_records);
	document.body.style.cursor = "default";
}

/**
 * Show on map selected types of locations.
 * Map engine independent.
 * @return Nothing
 */

function showMapLocationsHandler(){
	checkConfig( "showMapLocations" );
	mapTool.clearMap();
	clear_custom_balloon();
	mapTool.markerHash = {};
	setAjaxWait();
	var bounds = mapTool.getBounds();
	var str_bounds = 'lat_min=' + bounds.lat_min + '&lat_max=' + bounds.lat_max +
		'&lon_min=' + bounds.lon_min + '&lon_max=' + bounds.lon_max;
	var query = document.getElementById('geo_query').value;
	if (query === "Type keywords") {
		query = "";
	}
	query = query.replace(/,/g, ' ');
	var enc_form = get_form_data();
	if ($.trim(enc_form) != '') {
		//don't send explanatory text
		enc_form = enc_form.replace("Type%20location%20address", "");
		enc_form = enc_form.replace("Type%20keywords", "");
		doHttpRequestNoErrorChecking( server_base_url + "/xrjs_getGeoClusters?" + str_bounds +
				'&'+ enc_form + '&geo_query=' + query, mapRefreshHandler);
	}
	else {
		setRecordCounter(0);
		document.body.style.cursor = "default";
		noMapRefreshNeeded();
	}
	locations_update_notify(bounds, enc_form, query);
	update_locations_values(bounds, enc_form, query);
}

function get_form_data(){
	var form_data = new Array();
	$('#filter_map input:checkbox:checked').each(function(){
		form_data[form_data.length] = '&geo_types%3Alist=' + this.value;
	});
	$('.landscape_list input:checkbox:checked').each(function(){
		if (this.value != 'on') {
			form_data[form_data.length] = '&landscape_type%3Alist=' + this.value;
		}
	})
	$('.administrative_list input:checkbox:checked').each(function(){
		if (this.value != 'on') {
			form_data[form_data.length] = '&administrative_level%3Alist=' + this.value;
		}
	})
	form_data[form_data.length] = '&country=' + $('#country_list').attr('value');
	form_data[form_data.length] = '&path=' + encodeURIComponent($('#path').attr('value'));
	return form_data.join('');
}

var locations_update_observers = [update_locations_values];
function locations_update_register(func) {
	locations_update_observers.push(func);
}
function locations_update_notify(bounds, enc_form, query) {
	for (f_i in locations_update_observers) {
		f = locations_update_observers[f_i];
		f(bounds, enc_form, query);
	}
}

function update_locations_values(bounds, enc_form, query){
	/* update the locations form fields with the new viewport coordinates */
	var form = document.getElementById('list_locations_form');
	form.lat_min.value = bounds.lat_min;
	form.lat_max.value = bounds.lat_max;
	form.lon_min.value = bounds.lon_min;
	form.lon_max.value = bounds.lon_max;
	form.geo_query.value = query;
	var filter_map = document.getElementById('filter_map');
	if (filter_map != null) {
		var symbols = filter_map.getElementsByTagName('input');
		form.symbols.value = "";
		for (var i=0;i<symbols.length;i++){
			if (symbols[i].checked && form.symbols.value.indexOf(symbols[i]) == -1){
				if (form.symbols.value != ""){
					form.symbols.value = form.symbols.value + "," + symbols[i].value;
				}
				else {form.symbols.value = symbols[i].value;}
			}
		}
		var req_link = "?lat_min=" + bounds.lat_min +
				"&lat_max=" + bounds.lat_max +
				"&lon_min=" + bounds.lon_min +
				"&lon_max=" + bounds.lon_max +
				enc_form +
				"&geo_query=" + query;

		var list_locations_link = document.getElementById('view_as_list');
		list_locations_link.href = "./list_locations" + req_link;
		var geo_rss_link = document.getElementById('download_georss');
		geo_rss_link.href = "./export_geo_rss" + req_link;
		var view_ge_link = document.getElementById('view_in_google_earth');
		var form_symbols = form.symbols.value.split(',');
		var req_symbols = ""
		for (var i=0;i<form_symbols.length; i++) {
			req_symbols += ("geo_types=" + form_symbols[i]);
			if (i < form_symbols.length) {
				req_symbols += "&";
			}
		}
		view_ge_link.href = "./downloadLocationsKml?" + enc_form + "&geo_query=" + query;
	}
}

function setAjaxWait() {
	document.body.style.cursor = "wait";
	var rec_counter = document.getElementById('record_counter');
	rec_counter.innerHTML = "";
	var wait_gif = document.createElement('img');
	wait_gif.src = "../misc_/NaayaCore/progress.gif";
	rec_counter.appendChild(wait_gif);
}

function setRecordCounter( value ) {
	document.getElementById('record_counter').innerHTML = value.toString();
}

function findAddress() {
	mapCenterLoc = document.getElementById('address').value;
	if (mapCenterLoc != '') {
		mapTool.drawZoomAndCenter(mapCenterLoc);
	}
}

function handleKeyPress(elem, key) {
	if (key.keyCode == 13) { 
		if (elem.id == 'address') {findAddress(); return false;}
		if (elem.id == 'geo_query') {startMapRefresh(); return false;}
	}
}

function startMapRefresh() {
	if (map_refresh_in_progress) {
		map_needs_refresh = true;
		return;
	}

	map_refresh_in_progress = true;
	setAjaxWait();

	map_needs_refresh = false;
	showMapLocationsHandler();
}

function mapRefreshHandler(req) {
	map_refresh_in_progress = false;
	if (map_needs_refresh) {
		startMapRefresh();
		return
	}

	if (req.status == 200) {
		httpDocumentHandler(req);
	} else {
		setRecordCounter(0);
		document.body.style.cursor = "default";
		alert('Naaya GeoMapTool: there was a problem retrieving the map data:\n' + xmlhttp.statusText);
	}
}

function noMapRefreshNeeded() {
	map_refresh_in_progress = false;
}

function toggleChildren(elem) {
	li = elem.parentNode;
	children = li.getElementsByTagName('li');
	for (var i=0;i<children.length;i++) {
		children[i].getElementsByTagName('input')[0].checked = elem.checked;
	}
}

function displayParentCheckboxes() {
	form = document.getElementById('filter_map');
	if (form != null) {
		form_children = form.childNodes;
		for (var i=0;i<form_children.length;i++) {
			if (form_children[i].tagName == 'LI') {
				form_children[i].getElementsByTagName('input')[0].style.display = "inline"
			}
		}
	}
}

function showPageElements() {
	// set explanatory text in search fields
	var address = document.getElementById('address');
	var geo_query = document.getElementById('geo_query');
	address.value = "Type location address";
	address.style.color = "#ccc";
	address.onfocus = function() {
		if (this.value === "Type location address") {
			this.value = "";
		}
		this.style.color = "#000";
	}
	geo_query.value = "Type keywords";
	geo_query.style.color = "#ccc";
	geo_query.onfocus = function() {
		if (this.value === "Type keywords") {
			this.value = "";
		}
		this.style.color = "#000";
	}

	document.getElementById('checkall').style.display = "inline";
	document.getElementById('js_links').style.display = "block";
	a = document.getElementById('address').readOnly = false;
	document.getElementById('address_button').disabled = false;
	document.getElementById('geo_query_button').disabled = false;
	displayParentCheckboxes();
}

function custom_balloon(point_position, content) {
    clear_custom_balloon();
    var map_jq = $('#map');
    var css = {
        position: 'absolute',
        border: '2px solid #999',
        background: 'white',
        padding: '5px'
    };
    css.left = point_position.left + map_jq.position().left - 70;
    css.top = map_jq.offset().top + point_position.top;

    var balloon = $('<div>').css(css);
    var close_button = $('<a>[close]</a>').css({color: '#999', float: 'right'});
    close_button.click(function(){ clear_custom_balloon(); });
    balloon.append(close_button, $('<div>').html(content));
    map_jq.parent().append(balloon);

    clear_custom_balloon = function() { balloon.remove(); }
}
var clear_custom_balloon = function() {}
