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
    clear_add_point();
    clear_view_point();
    setAjaxWait();
    var str_bounds = 'lat_min=' + bounds.lat_min + '&lat_max=' + bounds.lat_max +
        '&lon_min=' + bounds.lon_min + '&lon_max=' + bounds.lon_max;
    var url = "./observatory/xrjs_clusters?" + str_bounds;
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
            alert(gettext("Error loading points: ") + response.error);
        }
        var num_records = 0;
        $.each(response.points, function(i, point) {
            if (point.label === 'cluster') {
                num_records += point.num_points;
            } else {
                num_records++;
            }
        });
        setRecordCounter(num_records);
        return response.points;
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
	address.value = naaya_map_i18n["Type location address"];
	address.style.color = "#ccc";
	address.onfocus = function() {
		if (this.value === naaya_map_i18n["Type location address"]) {
			this.value = "";
		}
		this.style.color = "#000";
	}
	var country = document.getElementById('country');
	country.value = gettext("Type country name");
	country.style.color = "#ccc";
	country.onfocus = function() {
		if (this.value === gettext("Type country name")) {
			this.value = "";
		}
		this.style.color = "#000";
	}

	document.getElementById('js_links').style.display = "block";
	a = document.getElementById('address').readOnly = false;
	document.getElementById('address_button').disabled = false;
	displayParentCheckboxes();
}

/*
 * Functions for showing the add pin balloon
 */
function load_add_point(lat, lon, type) {
    if (type == 'undefined') {
        type='';
    }

    if (load_add_point_in_progress) {
        return;
    }
    load_add_point_in_progress = true;
    clear_add_point();
    clear_view_point();

    $.ajax({
        url: 'observatory/pin_add?latitude='+lat+'&longitude='+lon+'&type='+type,
        dataType: 'json',
        success: function(data) {
            if (!data.can_add) {
                load_add_point_in_progress = false;
                alert(gettext('You can not add pin here. To close to a recently added pin!'));
                return;
            }

            add_point(lat, lon, data.html);
            load_add_point_in_progress = false;
        },
        error: function(req) {
            if (typeof(console) != 'undefined') {
                console.error('error getting map data', req);
            }
            load_add_point_in_progress = false;
        }
    });
}
function add_point(lat, lon, point_tooltip) {
    var map_jq = $('#map');
    var css = {position: 'absolute', 'z-index': 1000};

    // compute the positions for the balloon
    point_position = map_engine.page_position(lat, lon);
    if (point_position.x < map_jq.width() / 2) {
        css.left = point_position.x + map_jq.position().left;
    } else {
        css.left = point_position.x + map_jq.position().left - 458;
    }
    css.top = map_jq.offset().top + point_position.y - 280;

    // add the ballon
    var balloon = $('<div>').css(css).html(point_tooltip);
    map_jq.parent().append(balloon);
    clear_add_point = function() { balloon.remove(); }
}
var load_add_point_in_progress = false;
var clear_add_point = function() {}
function add_point_to_xy(x, y) {
    var point = map_engine.map_coords(x, y);
    load_add_point(point.lat, point.lon);
}

/*
 * Functions for showing the view pin balloon
 */
function load_view_point(lat, lon, point_id) {
    if (load_view_point_in_progress) {
        return;
    }
    load_view_point_in_progress = true;
    clear_add_point();
    clear_view_point();

    $.ajax({
        url: 'observatory/pin?id='+point_id,
        success: function(data) {
            view_point(lat, lon, data);
            load_view_point_in_progress = false;
        },
        error: function(req) {
            if (typeof(console) != 'undefined') {
                console.error('error getting map data', req);
            }
            load_view_point_in_progress = false;
        }
    });
}
function view_point(lat, lon, point_tooltip) {
    clear_add_point();
    clear_view_point();

    var map_jq = $('#map');
    var css = {position: 'absolute', 'z-index': 1000};

    // compute the positions for the balloon
    point_position = map_engine.page_position(lat, lon);
    if (point_position.x < map_jq.width() / 2) {
        css.left = point_position.x + map_jq.position().left;
    } else {
        css.left = point_position.x + map_jq.position().left - 300;
    }
    css.top = map_jq.offset().top + point_position.y - 120;

    // add the ballon
    var balloon = $('<div>').css(css).html(point_tooltip);
    map_jq.parent().append(balloon);
    clear_view_point = function() { balloon.remove(); }
}
var load_view_point_in_progress = false;
var clear_view_point = function() {}


function onclickpoint(lat, lon, point_id, point_tooltip) {
    if (point_tooltip) {
        view_point(lat, lon, point_tooltip);
    } else {
        if (point_id === '') {
            map_engine.set_center_and_zoom_in(lat, lon);
        } else {
            load_view_point(lat, lon, point_id);
        }
    }
}
function onmouseoverpoint(lat, lon, point_id, point_tooltip) {
    if (point_id !== '') {
        load_view_point(lat, lon, point_id);
    }
}

