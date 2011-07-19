$(function() {
  $('#description').val($('#description').attr('placeholder')).css({'color': '#999999', 'font-style': 'italic'});
  $('#year').val($('#year').attr('placeholder')).css({'color': '#999999', 'font-style': 'italic'});

  $('input.input-text').each(function(){
      $(this).focus(function(){
        if( $(this).val() == $(this).attr('placeholder') ){
          $(this).val('').css({'color': '#000000', 'font-style': 'normal'});
        }
      });

      $(this).blur(function(){
        if( $(this).val() == '' ){
          $(this).val($(this).attr('placeholder')).css({'color': '#999999', 'font-style': 'italic'});
        }
      });
  });

  $('.toggle-icon').live('click', function(){
    if( $(this).hasClass('expanded') && ($('.template-subsection', $(this).parent()).is(':visible') == true) ){
      $('.template-subsection', $(this).parent()).slideUp();
      $(this).removeClass('expanded').addClass('collapsed');
    }

    if( $(this).hasClass('collapsed') && ($('.template-subsection', $(this).parent()).is(':visible') == false) ){
      $('.template-subsection', $(this).parent()).slideDown();
      $(this).removeClass('collapsed').addClass('expanded');
    }
  });

$('#filters-form').submit(function(evt) {
  evt.preventDefault();

  form_data = {};
  $.each($(this).serializeArray(), function(n, field) {
    if(field.value)
      form_data[field.name] = field.value;
  });

  form_data['country'] = M.get_selected_countries();

  if(form_data['text'] == $('#description').attr('placeholder')) {
    form_data['text'] = "";
  }

  if(form_data['year'] == $('#year').attr('placeholder')) {
    form_data['year'] = "";
  }

  perform_search(form_data);
});

function perform_search(form_data) {
  $('ul.search-results').text('');
  $('.loading-animation').fadeIn();
  $.getJSON(M.config['search_url'], form_data, function(results) {
    if(M.config['debug'] && window.console) {
      var t = Math.round(results['query-time'] * 100) / 100;
      console.log("search results: " + results['documents'].length +
                  " documents in " + t + " seconds");
    }
    update_document_list(results['documents']);
    //update_polygon_numbers(results['documents']);
  });

  $('.loading-animation').fadeOut('fast', toggle_results_list('show'));
}

function toggle_results_list(action){
  if( ($('#results').is(':visible') === false) && (action === 'show') ){
    $("#results").show("slide", { direction: "left" }, 500);
  }else {
    if( ($('#results').is(':visible') === true) && (action === 'hide') ){
      $("#results").hide("slide", { direction: "left" }, 500);
    }
  }
}

function perform_demo_search(form_data) {
  if(form_data['country'].length == 0)
    form_data['country'] = "(all)";

  if(! form_data['text'])
    form_data['text'] = "(all)";

  if(! form_data['theme'])
    form_data['theme'] = "(all)";

  if(! form_data['author-organisation'])
    form_data['author-organisation'] = "(all)";

  var message = "Searching for documents: " + JSON.stringify(form_data);
  $("div#filters-debug").html(message, "<br>");

  $.getJSON('data/test-documents.json').success(update_document_list);
}

function get_template(elem) {
  var template_elem = $('.template', elem);
  template_elem.remove().template();
  return template_elem;
}

var template = {
  'search-results': get_template($('ul.search-results')),
  'document-info': get_template($('div#document-info'))
}

function update_document_list(documents) {
  var results = $('ul.search-results').empty();

  if(documents.length == 0) {
    var msg = "No results were found for this query";
    $('ul.search-results').append($('<li>').text(msg));
  }

  $.each(documents, function(n, doc) {
    var doc_li = template['search-results'].tmpl(doc);
    $('a.title', doc_li).click(function(evt) {
      evt.preventDefault();
      $('div.document-info').slideUp('fast', function() { $(this).remove(); });
      if($('div.document-info', doc_li).length > 0) {
        return; // click was on the current selection
      }
      var html = template['document-info'].tmpl(doc);
      var doc_info = $('<div class="document-info">').html(html);
      $(doc_li.append(doc_info));
      doc_info.hide().slideDown('fast');
      M.show_country_coverage(doc['country']);
    });
    results.append(doc_li);
  });
}

function update_polygon_numbers(documents) {
  var docs_and_countries = [];
  $.each(documents, function(n, doc) {
    docs_and_countries.push(doc['country']);
  });
  M.update_all_document_counts(docs_and_countries);
}

});
