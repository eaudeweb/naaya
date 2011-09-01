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
    M.config['async_config_loaded'] = true;
    if(response['patch'] != null) {
      eval(response['patch']);
    }
    M.configure_selection_info();
    $('div.loading-animation').remove();
    $(document).ready(function() {
      M.request_search();
    });
  }

  function on_error() {
    var error_msg = $('<span>').css({color: 'red', 'font-size': '14px'});
    error_msg.text("There was an error loading the list of documents.");
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

  $('.toggle-icon').live('click', function(){
    if( $(this).hasClass('expanded') &&
        ($('.template-subsection', $(this).parent()).is(':visible') == true)){
      $('.template-subsection', $(this).parent()).slideUp();
      $(this).removeClass('expanded').addClass('collapsed');
    }

    if( $(this).hasClass('collapsed') &&
        ($('.template-subsection', $(this).parent()).is(':visible') == false)){
      $('.template-subsection', $(this).parent()).slideDown();
      $(this).removeClass('collapsed').addClass('expanded');
    }
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
}

function get_search_form_data() {
  var form_data = {};
  $.each($('#filters-form').serializeArray(), function(n, field) {
    if(field.value)
      form_data[field.name] = field.value;
  });

  form_data['country'] = M.get_selected_countries();

  form_data['geolevel'] = M.current_view_name;

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

    /* check for geolevel */
    var geolevel = geolevel_reverse_map[doc['geolevel']];
    if(form_data['geolevel'] == geolevel) {}
    else if(form_data['geolevel'] == 'region' && geolevel == 'country') {}
    else return;

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

var filter_loop = {'stop': function(){}};

function perform_search(form_data) {
  filter_loop.stop();
  var results = $('ul.search-results').empty();

  var filter = M.build_document_filter(form_data);
  var all_documents = M.config['documents'];
  var results_counter = 0;
  filter_loop = M.async_loop(function() {
    while(results_counter < all_documents.length) {
      var doc = filter(all_documents[results_counter]);
      if(doc != null) {
        show_one_result(doc);
      }
      results_counter += 1;
      if(results_counter % 20 == 0) return true;
    }
    if($('>li', results).length == 0) {
      var msg = "No results were found for this query";
      $('ul.search-results').append($('<li>').text(msg));
    }
    return false;
  });

  function show_one_result(doc) {
    var doc_li = M.templates['search-results-document'].tmpl(doc);
    $('a.title', doc_li).click(function(evt) {
      evt.preventDefault();
      if($(this).hasClass('expanded')){
        $(this).removeClass('expanded').addClass('collapsed');
      }else {
        $(this).removeClass('collapsed').addClass('expanded');
      }
      
      if($('div.document-info', doc_li).length > 0) {
        // click was on the current selection
        M.hide_country_coverage();
        return;
      }
      var collapsing_doc = collapse_document_info();
      var html = M.templates['search-results-document-info'].tmpl(doc);
      var doc_info = $('<div class="document-info">').html(html);
      $(doc_li.append(doc_info));
      var list_offset = results.offset()['top'];

      var offset = doc_li.offset()['top'];
      if(collapsing_doc.length > 0) {
        var collapsing_offset = collapsing_doc.offset()['top'];
        if(offset > collapsing_offset) {
          offset -= collapsing_doc.height();
        }
      }

      doc_info.hide().slideDown(M.animation_speed);
      $('#results').scrollTo(offset - list_offset, M.animation_speed);

      M.show_country_coverage(doc['country']);
    });
    results.append(doc_li);
  }
}

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
