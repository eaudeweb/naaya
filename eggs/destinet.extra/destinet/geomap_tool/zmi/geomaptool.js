$(document).ready(function() {
  $(".category_child").toggle();
  $(".category_title, .category_img").click(function() {
    var img = $(this).parent().children('.category_img');
    if (img.attr('src') == 'misc_/Naaya/plus.gif') {
      img.attr('src', 'misc_/Naaya/minus.gif');
    } else {
      img.attr('src', 'misc_/Naaya/plus.gif')
    }
    $(this).siblings('.category_child').toggle();
  });
  $('#master_check_all').click(function() {
    $('.administrative_list input:checkbox, .topics_list input:checkbox, .landscape_list input:checkbox,.map_legend input:checkbox').attr('checked', this.checked);
  })
  //$('#geo_query').autocomplete(autocomplete_data, { multiple: true });
  $(window).unload(function() {
    var url = $("#map_url").val();
    History.pushState(null, null, url);
  });
});

var isSelected = true;

function toggleSelect() {
  var frm = document.frmFilterMap;
  if (frm != null) {
    var i;
    for (i = 0; i < frm.elements.length; i++)
      if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'geo_types:list')
        frm.elements[i].checked = !isSelected;
    isSelected = !isSelected;
    var btn = document.getElementById('checkall');
    if (btn.innerHTML == naaya_map_i18n["Check All"]) { btn.innerHTML = naaya_map_i18n["Uncheck All"] } else { btn.innerHTML = naaya_map_i18n["Check All"] }
  }
  startMapRefresh();
}

String.prototype.trim = function() {
  return (this.replace(/^[\s\xA0]+/, "").replace(/[\s\xA0]+$/, ""))
}

String.prototype.endsWith = function(str) { return (this.match(str + "$") == str) }

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
  if (enc_form.indexOf('geo_types') !== -1) {
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
        if (console) console.error('error getting map data', req);
      }
    });
  } else {
    var response = { 'points': {} };
    document.body.style.cursor = "default";
    parse_response_data(response)
  }

  function parse_response_data(response) {
    if (response.error) {
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
    if (num_records > 0){
        var req_link = '?' + str_bounds + '&' + enc_form + '&geo_query=' + query + '&all_records=True';
        $('#view_as_list').attr('href', "./list_locations" + req_link).css('opacity', 1).css('pointer-events', 'initial');
        $('#view_as_map').attr('href', "./portal_map" + req_link).css('opacity', 1).css('pointer-events', 'initial');
        $('#view_this_map').attr('href', "./" + req_link).css('opacity', 1).css('pointer-events', 'initial');
        $('#download_georss').attr('href', "./export_geo_rss" + req_link).css('opacity', 1).css('pointer-events', 'initial');

    } else {
        $('#view_as_list').css('opacity', 0).css('pointer-events', 'none');
        $('#view_as_map').css('opacity', 0).css('pointer-events', 'none');
        $('#view_this_map').css('opacity', 0).css('pointer-events', 'none');
        $('#download_georss').css('opacity', 0).css('pointer-events', 'none');
    }
    update_locations_values(bounds, enc_form, query);
    return response.points;
  }
}



// override tibi

var _map_points_loader = { abort: function() {} };
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
    if (skip[pair.name] == pair.value) return; // placeholder, ignore it
    if (pair.value == "") return; // empty, ignore it
    filter.push(pair);
  });
  return filter;
}

