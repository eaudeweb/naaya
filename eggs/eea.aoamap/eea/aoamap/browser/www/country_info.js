$(function() {

var country_info_template = M.get_template($('div#country-info'));

M.country_info_result = {};
M.country_info = function(name) {
  return setdefault(M.country_info_result, name, $.Deferred());
};

M.docs_summary_result.done(function(docs_summary) {
  var country_info_map = {};
  var short_name = {'Water': 'water', 'Green economy': 'green_economy'};
  $.each(docs_summary, function() {
    var doc = this;
    $.each(doc['countries'], function() {
      var info = setdefault(country_info_map, this, {});
      $.each(doc['themes'], function() {
        inc(info, 'documents_' + (short_name[this] || 'other'));
      });
      inc(info, 'documents_total')
    });
  });

  $.each(country_info_map, function(name, info) {
    M.country_info(name).resolve(info);
  });
});

$('div#filters').bind('map-selection-changed', function(evt) {
  $('div.country-info-box', M.map_div).remove();
  var countries = M.get_selected_countries();
  if(countries.length != 1) {
    return;
  }
  var country_name = countries[0];
  var country_info_box = $('<div class="country-info-box">').hide();
  $('.olMapViewport', M.map_div).append(country_info_box);

  M.country_info(country_name).done(function(info) {
    var tmpl_data = $.extend({name: country_name}, info);
    var html = country_info_template.tmpl(tmpl_data);
    country_info_box.append(html).show();
  });
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
