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
		$('.administrative_list input:checkbox, .topics_list input:checkbox, .landscape_list input:checkbox,.map_legend input:checkbox').attr('checked', this.checked);
	})
	$('#geo_query').autocomplete(autocomplete_data, {multiple: true});
});

var isSelected = true;
function toggleSelect() {
  var frm = document.frmFilterMap;
  if(frm != null) {
	  var i;
	  for(i=0; i<frm.elements.length; i++)
		if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'geo_types:list')
		  frm.elements[i].checked = !isSelected;
	  isSelected = !isSelected;
  var btn = document.getElementById('checkall');
  if (btn.innerHTML == naaya_map_i18n["Check All"]) {btn.innerHTML = naaya_map_i18n["Uncheck All"]}
  else {btn.innerHTML = naaya_map_i18n["Check All"]}
  }
  startMapRefresh();
}

String.prototype.trim = function(){return
(this.replace(/^[\s\xA0]+/, "").replace(/[\s\xA0]+$/, ""))}

String.prototype.endsWith = function(str)
{return (this.match(str+"$")==str)}

function encode_form_value(value) {
    // uri-encode with "+" for space
    return encodeURIComponent(value).replace(/%20/g, '+');
}

/**
 * Show on map selected types of locations.
 * Map engine independent.
 * @return Nothing
 */

function load_map_points(bounds, callback) {
    clear_custom_balloon();
    setAjaxWait();
    var str_bounds = 'lat_min=' + bounds.lat_min + '&lat_max=' + bounds.lat_max +
        '&lon_min=' + bounds.lon_min + '&lon_max=' + bounds.lon_max;
    var query = document.getElementById('geo_query').value;
    if (query === naaya_map_i18n["Type keywords to filter locations"]) {
        query = "";
    }
    if (query.endsWith(", ")) {
        query = query.slice(0, -2);
    }
    var enc_form = destinet_get_form_data();
    //don't send explanatory text
    enc_form = enc_form.replace(encode_form_value(
                naaya_map_i18n["Type location address"]), "");
    enc_form = enc_form.replace(encode_form_value(
                naaya_map_i18n["Type keywords to filter locations"]), "");
    var url = portal_map_url + "/xrjs_getGeoClusters?" +
              str_bounds + '&' + enc_form + '&geo_query=' + query;
	if (enc_form.indexOf('geo_types') !== -1)
	{
		$.ajax({
			url: url,
			dataType: 'json',
			success: function(data) {
				document.body.style.cursor = "default";
				callback(parse_response_data(data));
			},
			error: function(req) {
				document.body.style.cursor = "default";
				setRecordCounter(0);
				if(console) console.error('error getting map data', req);
			}
		});
	}
	else{
		var response = {'points': {}};
		document.body.style.cursor = "default";
		parse_response_data(response)
	}

    function parse_response_data(response) {
        if(response.error) {
            alert("Error loading points: " + response.error);
        }
        var num_records = 0;
        $.each(response.points, function(i, point) {
            if (point.label === 'cluster') {
                num_records += point.num_records;
            } else {
                num_records++;
            }
        });
        setRecordCounter(num_records);
        update_locations_values(bounds, enc_form, query);
        return response.points;
    }
}

function points_nearby(places, lat, lon, radius) {
    return $.map(places, function(place) {
        if(distance_to(place.lat, place.lon) > radius)
            return;
        if(place.id == "")
            return;
        return place.id;
    });

    function distance_to(lat2, lon2) {
        var dlat = lat2-lat, dlon = lon2-lon;
        return Math.sqrt(dlat*dlat + dlon*dlon);
    }
}

function load_marker_balloon(point_id_list, callback) {
    var point_args = $.map(point_id_list, function(point_id) {
        if(point_id == '') return;
        return "point_id=" + encodeURIComponent(point_id);
    });
    var url = portal_map_url + "/xrjs_getPointBalloon?" + point_args.join('&');

    $.get(url, function(data) {
        callback(data);
    });
}

function destinet_get_form_data(){
	var form_data = new Array();
	$('#filter_map input:checkbox:checked').each(function(){
		form_data[form_data.length] = '&geo_types%3Alist=' + this.value;
	});
	$('.topics_list input:checkbox:checked').each(function(){
		if (this.value != 'on') {
			form_data[form_data.length] = '&topics%3Alist=' + this.value;
		}
	})
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
	
		$('#view_as_list').attr('href', "./list_locations" + req_link);
		$('#map_url').val(portal_map_url + "/" + req_link);
		$('#download_georss').attr('href', "./export_geo_rss" + req_link);
		var form_symbols = form.symbols.value.split(',');
		var req_symbols = enc_form;
		$('#view_in_google_earth').attr('href', "./downloadLocationsKml?" +
		       req_symbols + "&geo_query=" + query);
	}

	notify_contacts_csv(bounds, query, enc_form);

	var map_info = map_engine.get_center_and_zoom();
	var map_params = "?lat_center=" + map_info.lat_center +
		"&lon_center=" + map_info.lon_center +
		"&map_zoom=" + map_info.map_zoom +
		"&map_engine=" + naaya_map_engine.name +
		"&base_layer=" + map_engine.get_map_layer() +
		enc_form +
		"&geo_query=" + query;
	$('#map_url').attr('value', portal_map_url + map_params);
}

