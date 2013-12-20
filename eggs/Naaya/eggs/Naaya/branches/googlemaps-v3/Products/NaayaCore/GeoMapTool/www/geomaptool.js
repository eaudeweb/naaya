var isSelected = true;
function toggleSelect() {
  var frm = document.frmFilterMap;
  if(frm != null) {
    var i;
    for(i=0; i<frm.elements.length; i++)
	  if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'geo_types:list')
	    frm.elements[i].checked = !isSelected;
    isSelected = !isSelected;
    jQuery("#toggle-progress").show();
  }

  // change button and hide loading animation after map.refresh_points
  callback = function(){
      if(frm != null){
	var btn = document.getElementById('checkall');
	if (btn.innerHTML == naaya_map_i18n["Show All"]){
	  btn.innerHTML = naaya_map_i18n["Hide All"];
	  jQuery(btn).attr("title", naaya_map_i18n["Hide All"]);
	}
	else{
	  btn.innerHTML = naaya_map_i18n["Show All"];
	  jQuery(btn).attr("title", naaya_map_i18n["Show All"]);
	}

	jQuery("#toggle-progress").hide();
      }
  };

  startMapRefresh(callback);

}

function encode_form_value(value) {
    // uri-encode with "+" for space
    return encodeURIComponent(value).replace(/%20/g, '+');
}

function update_map_filter_values(filter) {
    // update filters from URL hash

    var form = $('form#frmFilterMap');

    var geo_types_cleared = false;

    $.each(filter, function(i, pair) {
        if(pair.name == 'geo_types') {
            var inputs = $('input[name="geo_types:list"]', form);
            if(! geo_types_cleared) {
                geo_types_cleared = true;
                inputs.attr('checked', null);
            }
            var filter = function(e) { return ($(e).val() == pair.value) }
            $($.grep(inputs, filter)).attr('checked', 'checked');
        }
        if(pair.name == 'geo_query') {
            $('input#geo_query', form)[0].onfocus();
            $('input#geo_query', form).val(pair.value);
        }
        if(pair.name == 'address') {
            $('input#address', form)[0].onfocus();
            $('input#address', form).val(pair.value);
        }
    });

    // no need to call map refresh, since this handler is called on page
    // load, and the map refresh will follow shortly.
}

var _map_points_loader = {abort: function(){}};
var _map_points_loader_delay = 200;

function load_map_points(bounds, callback) {
    // schedule a map point loading

    _map_points_loader.abort();

    var loader = {
        cancelled: false
    };

    loader.run = function() {
        _refresh_map_points(bounds, callback, loader);
    };

    loader.timeout = setTimeout(function() { loader.run(); },
                                _map_points_loader_delay);

    loader.abort = function() {
        loader.cancelled = true;
        clearTimeout(loader.timeout);
    };

    _map_points_loader = loader;
}

function get_map_filter_values() {
    // don't include bounds since this is used to set URL hash
    var filter = [];
    var skip = {
        'address:ustring:utf8': naaya_map_i18n["Type location address"],
        'geo_query:ustring:utf8': naaya_map_i18n["Type keywords to filter locations"]
    };
    $.each($("form#frmFilterMap").serializeArray(), function(i, pair) {
        if(skip[pair.name] == pair.value) return; // placeholder, ignore it
        if(pair.value == "") return; // empty, ignore it
        filter.push(pair);
    });
    return filter;
}

