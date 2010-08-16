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
    clear_new_point();
    setAjaxWait();
    var str_bounds = 'lat_min=' + bounds.lat_min + '&lat_max=' + bounds.lat_max +
        '&lon_min=' + bounds.lon_min + '&lon_max=' + bounds.lon_max;
    var query = document.getElementById('geo_query').value;
    if (query === naaya_map_i18n["Type keywords"]) {
        query = "";
    }
    var enc_form = $("form#frmFilterMap").serialize();
    //don't send explanatory text
    enc_form = enc_form.replace(encode_form_value(
                naaya_map_i18n["Type location address"]), "");
    enc_form = enc_form.replace(encode_form_value(
                naaya_map_i18n["Type keywords"]), "");
    var url = portal_url + "/observatory_xrjs_clusters?" +
              str_bounds + '&' + enc_form + '&geo_query=' + query;
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

    function parse_response_data(response) {
        if(response.error) {
            alert("Error loading points: " + response.error);
        }
        var num_records = 0;
        $.each(response.points, function(i, point) {
            if (point.label === 'cluster') {
                var m = /(\d+) location\(s\) inside/.exec(point.tooltip);
                if (m === null) {
                    num_records++;
                } else {
                    num_records += parseInt(m[1]);
                }
            } else {
                num_records++;
            }
        });
        setRecordCounter(num_records);
        update_locations_values(bounds, query);
        return response.points;
    }
}

function load_marker_balloon(latitude, longitude, callback) {
    var query = document.getElementById('geo_query').value;
    if (query === naaya_map_i18n["Type keywords"]) {
        query = "";
    }
    var enc_form = $("form#frmFilterMap").serialize();
    //don't send explanatory text
    enc_form = enc_form.replace(encode_form_value(
                    naaya_map_i18n["Type location address"]), "");
    enc_form = enc_form.replace(encode_form_value(
                    naaya_map_i18n["Type keywords"]), "");

    var url = portal_url + "/observatory_xrjs_tooltip?" +
            enc_form + '&lat='+ latitude + '&lon=' + longitude +
            '&geo_query=' + query;

    $.get(url, function(data) {
        callback(data);
    });
}

function update_locations_values(bounds, query){
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
				"&geo_types=" + form.symbols.value +
				"&geo_query=" + query;
	
		$('#view_as_list').attr('href', "./list_locations" + req_link);
		$('#download_georss').attr('href', "./export_geo_rss" + req_link);
		var form_symbols = form.symbols.value.split(',');
		var req_symbols = "";
		for (var i=0;i<form_symbols.length; i++) {
			req_symbols += ("geo_types=" + form_symbols[i]);
			if (i < form_symbols.length) {
				req_symbols += "&";
			}
		}
		$('#view_in_google_earth').attr('href', "./downloadLocationsKml?" +
		       req_symbols + "&geo_query=" + query);
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
	setAjaxWait();
	map_engine.refresh_points();
}

function toggleChildren(elem) {
	li = elem.parentNode;
	children = li.getElementsByTagName('li');
	for (var i=0;i<children.length;i++) {
		children[i].getElementsByTagName('input')[0].checked = elem.checked;
	}
	startMapRefresh();
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
	geo_query.value = naaya_map_i18n["Type keywords"];
	geo_query.style.color = "#ccc";
	geo_query.onfocus = function() {
		if (this.value === naaya_map_i18n["Type keywords"]) {
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
    };
    css.left = point_position.left + map_jq.position().left;
    css.top = map_jq.offset().top + point_position.top - 50;

    var balloon = $('<div>').css(css).html(content);
    //var close_button = $('<a>[' + naaya_map_i18n["close"] + ']</a>').css({color: '#999', float: 'right'});
    //close_button.click(function(){ clear_custom_balloon(); });
    //balloon.append(close_button, $('<div>').html(content));
    map_jq.parent().append(balloon);

    clear_custom_balloon = function() { balloon.remove(); }
}
var clear_custom_balloon = function() {}

function onclick_onempty(point, point_position) {
    clear_new_point();

    $.ajax({
        url: 'observatory_map_new_point?latitude='+point.latitude+'&longitude='+point.longitude,
        success: function(data) {
            var map_jq = $('#map');
            var css = {
                    position: 'absolute',
                    'z-index': 1000
                    };
            css.left = point_position.x + map_jq.position().left;
            css.top = map_jq.offset().top + point_position.y;

            var balloon = $('<div>').css(css).html(data);
            map_jq.parent().append(balloon);
            clear_new_point = function() { balloon.remove(); }
        },
        error: function(req) {
            if (console) console.error('error getting map data', req);
        }
    });
}
var clear_new_point = function() {}

