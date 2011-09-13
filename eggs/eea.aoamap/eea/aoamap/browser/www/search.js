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
  return $.map(str.toLowerCase().split(/\b/), function(tk) {
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
    M.config['country_code'] = response['country_code'];
    M.config['country_index'] = response['country_index'];
    M.config['region_countries'] = response['region_countries'];
    M.config['documents'] = response['documents'];
    M.config['recent_documents'] = $.map(response['recent'], function(i) {
      return response['documents'][i];
    });
    M.config['async_config_loaded'] = true;
    if(response['patch'] != null) {
      eval(response['patch']);
    }
    M.configure_selection_info();
    $('div.loading-animation').remove();
    $(document).ready(function() {
      M.display_recent_entries();
    });
  }

  function on_error() {
    var error_msg = $('<span>').css({color: 'red', 'font-size': '14px'});
    error_msg.text(M._('error-loading-documents'));
    $('div.loading-animation').replaceWith(error_msg);
  }
};

function setup_filter_form_visuals() {
  $('#description').val($('#description').attr('placeholder')).css(
    {'color': '#999999', 'font-style': 'italic'});
  $('#year').val($('#year').attr('placeholder')).css(
    {'color': '#999999', 'font-style': 'italic'});

  $('input.input-text').each(function(){
      $(this).focus(function(){
        if( $(this).val() == $(this).attr('placeholder') ){
          $(this).val('').css({'color': '#000000', 'font-style': 'normal'});
        }
      });

      $(this).blur(function(){
        if( $(this).val() == '' ){
          $(this).val($(this).attr('placeholder')).css(
            {'color': '#999999', 'font-style': 'italic'});
        }
      });
  });
}


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
    M.deselect_all_polygons();
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
    var selected = [];
    if(M.current_view_name == 'country') {
      selected = M.get_selected_countries();
    }
    if(M.current_view_name == 'region') {
      selected = M.get_selected_regions();
    }

    var span = $('span#selected-on-map').text("");
    var parent_box = $('div#search-geolevel-box');

    for(var c = 0; c < selected.length; c ++) {
      span.text(join_values(selected, c));
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

M.request_search = function() {
  if(! M.config['async_config_loaded']) {
    return;
  }
  perform_search(get_search_form_data());
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
    if(form_data['country'].length > 0) {
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
    if(form_data['region'].length > 0) {
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
    var doc_tokens = M.tokenize(doc['title']);
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

function search_criteria_info(form_data) {
  var criteria = [];
  if(form_data['year']) {
    criteria.push(M._("year") + " " + form_data['year']);
  }
  if(form_data['theme']) {
    criteria.push(M._("theme") + " " + form_data['theme']);
  }
  if(form_data['country'].length > 0) {
    criteria.push(M._("country") + " (" + form_data['country'].join(", ") + ")");
  }
  if(form_data['region'].length > 0) {
    criteria.push(M._("region") + " (" + form_data['region'].join(", ") + ")");
  }
  if(form_data['text']) {
    criteria.push(M._("title-contains") + " " + form_data['text']);
  }

  if(criteria.length > 0) {
    return "Assessments with: " + criteria.join(", ");
  }
  else {
    return "All assessments";
  }
}

var filter_loop = {'stop': function(){}};

function perform_search(form_data) {
  M.hide_country_coverage();
  filter_loop.stop();
  var title = $('<h2>').text(search_criteria_info(form_data));
  var results_ul = $('<ul class="search-results">');
  var results_box = $('#results').empty().append(title, results_ul);

  var filter = M.build_document_filter(form_data);
  var all_documents = M.config['documents'];
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
}

M.display_recent_entries = function() {
  filter_loop.stop();
  var title = $('<h2>').text(M._('recent-assessments'));
  var results_ul = $('<ul class="search-results">');
  var results_box = $('#results').empty().append(title, results_ul);

  $.each(M.config['recent_documents'], function(i, doc) {
    M.display_one_result(doc, results_ul);
  });
};

M.display_one_result = function(doc, results_ul) {
  var doc_li = M.templates['search-results-document'].tmpl(doc);
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

    M.show_country_coverage(doc['country']);
  });
  results_ul.append(doc_li);
};

function update_polygon_numbers(documents) {
  var docs_and_countries = [];
  $.each(documents, function(n, doc) {
    docs_and_countries.push(doc['country']);
  });
  M.update_all_document_counts(docs_and_countries);
}


$(document).ready(function() {
  setup_filter_form_visuals();
  setup_search_handlers();
  $('div#filters').bind('map-coverage-hidden', collapse_document_info);
});

})(jQuery);
