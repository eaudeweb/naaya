showPageElements();
window.map_engine = naaya_map_engine.portal_map('map');

// If URL contains lat/lon bounds (e.g. from "Link to this filtered map"),
// zoom the map to those bounds instead of the default view
(function() {
  var params = new URLSearchParams(window.location.search);
  var lat_min = parseFloat(params.get('lat_min'));
  var lat_max = parseFloat(params.get('lat_max'));
  var lon_min = parseFloat(params.get('lon_min'));
  var lon_max = parseFloat(params.get('lon_max'));
  if (!isNaN(lat_min) && !isNaN(lat_max) && !isNaN(lon_min) && !isNaN(lon_max) &&
      !(lat_min <= -90 && lat_max >= 90 && lon_min <= -180 && lon_max >= 180)) {
    window._naaya_bounds_from_url = true;
    if (map_engine._google_map) {
      // Google Maps engine
      var sw = new google.maps.LatLng(lat_min, lon_min);
      var ne = new google.maps.LatLng(lat_max, lon_max);
      map_engine._google_map.fitBounds(new google.maps.LatLngBounds(sw, ne), 0);
    } else if (typeof naaya_map_engine.bounds_btlr === 'function') {
      // OpenLayers engine
      var bounds = naaya_map_engine.bounds_btlr([lat_min, lat_max, lon_min, lon_max]);
      map_engine.zoom_to_extent(bounds);
    }
  }
})();

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
  css.left = point_position.x + map_jq.position().left - 20;
  css.top = map_jq.offset().top + point_position.y - 100;

  var balloon = $('<' + 'div>').css(css);
  var content_div = $('<' + 'div>');
  var destroy_callbacks = [];
  var close_button = $('<' + 'a>[' + naaya_map_i18n["close"] + ']<' + '/a>').css({ color: '#999', float: 'right' });
  close_button.click(function() { clear_custom_balloon(); });
  balloon.append(close_button, content_div);
  map_jq.parent().append(balloon);

  clear_custom_balloon = function() {
    clear_custom_balloon = function() {};
    balloon.remove();
    $.each(destroy_callbacks, function(i, callback) { callback(); });
  }

  // Same interface as new_naaya_map_balloon, used by map_marker_clicked.
  var handle = {
    html: function(html) {
      content_div.html(html);
      $('div.marker-more > a', balloon).attr('target', '_blank');
      $('div.marker-body > small', balloon).remove();
      return handle;
    },
    destroy: function(callback) {
      if (callback) destroy_callbacks.push(callback); else clear_custom_balloon();
      return handle;
    }
  };
  return handle.html(content);
}

