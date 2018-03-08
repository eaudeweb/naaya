showPageElements();
window.map_engine = naaya_map_engine.portal_map('map');
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
  var close_button = $('<' + 'a>[' + naaya_map_i18n["close"] + ']<' + '/a>').css({ color: '#999', float: 'right' });
  close_button.click(function() { clear_custom_balloon(); });
  balloon.append(close_button, $('<' + 'div>').html(content));
  map_jq.parent().append(balloon);

  $('div.marker-more > a', balloon).attr('target', '_blank');
  $('div.marker-body > small', balloon).remove();

  clear_custom_balloon = function() { balloon.remove(); }
}

