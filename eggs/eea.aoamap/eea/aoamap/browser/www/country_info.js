$(function() {

var country_info_template = M.get_template($('div#country-info'));

$('div#filters').bind('map-selection-changed', function(evt) {
  $('div.country-info-box', M.map_div).remove();
  var countries = M.get_selected_countries();
  if(countries.length != 1) {
    return;
  }
  var country_name = countries[0];
  var html = country_info_template.tmpl({name: country_name});
  var country_info_box = $('<div class="country-info-box">').append(html);
  $('.olMapViewport', M.map_div).append(country_info_box);
});

});
