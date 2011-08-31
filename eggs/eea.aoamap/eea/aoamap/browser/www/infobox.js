(function($) {

M.configure_selection_info = function() {
  var per_country = {};
  var per_region = {};

  var regions_countries_hash = {};
  $.each(M.config['region_countries'], function(region_name, countries) {
    regions_countries_hash[region_name] = {};
    $.each(countries, function(i, country_name) {
      regions_countries_hash[region_name][country_name] = true;
    });
  });

  $.each(M.config['documents'], function() {
    var doc = this;

    // country counters
    $.each(doc['country'], function() {
      inc(per_country, this);
    });

    // region counters
    $.each(regions_countries_hash, function(region_name, has_member) {
      $.each(doc['country'], function() {
        if(has_member[this]) {
          inc(per_region, region_name);
          return false;
        }
      });
    });
  });

  M.document_counts = {'country': per_country, 'region': per_region};

  $('div#filters').bind('map-selection-changed', M.update_selection_info);
  M.map_div.bind('map-layer-changed', M.update_selection_info);
  M.update_selection_info();
};


M.update_selection_info = function() {
  $('#selection-info').empty().append(selection_info_content());

  function selection_info_content() {
    if(M.current_view_name == 'country') {
      var countries = M.get_selected_countries();
      if(countries.length == 0) {
        return M.render_global_info();
      }
      else if(countries.length == 1) {
        return M.render_country_info(countries[0]);
      }
      else {
        return $('<p>').text(countries.join(", "));
      }
    }
    else if(M.current_view_name == 'region') {
      var regions = M.get_selected_regions();
      if(regions.length == 0) {
        return M.render_global_info();
      }
      else if(regions.length == 1) {
        var countries = M.get_selected_countries();
        return M.render_region_info(regions[0], countries);
      }
      else {
        return $('<p>').text(regions.join(", "));
      }
    }
    else {
      return M.render_global_info();
    }
  }
};

M.render_country_info = function(name) {
  var tmpl_data = {
    name: name,
    code: M.config['country_code'][name],
    documents_count: M.document_counts['country'][name]
  };
  var html = M.templates['country-info'].tmpl(tmpl_data);
  var country_info_box = $('<div>').append(html);
  $('img.country-flag', country_info_box).attr('src', country_flag_url(name));
  $('a.link-water-fiche', country_info_box).attr('href',
      country_fiche_url(name, "Water"));
  $('a.link-green-economy-fiche', country_info_box).attr('href',
      country_fiche_url(name, "Green Economy"));
  return country_info_box;
};

M.render_region_info = function(name, countries) {
  var countries_txt = (countries.length > 1) ? countries.join(", ") : null;
  return M.templates['region-info'].tmpl({
    name: name,
    countries_txt: countries_txt,
    documents_count: M.document_counts['region'][name]
  });
};

M.render_global_info = function() {
  var total_documents = M.config['documents'].length;
  return M.templates['global-info'].tmpl({total_documents: total_documents});
};

function country_fiche_url(country_name, theme_name) {
  return M.config['country_fiche_prefix'] + '?country%3Aint=' +
      M.config['country_index'][country_name] + '&theme=' +
      encodeURIComponent(theme_name);
}

function country_flag_url(country_name) {
  return M.config['www_prefix'] + '/flags/' +
    M.config['country_code'][country_name] + '.gif';
}

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

})(jQuery);