function notify_contacts_csv(bounds, query, enc_form) {
	var form = document.getElementById('list_locations_form');
	if(form === null) return;
	var filter_map = document.getElementById('filter_map');
	if (filter_map != null) {
		var req_link = "?lat_min=" + bounds.lat_min +
			"&lat_max=" + bounds.lat_max +
			"&lon_min=" + bounds.lon_min +
			"&lon_max=" + bounds.lon_max +
			"&geo_types=" + form.symbols.value +
			enc_form +
			"&geo_query=" + query;

		$('#download_contacts_csv').attr('href',
            "./export_csv" + req_link + "&meta_type=Naaya Contact");
	}
}

function setAjaxWait() {
	document.body.style.cursor = "wait";
	var rec_counter = document.getElementById('record_counter');
	if (rec_counter) {
		rec_counter.innerHTML = "";
		var wait_gif = document.createElement('img');
		wait_gif.src = "../misc_/NaayaCore/progress.gif";
		rec_counter.appendChild(wait_gif);
	}
}

function setRecordCounter( value ) {
	var rec_counter = document.getElementById('record_counter');
	if (rec_counter) { rec_counter.innerHTML = value.toString(); }
}

function findAddress(evt) {
	if(evt) evt.preventDefault();
	mapCenterLoc = document.getElementById('address').value;
	if (mapCenterLoc != '') {
		map_engine.go_to_address(mapCenterLoc);
	}
}

function handleKeyPress(elem, key) {
	if (key.keyCode == 13) { 
		if (elem.id == 'address') {findAddress(); return false;}
		if (elem.id == 'geo_query') {startMapRefresh(); return false;}
	}
}

function startMapRefresh() {
	if ($('input[name="geo_types:list"]:checked').length == 0){
		var alert_msg = gettext('Please select at least one category to display on the map');
		alert(alert_msg);
	}
	else{
		setAjaxWait();
		map_engine.refresh_points();
	}
}

function toggleChildren(elem) {
	li = elem.parentNode;
	children = li.getElementsByTagName('li');
	for (var i=0;i<children.length;i++) {
		children[i].getElementsByTagName('input')[0].checked = elem.checked;
	}
	// startMapRefresh();
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
	address.value = naaya_map_i18n["Type location address"];
	address.style.color = "#ccc";
	address.onfocus = function() {
		if (this.value === naaya_map_i18n["Type location address"]) {
			this.value = "";
		}
		this.style.color = "#000";
	}
	if (!geo_query.value) {
		geo_query.value = naaya_map_i18n["Type keywords to filter locations"];
		geo_query.style.color = "#ccc";
	}
	geo_query.onfocus = function() {
		if (this.value === naaya_map_i18n["Type keywords to filter locations"]) {
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

function custom_balloon(lat, lon, content) {
    clear_custom_balloon();
    var map_jq = $('#map');
    var css = {
        position: 'absolute',
        border: '2px solid #999',
        background: 'white',
        padding: '5px',
        'z-index': 1000
    };
    var point_position = map_engine.page_position(lat, lon);
    css.left = point_position.x + map_jq.position().left - 70;
    css.top = map_jq.offset().top + point_position.y;

    var balloon = $('<div>').css(css);
    var close_button = $('<a>[' + naaya_map_i18n["close"] + ']</a>').css({color: '#999', float: 'right'});
    close_button.click(function(){ clear_custom_balloon(); });
    balloon.append(close_button, $('<div>').html(content));
    map_jq.parent().append(balloon);

    clear_custom_balloon = function() { balloon.remove(); }
}
var clear_custom_balloon = function() {}

function onclickpoint(lat, lon, point_id, point_tooltip) {
    if (point_id === '') {
        map_engine.set_center_and_zoom_in(lat, lon);
    } else {
        var current_places = map_engine.get_current_places();
        var points = points_nearby(current_places, lat, lon, 0.0001);
        load_marker_balloon(points, function(html) {
            custom_balloon(lat, lon, html);
        });
    }
}

// can be overwritten to get notifications for the mouse over events
function onmouseoverpoint(lat, lon, point_id, point_tooltip) {}

