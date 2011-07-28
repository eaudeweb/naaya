$(function() {

var country_info_template = M.get_template($('div#country-info'));

M.country_info = {};

var country_info_map = {};
var short_name = {'Water': 'water', 'Green economy': 'green_economy'};
$.each(M.config['documents_summary'], function() {
  var doc = this;
  $.each(doc['countries'], function() {
    var info = setdefault(country_info_map, this, {});
    $.each(doc['themes'], function() {
      inc(info, 'documents_' + (short_name[this] || 'other'));
    });
    inc(info, 'documents_total');
  });
});

$.each(country_info_map, function(name, info) {
  M.country_info[name] = info;
});

$('div#filters').bind('map-selection-changed', function(evt) {
  $('div.country-info-box', M.map_div).remove();
  var countries = M.get_selected_countries();
  if(countries.length != 1) {
    return;
  }
  var name = countries[0];
  var tmpl_data = {name: name, code: M.config['country_code'][name]};
  $.extend(tmpl_data, M.country_info[name]);
  var html = country_info_template.tmpl(tmpl_data);
  var flag = $('<img>').attr('src', M.config['www_prefix'] + '/flags/' +
                                    M.config['country_code'][name] + '.gif');
  var country_info_box = $('<div class="country-info-box">').append(flag, html);
  $('.olMapViewport', M.map_div).append(country_info_box);
});

function setdefault(dic, name, value) {
  if(dic[name] == null) {
    dic[name] = value;
  }
  return dic[name];
}

function inc(dic, name) {
  setdefault(dic, name, 0);
  dic[name] += 1;
}

});
