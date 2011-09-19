(function($) {

M.configure_selection_info = function() {
  var per_country = {};
  var per_region = {};

  var regions_countries_hash = {};
  $.each(M.config['region_countries'], function(region_code, countries) {
    regions_countries_hash[region_code] = {};
    $.each(countries, function(i, country_code) {
      regions_countries_hash[region_code][country_code] = true;
    });
  });

  $.each(M.config['documents'], function() {
    var doc = this;

    // country counters
    $.each(doc['country'], function() {
      inc(per_country, this);
    });

    // region counters
    $.each(regions_countries_hash, function(region_code, has_member) {
      $.each(doc['country'], function() {
        if(has_member[this]) {
          inc(per_region, region_code);
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
  $('#selection-info').empty().append(
    M.render_global_info(), render_selection_info());

  function render_selection_info() {
    if(M.current_view_name == 'country') {
      var countries = M.get_selected_countries();
      if(countries.length == 1) {
        return M.render_country_info(countries[0]);
      }
    }
    else if(M.current_view_name == 'region') {
      var regions = M.get_selected_regions();
      if(regions.length == 1) {
        var countries = M.get_selected_countries();
        return M.render_region_info(regions[0], countries);
      }
    }
    return "";
  }
};

M.render_country_info = function(code) {
  var name = M.config['country_name'][code];
  var tmpl_data = {
    name: name,
    code: code,
    documents_count: M.document_counts['country'][code]
  };
  var html = M.templates['country-info'].tmpl(tmpl_data);
  var country_info_box = $('<div>').append(html);
  $('img.country-flag', country_info_box).attr('src', country_flag_url(code));
  $('a.link-water-fiche', country_info_box).attr('href',
      M.document_url(name, "Water"));
  $('a.link-green-economy-fiche', country_info_box).attr('href',
      M.document_url(name, "Green economy"));
  $('a.link-country-profile', country_info_box).attr('href',
      M.document_url(name, "profile"));
  return country_info_box;
};

M.render_region_info = function(code, countries) {
  var countries_txt = null;
  if(countries.length > 1) {
    countries_txt = $.map(countries, function(code) {
      return M.config['country_name'][code];
    }).join(", ");
  }

  var name = M.config['region_name'][code];
  var html = M.templates['region-info'].tmpl({
    name: name,
    countries_txt: countries_txt,
    documents_count: M.document_counts['region'][code]
  });
  var region_info_box = $('<div>').append(html);
  var href = M.regional_report_url(code);
  if(href) {
    $('a.link-to-regional-report', region_info_box).attr('href', href);
  }
  else {
    $('p.link-to-regional-report-box', region_info_box).remove();
  }
  $('a.link-region-profile', region_info_box).attr('href',
    M.region_info_url(name));
  return region_info_box;
};

M.render_global_info = function() {
  var total_documents = M.config['documents'].length;
  return M.templates['global-info'].tmpl({
    total_documents: total_documents,
    when: M.format_date(M.config['load_time'])
  });
};

M.regional_report_url = function(code) {
  var slug_by_region = {
    'caucasus': "eastern-europe-assessment-of-assessment-report",
    'eastern-europe': "caucasus-assessment-of-assessment-report",
    'central-asia': "central-asia-assessment-of-assessment-report",
    'russian-federation': "russian-federation-assessment-of-assessment-report"
  };
  if(! slug_by_region[code]) return null;
  return "http://www.eea.europa.eu/themes/regions/pan-european/" +
         "sub-regional-assessment-of-assessment-reports/" +
         slug_by_region[code];
};

M.document_url = function(country_name, theme_name) {
  return M.config['report_documents_url'] + '/' +
      slug(country_name) + '-' + slug(theme_name);
};

M.region_info_url = function(region_name) {
  return M.config['report_documents_url'] + '/' + slug(region_name) + '-info';
};

function slug(name) {
  return name.replace(/ /g, "-");
}

function country_flag_url(country_code) {
  return M.config['www_prefix'] + '/flags/' + country_code + '.png';
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
