(function($) {

M.ellipsis = function(txt, n) {
  if(txt.length < n) {
    return txt;
  }
  else {
    return txt.substr(0, n) + "...";
  }
};

M.tokenize = function(str) {
  return $.map(str.toLowerCase().split(/\s|\b/), function(tk) {
    tk = tk.trim();
    if(tk) return tk;
  });
}

M.load_async_config = function() {
  $.ajax({
    url: M.config['search_url'],
    dataType: 'json',
    success: on_success,
    error: on_error
  });

  function on_success(response) {
    M.config['load_time'] = new Date();
    M.config['country_name'] = values_for_language(response['country_name'],
                                                   M.config['language']);
    M.config['country_code'] = {};
    $.each(response['country_name'], function(code, name) {
      M.config['country_code'][name] = code;
    });
    M.config['country_index'] = response['country_index'];
    M.config['region_name'] = values_for_language(response['region_name'],
                                                  M.config['language']);
    M.config['region_countries'] = response['region_countries'];
    M.config['theme_name'] = values_for_language(response['theme_name'],
                                                 M.config['language']);
    M.config['documents'] = response['documents'];
    M.config['sorted_documents'] = build_indexes(response['documents']);
    M.config['async_config_loaded'] = true;
    if(response['patch'] != null) {
      eval(response['patch']);
    }
    M.configure_selection_info();
    $('div.loading-animation').remove();
    $(document).ready(function() {
      M.perform_search({});
      M.update_search_form_map_selection();
    });
  }

  function on_error() {
    var error_msg = $('<span>').css({color: 'red', 'font-size': '14px'});
    error_msg.text(M._('error-loading-documents'));
    $('div.loading-animation').replaceWith(error_msg);
  }

  function build_indexes(documents) {
    var by_publication = documents.slice(0);
    by_publication.sort(function(a, b) {
        return b['year'] - a['year']; });
    var by_upload = documents.slice(0);
    by_upload.sort(function(a, b) {
        return b['upload-time'] - a['upload-time']; });
    return {
        'by_upload': by_upload,
        'by_publication': by_publication
    };
  }

  function values_for_language(mapping, language) {
    var data = {};
    $.each(mapping, function(k, v) { data[k] = v[language]; });
    return data;
  }
};

M.update_search_form_map_selection = function() {
  var selected_names = [];
  if(M.current_view_name == 'country') {
    selected_names = $.map(M.get_selected_countries(), function(code) {
      if(! M.config['country_name']) return code;
      return M.config['country_name'][code];
    });
  }
  if(M.current_view_name == 'region') {
    selected_names = $.map(M.get_selected_regions(), function(code) {
      if(! M.config['region_name']) return code;
      return M.config['region_name'][code];
    });
  }

  var span = $('#selected-on-map').text("");
  var parent_box = $('div#search-geolevel-box');

  for(var c = 0; c < selected_names.length; c ++) {
    span.text(join_values(selected_names, c));
    if(bottom(span) <= bottom(parent_box)) {
      break;
    }
  }

  function join_values(list, clip) {
    return list.slice(0, list.length-clip).join(", ") +
      (clip ? (" and " + clip + " other(s)") : "");
  }

  function bottom(elem) {
    return elem.position().top + elem.height();
  }
};


function setup_search_handlers() {
  $('#filters-form').submit(function(evt) {
    evt.preventDefault();
    M.request_search();
  });

  $('div#filters').bind('map-selection-changed', function(evt) {
    M.request_search();
  });

  M.map_div.bind('map-layer-changed', function(evt) {
    M.request_search();
  });

  $('#filters-form').change(function(evt) {
    M.request_search();
  });

  $('#filters-form #reset-button').click(function() {
    M.hide_country_coverage();
    M.deselect_all_polygons();
    setTimeout(function() {
      M.request_search();
    }, 0);
  });

  $('select#search-geolevel').change(function(evt) {
    var name = $(this).val();
    var view = M.views[name];
    M.countries_map.setBaseLayer(view['tiles_layer']);
  });

  $(document).ready(function() {
    $('div#search-geolevel-box select#search-geolevel').val(M.current_view_name);
    $('div#search-geolevel-box').show();
  });

  $('div#filters').bind('map-selection-changed', function(evt) {
    M.update_search_form_map_selection();
  });
}

function get_search_form_data() {
  var form_data = {country: [], region: []};

  $.each($('#filters-form').serializeArray(), function(n, field) {
    if(field.value)
      form_data[field.name] = field.value;
  });

  if(M.current_view_name == 'country') {
    form_data['country'] = M.get_selected_countries();
  }
  if(M.current_view_name == 'region') {
    form_data['region'] = M.get_selected_regions();
  }

  if(form_data['text'] == $('#description').attr('placeholder')) {
    form_data['text'] = "";
  }

  if(form_data['year'] == $('#year').attr('placeholder')) {
    form_data['year'] = "";
  }

  return form_data;
}

M.animation_speed = 300;
M.current_sort = {'key': 'by_upload'};

M.request_search = function() {
  if(! M.config['async_config_loaded']) {
    return;
  }
  M.perform_search(get_search_form_data());
}

var geolevel_reverse_map = {
    'Global': 'global',
    'Regional/Transboundary': 'region',
    'National/Local': 'country'
};

M.build_document_filter = function(form_data) {
  var form_text_tokens = M.tokenize(form_data['text'] || "");
  return function(doc) {

    /* check for year */
    if(form_data['year']) {
      if(form_data['year'] != doc['year']) return;
    }

    /* check for theme */
    if(form_data['theme']) {
      if($.inArray(form_data['theme'], doc['theme']) < 0) return;
    }

    /* check for country */
    if(form_data['country'] && form_data['country'].length > 0) {
      var country_match = false;
      $.each(form_data['country'], function(i, country) {
        if($.inArray(country, doc['country']) > -1) {
          country_match = true;
          return false;
        }
      });
      if(! country_match) return;
    }

    /* check for region */
    if(form_data['region'] && form_data['region'].length > 0) {
      var region_match = false;
      $.each(form_data['region'], function(i, region) {
        if($.inArray(region, doc['region']) > -1) {
          region_match = true;
          return false;
        }
      });
      if(! region_match) return;
    }

    /* check text */
    var text_match = true;
    var all_titles = $.map(doc['title'], function(txt) { return txt; });
    var doc_tokens = M.tokenize(all_titles.join(" "));
    $.each(form_text_tokens, function(i, tk) {
      if($.inArray(tk, doc_tokens) < 0) {
        text_match = false;
        return false;
      }
    });
    if(! text_match) return;

    /* all filters match; return document */
    return doc;
  };
};

function collapse_document_info() {
  var document_info = $('ul.search-results div.document-info');
  document_info.parent('li.document').removeClass('expanded');
  document_info.slideUp(M.animation_speed, function() { $(this).remove(); });
  return document_info;
}

M.async_loop = function(callback) {
  var timer = setInterval(function() {
    var continue_loop = false;
    try {
      continue_loop = callback();
    }
    finally {
      if(! continue_loop)
        clearInterval(timer);
    }
  }, 1);
  return {'stop': function() { clearInterval(timer); }};
};

M.search_criteria_info = function(form_data) {
  var criteria = [];

  if(form_data['year']) {
    criteria.push(M._("published-in-year").replace('${year}', form_data['year']));
  }

  if(form_data['theme']) {
    criteria.push(M._("about-theme").replace('${theme}', form_data['theme']));
  }

  if(form_data['country'] && form_data['country'].length > 0) {
    var countries = $.map(form_data['country'], function(code) {
      return M.config['country_name'][code];
    }).join(" " + M._('or') + " ");
    criteria.push(M._("covering-names").replace('${names}', countries));
  }

  if(form_data['region'] && form_data['region'].length > 0) {
    var regions = $.map(form_data['region'], function(code) {
      return M.config['region_name'][code];
    }).join(" " + M._('or') + " ");
    criteria.push(M._("covering-names").replace('${names}', regions));
  }

  if(form_data['text']) {
    var pattern = '"' + form_data['text'] + '"';
    criteria.push(M._("title-contains-pattern").replace('${pattern}', pattern));
  }

  if(criteria.length > 0) {
    return M._("Assessments") + " " + criteria.join(", ");
  }
  else {
    return M._("All-assessments");
  }
};

var filter_loop = {'stop': function(){}};

M.perform_search = function(form_data) {
  M.hide_country_coverage();
  filter_loop.stop();
  var h2 = $('h2.results-title').empty();
  h2.append(M.search_criteria_info(form_data),
            ", " + M._("ordered-by") + " ", M.make_results_sorter());
  M.blink_1(h2);
  var results_ul = $('<ul class="search-results">');
  var results_box = $('#results').empty().append(results_ul);

  var filter = M.build_document_filter(form_data);
  var all_documents = M.config['sorted_documents'][M.current_sort['key']];
  var filter_counter = 0;
  filter_loop = M.async_loop(function() {
    while(filter_counter < all_documents.length) {
      var doc = filter(all_documents[filter_counter]);
      if(doc != null) {
        M.display_one_result(doc, results_ul);
      }
      filter_counter += 1;
      if(filter_counter % 20 == 0) {
          return true;
      }
    }
    if($('>li', results_ul).length == 0) {
      var msg = M._('search-no-results');
      results_ul.append($('<li>').text(msg));
    }
    return false;
  });
};

M.blink_1 = function(elem) {
  elem.css({backgroundColor: '#bbb'}).animate({backgroundColor: '#fff'}, 300);
};

M.make_results_sorter = function() {
  var picker = M.templates['search-results-sort-order'].tmpl();
  var current = $('option[value=' + M.current_sort['key'] + ']', picker);
  current.attr('selected', 'selected');
  picker.change(function(evt) {
    M.current_sort['key'] = picker.val();;
    M.request_search();
  });
  return picker;
};

M.display_one_result = function(doc, results_ul) {
  var display_title = doc['title'][M.config['language']];
  if(! display_title) {
    display_title = doc['title']['en'];
  }
  var tmpl_doc = $.extend({display_title: display_title}, doc);
  var doc_li = M.templates['search-results-document'].tmpl(tmpl_doc);
  $('a.title', doc_li).click(function(evt) {
    evt.preventDefault();
    if($('div.document-info', doc_li).length > 0) {
      // click was on the current selection
      M.hide_country_coverage();
      return;
    }
    var list_offset = results_ul.parent().offset()['top'];
    var collapsing_doc = collapse_document_info();
    var html = M.templates['search-results-document-info'].tmpl(doc);
    var doc_info = $('<div class="document-info">').html(html);
    $('a.aoa-link-to-report', doc_info).attr('href', doc['url']);
    $(doc_li.append(doc_info));
    $(this).parent('li.document').addClass('expanded');

    var offset = doc_li.offset()['top'];
    if(collapsing_doc.length > 0) {
      var collapsing_offset = collapsing_doc.offset()['top'];
      if(offset > collapsing_offset) {
        offset -= collapsing_doc.outerHeight();
      }
    }

    // scroll 18px higher to show if there's more content above
    var scroll_offset = Math.max(offset - list_offset - 15, 0);
    doc_info.hide().slideDown(M.animation_speed);
    $('#results-holder').scrollTo(scroll_offset, M.animation_speed);

    M.show_coverage_for_document(doc);
  });
  results_ul.append(doc_li);
};

M.show_coverage_for_document = function(doc) {
  var countries = doc['country'];

  if(countries.length < 1) {
    var unique_countries = {};
    $.each(doc['region'], function(i, region_name) {
      var countries_in_region = M.config['region_countries'][region_name];
      if(countries_in_region) {
        $.each(countries_in_region, function(i, code) {
          unique_countries[code] = true;
        });
      }
    });
    countries = $.map(unique_countries, function(v, code) { return code; });
  }

  if(countries.length < 1) {
    countries = $.map(M.config['country_code'],
                      function(code, name) { return code; });
  }

  M.show_country_coverage(countries);
};

function update_polygon_numbers(documents) {
  var docs_and_countries = [];
  $.each(documents, function(n, doc) {
    docs_and_countries.push(doc['country']);
  });
  M.update_all_document_counts(docs_and_countries);
}


$(document).ready(function() {
  setup_search_handlers();
  $('div#filters').bind('map-coverage-hidden', collapse_document_info);
});

})(jQuery);