function _refresh_map_points(bounds, callback, loader) {
  // clear_custom_balloon();
  // setAjaxWait();

  // var filter = get_map_filter_values();
  // var filter_dict = {};
  // $.each(filter, function(i, pair) { filter_dict[pair.name] = pair.value; });
  // if(window.naaya_map_url_hash) {
  //     var stripped_filter = $.map(filter, function(item) {
  //         return {
  //             name: item.name.replace(/:(utf8|ustring|list)/g, ''),
  //             value: item.value
  //         };
  //     });
  //     naaya_map_url_hash.filter_change(stripped_filter);
  // }

  // var method = (naaya_map_engine.config['cluster_points'] ?
  //               "xrjs_getGeoClusters" : "xrjs_getGeoPoints");
  // var str_bounds = 'lat_min=' + bounds.lat_min + '&lat_max=' + bounds.lat_max +
  //     '&lon_min=' + bounds.lon_min + '&lon_max=' + bounds.lon_max;
  // // TODO use zope flags!
  // var url = (portal_map_url + "/" + method + "?" +
  //            str_bounds + '&' + $.param(filter, true));

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
  if (enc_form.indexOf('geo_types') !== -1) {
    $.ajax({
      url: url,
      dataType: 'json',
      success: function(data) {
        if (loader.cancelled) return;
        document.body.style.cursor = "default";
        parse_response_data(data);
        callback(data.points);
      },
      error: function(req) {
        if (loader.cancelled) return;
        document.body.style.cursor = "default";
        setRecordCounter(0);
      }
    });
  } else {
    var response = { 'points': {} };
    document.body.style.cursor = "default";
    parse_response_data(response)
  }

  function parse_response_data(response) {
    if (response.error) {
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
    if (num_records > 0){
        var req_link = '?' + str_bounds + '&' + enc_form + '&geo_query=' + query + '&all_records=True';
        $('#view_as_list').attr('href', "./list_locations" + req_link).css('opacity', 1).css('pointer-events', 'initial');
        $('#view_as_map').attr('href', "./portal_map" + req_link).css('opacity', 1).css('pointer-events', 'initial');
        $('#view_this_map').attr('href', "./" + req_link).css('opacity', 1).css('pointer-events', 'initial');
        $('#download_georss').attr('href', "./export_geo_rss" + req_link).css('opacity', 1).css('pointer-events', 'initial');
    } else {
        $('#view_as_list').css('opacity', 0).css('pointer-events', 'none');
        $('#view_as_map').css('opacity', 0).css('pointer-events', 'none');
        $('#view_this_map').css('opacity', 0).css('pointer-events', 'none');
        $('#download_georss').css('opacity', 0).css('pointer-events', 'none');
    }
    update_locations_values(bounds, enc_form, query);
    return response.points;
  }

}



function points_nearby(places, lat, lon, radius) {
  return $.map(places, function(place) {
    if (distance_to(place.lat, place.lon) > radius)
      return;
    if (place.id == "")
      return;
    return place.id;
  });

  function distance_to(lat2, lon2) {
    var dlat = lat2 - lat,
      dlon = lon2 - lon;
    return Math.sqrt(dlat * dlat + dlon * dlon);
  }
}

function load_marker_balloon(point_id_list, callback) {
  var point_args = $.map(point_id_list, function(point_id) {
    if (point_id == '') return;
    return "point_id=" + encodeURIComponent(point_id);
  });
  var url = portal_map_url + "/xrjs_getPointBalloon?" + point_args.join('&');

  $.get(url, function(data) {
    callback(data);
  });
}

function destinet_get_form_data() {
  var form_data = new Array();
  $('#filter_map input:checkbox:checked').each(function() {
    form_data[form_data.length] = '&geo_types%3Alist=' + this.value;
  });
  $('.topics_list input:checkbox:checked').each(function() {
    if (this.value != 'on') {
      form_data[form_data.length] = '&topics%3Alist=' + this.value;
    }
  })
  $('.landscape_list input:checkbox:checked').each(function() {
    if (this.value != 'on') {
      form_data[form_data.length] = '&landscape_type%3Alist=' + this.value;
    }
  })
  if ($('#landscape_type').val() != null){
    $.each($('#landscape_type').val(), function(index, value){
      form_data[form_data.length] = '&landscape_type%3Alist=' + value;
    })
  }
  if ([undefined, '', null].indexOf($('#country').val()) == -1){
    if ($('#country').val() && $('#country').val().constructor == Array){
      $.each($('#country').val(), function(index, value){
        form_data[form_data.length] = '&country%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&country%3Alist=' + $('#country').val();
    }
  }
  if ([undefined, '', null].indexOf($('#coverage').val()) == -1){
    if ($('#coverage').val() && $('#coverage').val().constructor == Array){
      $.each($('#coverage').val(), function(index, value){
        form_data[form_data.length] = '&coverage%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&coverage%3Alist=' + $('#coverage').val();
    }
  }
  if ([undefined, '', null].indexOf($('#administrative_level').val()) == -1){
    if ($('#administrative_level').val() && $('#administrative_level').val().constructor == Array){
      $.each($('#administrative_level').val(), function(index, value){
        form_data[form_data.length] = '&administrative_level%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&administrative_level%3Alist=' + $('#administrative_level').val();
    }
  }
  if ([undefined, '', null].indexOf($('#geo_types').val()) == -1){
    if ($('#geo_types').val() && $('#geo_types').val().constructor == Array){
      $.each($('#geo_types').val(), function(index, value){
        form_data[form_data.length] = '&geo_types%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&geo_types%3Alist=' + $('#geo_types').val();
    }
  }
  if ([undefined, '', null].indexOf($('#category').val()) == -1){
    if ($('#category').val() && $('#category').val().constructor == Array){
      $.each($('#category').val(), function(index, value){
        form_data[form_data.length] = '&category%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&category%3Alist=' + $('#category').val();
    }
  }
  if ([undefined, '', null].indexOf($('#gstc_criteria').val()) == -1){
    if ($('#gstc_criteria').val() && $('#gstc_criteria').val().constructor == Array){
      $.each($('#gstc_criteria').val(), function(index, value){
        form_data[form_data.length] = '&gstc_criteria%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&gstc_criteria%3Alist=' + $('#gstc_criteria').val();
    }
  }
  if ([undefined, '', null].indexOf($('#sustainability').val()) == -1){
    if ($('#sustainability').val() && $('#sustainability').val().constructor == Array){
      $.each($('#sustainability').val(), function(index, value){
        form_data[form_data.length] = '&sustainability%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&sustainability%3Alist=' + $('#sustainability').val();
    }
  }
  if ([undefined, '', null].indexOf($('#credibility').val()) == -1){
    if ($('#credibility').val() && $('#credibility').val().constructor == Array){
      $.each($('#credibility').val(), function(index, value){
        form_data[form_data.length] = '&credibility%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&credibility%3Alist=' + $('#credibility').val();
    }
  }
  if ([undefined, '', null].indexOf($('#certificate_services').val()) == -1){
    if ($('#certificate_services').val() && $('#certificate_services').val().constructor == Array){
      $.each($('#certificate_services').val(), function(index, value){
        form_data[form_data.length] = '&certificate_services%3Alist=' + value;
      });
    } else {
        form_data[form_data.length] = '&certificate_services%3Alist=' + $('#certificate_services').val();
    }
  }
  if ([undefined, '', null, 'Type location address'].indexOf($('#address').val()) == -1){
      form_data[form_data.length] = '&address=' + $('#address').val();
  }
  $('.administrative_list input:checkbox:checked').each(function() {
    if (this.value != 'on') {
      form_data[form_data.length] = '&administrative_level%3Alist=' + this.value;
    }
  })
  $('.meta_type_list').each(function() {
    form_data[form_data.length] = '&meta_types%3Alist=' + this.value;
  })
  return form_data.join('');
}

function update_locations_values(bounds, enc_form, query) {
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
    for (var i = 0; i < symbols.length; i++) {
      if (symbols[i].checked && form.symbols.value.indexOf(symbols[i]) == -1) {
        if (form.symbols.value != "") {
          form.symbols.value = form.symbols.value + "," + symbols[i].value;
        } else { form.symbols.value = symbols[i].value; }
      }
    }
    var req_link = "?lat_min=" + bounds.lat_min +
      "&lat_max=" + bounds.lat_max +
      "&lon_min=" + bounds.lon_min +
      "&lon_max=" + bounds.lon_max +
      enc_form +
      "&geo_query=" + query;


    $('#view_as_list').attr('href', "./list_locations" + req_link + '&all_records=True');
    $('#view_as_map').attr('href', "./portal_map" + req_link + '&all_records=True');
    $('#view_this_map').attr('href', "./" + req_link);
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

var MAP_CLUSTER_ZOOM_RESOLUTION_THRESHOLD = 100;

function map_marker_clicked(point) {
  // new click handler
  var resolution = map_engine.get_resolution();
  var point_id_list = [];
  if (point.id == '') {
    if (point.point_ids.length < 5 ||
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
  var balloon = custom_balloon(point.lat, point.lon, point.tooltip);
  return balloon;
}


function notify_contacts_csv(bounds, query, enc_form) {
  var form = document.getElementById('list_locations_form');
  if (form === null) return;
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
      "./export_csv" + req_link + "&meta_type=Naaya Contact" + "&file_type=csv");
    $('#download_contacts_xls').attr('href',
      "./export_csv" + req_link + "&meta_type=Naaya Contact");
  }
}

function setAjaxWait() {
  $('#view_as_list').css('opacity', 0).css('pointer-events', 'none');
  $('#view_as_map').css('opacity', 0).css('pointer-events', 'none');
  $('#view_this_map').css('opacity', 0).css('pointer-events', 'none');
  $('#download_georss').css('opacity', 0).css('pointer-events', 'none');
  document.body.style.cursor = "wait";
  var rec_counter = document.getElementById('record_counter');
  if (rec_counter) {
    rec_counter.innerHTML = "";
    var wait_gif = document.createElement('img');
    wait_gif.src = "../misc_/NaayaCore/progress.gif";
    rec_counter.appendChild(wait_gif);
  }
}

function setRecordCounter(value) {
  var rec_counter = document.getElementById('record_counter');
  if (rec_counter) { rec_counter.innerHTML = value.toString(); }
}

function findAddress(evt) {
  if (evt) evt.preventDefault();
  mapCenterLoc = document.getElementById('address').value;
  if (mapCenterLoc != '') {
    map_engine.go_to_address(mapCenterLoc);
  }
}

function handleKeyPress(elem, key) {
  if (key.keyCode == 13) {
    if (elem.id == 'address') { findAddress(); return false; }
    if (elem.id == 'geo_query') { startMapRefresh(); return false; }
  }
}

function startMapRefresh() {
  if ($('input[name="geo_types:list"]:checked').length == 0 && $('#geo_types').val() == null) {
    var alert_msg = gettext('Please select at least one category to display on the map');
    alert(alert_msg);
  }
  setAjaxWait();
  map_engine.refresh_points();
}

function toggleChildren(elem) {
  li = elem.parentNode;
  children = li.getElementsByTagName('li');
  for (var i = 0; i < children.length; i++) {
    children[i].getElementsByTagName('input')[0].checked = elem.checked;
  }
  // startMapRefresh();
}

function displayParentCheckboxes() {
  form = document.getElementById('filter_map');
  if (form != null) {
    form_children = form.childNodes;
    for (var i = 0; i < form_children.length; i++) {
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

  //document.getElementById('checkall').style.display = "inline";
  document.getElementById('js_links').style.display = "inline";
  a = document.getElementById('address').readOnly = false;
  document.getElementById('address_button').disabled = false;
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
  var close_button = $('<a>[' + naaya_map_i18n["close"] + ']</a>').css({ color: '#999', float: 'right' });
  close_button.click(function() { clear_custom_balloon(); });
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
