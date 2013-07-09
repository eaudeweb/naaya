$(function() {
    // fix for IE
    if(typeof String.prototype.trim !== 'function') {
      String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, '');
      }
    }

    var pick_ui = $('span#pick-user-ui');
    var pick_button = $('button', pick_ui);
    var search_ui = $('div.search', pick_ui);
    var results = $('div#user-search-results', pick_ui);
    var user_id_input = $('input#user_id');

    var location_div = $('#location_id');
    var subscribe_to_div = $('#subscribe_to_id');
    var all_content_types_div = $('#all_content_types');
    var content_types_div = $('#content_types');
    var lang_div = $('#language_id');
    var subscribe_button = $('#subscribe_button_id');

    pick_ui.show();

    location_div.hide();
    subscribe_to_div.hide();
    all_content_types_div.hide();
    content_types_div.hide();
    content_types_div.hide();
    lang_div.hide();
    subscribe_button.hide();

    pick_button.click(function(evt) {
        evt.preventDefault();

        var query_uid = user_id_input.val().trim();
        if (query_uid.length < 2) {
            alert('Please type at least two letters to narrow search results.');
            return false;
        }

        pick_button.attr({disabled: "disabled"});
        results.empty();
        $('div.search', pick_ui).show();
        $.get(notif_tool_url+'/admin_search_user', {query: query_uid},
                show_results);
    });

    user_id_input.focusin(function() {
        $(this.attributes).each(function() {
            if (this.nodeName == "readonly" && this.nodeValue == "readonly") {
                $('#uid_wakeup').text("You have already chosen the user. \
                                       Please move forward in completing the \
                                       other fields");
            }
        });
    });

    function show_results(users) {
        results.empty();
        if(users.length > 0) {
            results.append("Results:");
            var results_list = $('<ul'+'>').appendTo(results);
            $.each(users, function(n, user) {
                var link = $('<'+'a href="#"><'+'/a>').click(function(evt) {
                    evt.preventDefault();
                    user_id_input.val(user.user_id);
                    user_id_input.attr('readonly', "readonly");
                    pick_button.attr({disabled: null});

                    location_div.show();
                    subscribe_to_div.show();
                    all_content_types_div.show();
                    lang_div.show();
                    subscribe_button.show();
                    if ($('#subscribe_me-notif_type').val() == 'administrative'){
                        $('#subscribe_me-content_types option').removeProp('selected')
                        $('#content_types').hide();
                        $('#subscribe_me-all_content_types').prop('checked', 'checked');
                        $('#subscribe_me-all_content_types').prop('disabled', 'disabled');
                    }

                    search_ui.hide();
                }).text(user.full_name);
                var li = $('<li'+'>').append(link, ' &lt;', user.email, '&gt;');
                li.appendTo(results_list);
            });
        } else {
            pick_button.attr({disabled: null});
            results.text("No user, as member of this Interest Group, \
                          was found using the indicated criteria.");
        }
    }
    $('#subscribe_me-notif_type').change(function(){
      if ($(this).val() == 'administrative'){
          if (!$('#subscribe_me-all_content_types').is(':checked')){
              $('#subscribe_me-content_types option').removeProp('selected')
              $('#content_types').hide();
              $('#subscribe_me-all_content_types').prop('checked', 'checked');
          }
          $('#subscribe_me-all_content_types').prop('disabled', 'disabled');
      } else {
          if ($('#subscribe_me-all_content_types').is(':disabled')){
              $('#subscribe_me-all_content_types').removeProp('disabled');
          }
      }
    });
    $('#subscribe_me-all_content_types').change(function(){
        if ($(this).is(':checked')){
            $('#subscribe_me-content_types option').removeProp('selected')
            content_types_div.hide();
        }
        else{
            content_types_div.show();
        };
    });
});