function _refresh_map_points(bounds, callback, loader) {
    clear_custom_balloon();
    setAjaxWait();

    var filter = get_map_filter_values();
    var filter_dict = {};
    $.each(filter, function(i, pair) { filter_dict[pair.name] = pair.value; });
    if(window.naaya_map_url_hash) {
        var stripped_filter = $.map(filter, function(item) {
            return {
                name: item.name.replace(/:(utf8|ustring|list)/g, ''),
                value: item.value
            };
        });
        naaya_map_url_hash.filter_change(stripped_filter);
    }

    var method = (naaya_map_engine.config['cluster_points'] ?
                  "xrjs_getGeoClusters" : "xrjs_getGeoPoints");
    var str_bounds = 'lat_min=' + bounds.lat_min + '&lat_max=' + bounds.lat_max +
        '&lon_min=' + bounds.lon_min + '&lon_max=' + bounds.lon_max;
    // TODO use zope flags!
    var url = (portal_map_url + "/" + method + "?" +
               str_bounds + '&' + $.param(filter, true));

    $.ajax({
        url: url,
        dataType: 'json',
        success: function(data) {
            if(loader.cancelled) return;
            document.body.style.cursor = "default";
            parse_response_data(data);
            callback(data.points);
        },
        error: function(req) {
            if(loader.cancelled) return;
            document.body.style.cursor = "default";
            setRecordCounter(0);
        }
    });

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
        var geo_query = filter_dict['geo_query:ustring:utf8'];
        if(! geo_query) geo_query = "";
        update_locations_values(bounds, geo_query);
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
		var container_li = undefined;
		for (var i=0;i<symbols.length;i++){
			container_li = symbols[i].parentNode;
			if (symbols[i].checked){
			  container_li.className = '';
			  if(form.symbols.value.indexOf(symbols[i]) == -1){
				// construct ','.join(symbols values) in form.symbols.value
				if (form.symbols.value != ""){
					form.symbols.value = form.symbols.value + "," + symbols[i].value;
				}
				else {form.symbols.value = symbols[i].value;}
			  }
			} else {
			  container_li.className = 'unchecked_categ';
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

function handleKeyPress(event) {
	var elem = event.target;
	if (event.keyCode == 13) { 
		if (elem.id == 'address') {findAddress(); return false;}
		if (elem.id == 'geo_query') {startMapRefresh(); return false;}
	}
}

function startMapRefresh(callback) {
	setAjaxWait();
	// `event` param is undefined
	map_engine.refresh_points(undefined, callback);
}

function toggleChildren(elem) {
	li = elem.parentNode;
	children = li.getElementsByTagName('li');
	for (var i=0;i<children.length;i++) {
		children[i].getElementsByTagName('input')[0].checked = elem.checked;
	}
	startMapRefresh();
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
	geo_query.value = naaya_map_i18n["Type keywords to filter locations"];
	geo_query.style.color = "#ccc";
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
	document.getElementById('map_links_js').style.display = "block";
	//Also place handlers on inputs:
	jQuery('#geo_query, #address').keypress(handleKeyPress);
}

var new_naaya_map_balloon = function(options) {
    var balloon = {
        div: $('<div>')[0],
        destroy_callbacks: []
    };

    var content_div = $('<div>')[0];

    var close_button = $('<a href="javascript:void(0);" class="marker-balloon-close-button" title="' + naaya_map_i18n["Close"] + '">&nbsp;</a>');
    close_button.click(function(){ balloon.destroy(); });

    var balloon_div = $(balloon['div']).addClass('marker-balloon');
    $(balloon['div']).append(close_button, content_div);

    balloon.show = function(options) {
        $(balloon['div']).appendTo(options['parent']).css({
            left: options['left'],
            top: options['top']
        });
        return balloon;
    };

    balloon.html = function(html) {
        $(content_div).html(html);
        return balloon;
    };

    balloon.destroy = function(callback) {
        if(arguments.length == 0) {
            $(balloon['div']).remove();
            $.each(balloon.destroy_callbacks, function(i, callback) {
                callback();
            });
        }
        else {
            balloon.destroy_callbacks.push(callback);
        }
        return balloon;
    };

    return balloon;
};

var custom_balloon_singleton = null;
var clear_custom_balloon = function() {
    if(custom_balloon_singleton != null) {
        custom_balloon_singleton.destroy();
        custom_balloon_singleton = null;
    }
}

function custom_balloon(lat, lon, content) {
    clear_custom_balloon();
    var balloon = custom_balloon_singleton = new_naaya_map_balloon();
    balloon.html(content);

    var map_div = $('#map');
    var map_position = map_div.position();
    var point_position = map_engine.page_position(lat, lon);

    balloon.show({
        left: map_position.left + point_position.x - 70,
        top: map_position.top + point_position.y + 10,
        parent: map_div.parent()
    });

    return balloon;
}

var map_url_hash = function() {
    var hash = {
        _filter: [],
        _map_position: [],
        _our_hash: null,
        _change_handlers: []
    };

    hash.map = function(map) {
        hash._map = map;
        if(hash._map.on_move) {
            hash._map.on_move(hash.map_move);
        }
        if(hash._map.set_zoom_and_center) {
            hash.on_change(function(filter) {
                var position = {};
                $.each(filter, function(i, pair) {
                    var name = pair.name, value = pair.value;
                    if(name == 'lat' || name == 'lon' || name == 'zoom') {
                        position[name] = value;
                    }
                });
                hash._map.set_zoom_and_center(position);
            });
        }
    };

    hash.activate = function() {
        $(window).bind("hashchange", hash._hash_changed);
        if(location.hash) {
            hash._hash_changed();
        }
    };

    hash._update_url = function() {
        var data = $.merge($.merge([], hash._filter), hash._map_position);
        var new_hash = '#' + $.param(data);
        if(hash._our_hash !== new_hash) {
            hash._our_hash = new_hash;
            location.replace(new_hash);
        }
    };

    hash._hash_changed = function() {
        var new_hash = location.hash;
        if(new_hash === hash._our_hash) return;
        var filter = [];
        $.each(new_hash.substr(1).split('&'), function(i, pair) {
            var split_pair = pair.split('=');
            if(split_pair.length < 2) return;
            var name = decodeURIComponent(split_pair[0].replace("+", " "));
            var value = decodeURIComponent(split_pair[1].replace("+", " "));
            filter.push({name: name, value: value});
        });

        $.each(hash._change_handlers, function(i, handler) {
            handler(filter);
        });
    };

    hash.on_change = function(handler) {
        hash._change_handlers.push(handler);
    };

    hash.map_move = function(lon, lat, zoom) {
        hash._map_position = [
            {name: 'lat', value: Math.round(lat*10000)/10000},
            {name: 'lon', value: Math.round(lon*10000)/10000},
            {name: 'zoom', value: zoom}
        ];
        hash._update_url();
    };

    hash.filter_change = function(filter) {
        hash._filter = filter;
        hash._update_url();
    };

    return hash;
};

var MAP_CLUSTER_ZOOM_RESOLUTION_THRESHOLD = 100;

function map_marker_clicked(point) {
    // new click handler
    var resolution = map_engine.get_resolution();
    var point_id_list = [];
    if (point.id == '') {
        if(point.point_ids.length < 5 ||
           resolution > MAP_CLUSTER_ZOOM_RESOLUTION_THRESHOLD) {
            point_id_list = point.point_ids;
        } else {
            map_engine.set_center_and_zoom_in(point.lat, point.lon);
            return;
        }
    } else {
        var radius = 10 / resolution;
        point_id_list = points_nearby(map_engine.get_current_places(),
                                      point.lat, point.lon, radius);
    }
    var balloon = custom_balloon(point.lat, point.lon, "loading...");
    load_marker_balloon(point_id_list, function(html) {
        balloon.html(html);
    });
    return balloon;
}

function onclickpoint(lat, lon, point_id, point_tooltip) {
    // old click handler
    // TODO replace calls to onclickpoint with calls to map_marker_clicked
    if (point_id === '') {
        map_engine.set_center_and_zoom_in(lat, lon);
    } else {
        debugger;
        var current_places = map_engine.get_current_places();
        var points = points_nearby(current_places, lat, lon, 0.0001);
        load_marker_balloon(points, function(html) {
            custom_balloon(lat, lon, html);
        });
    }
}

// can be overwritten to get notifications for the mouse over events
function onmouseoverpoint(lat, lon, point_id, point_tooltip) {}

