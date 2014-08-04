function ny_glossary_widget_js(options) {

var form_input = $('#'+options['input_id']);
var container = form_input.parent();
var list_mode = container.hasClass('glossary-widget-mode-values-list');
var values_list = null;

load_ui();

function load_ui() {
    var url = form_input.attr('rel');

    if(list_mode) {
        values_list = $('<ul class="glossary-widget-values">');
        values_list.appendTo(container);
    }

    form_input.keypress(function(evt) {
        if(evt.charCode == 13) {
            evt.preventDefault();
            if(list_mode) {
                var new_value = $.trim(form_input.val());
                if(new_value) {
                    add_value(form_input.val());
                    form_input.val('');
                }
            }
        }
    });

    if (form_input.val() != '') {
        var self = form_input;
        var values = form_input.val();
        form_input.val('');
        $.each(values.split(options['separator']+' '), function() {
            add_value(this, true);
        });
    }

    function autocomplete_text() {
        return $.trim(form_input.val().split(options['separator']).pop());
    }

    form_input.autocomplete({
        source: function(request, response) {
            var url = options['widget_url'] + '/search_glossary';
            var data = {
                'q': autocomplete_text(),
                'lang': options['lang']
            }
            $.getJSON(url, data, function(data) {
                response(data);
            });
        },
        select: function(event, ui) {
            event.preventDefault();
            add_value(ui.item.value);
            if(list_mode) {
                form_input.val('');
            }
        },
        focus: function() {
            if(! list_mode) {
                return false;
            }
        }
    });

    // hack autocomplete's _renderItem to display matched substrings in bold
    form_input.data("autocomplete")._renderItem = function( ul, item ) {
        var term = autocomplete_text();
        var term_bold = "<span style='font-weight:bold;'>" + term + "</span>";
        var text = item.label.replace(new RegExp(term), term_bold);
        var li = $("<li>").append("<a>" + text + "</a>");
        li.data("item.autocomplete", item);
        return li.appendTo(ul);
    };

    //Open dialog
    var pick_button = $('.glossary-widget-pick', container)
    var dialog_div = $('.glossary-widget-dialog-content', container);
    pick_button.show();
    pick_button.click(function() {
        buttons = {};
        close_text = gettext("Close");
        buttons[close_text] = function() {
            $(this).dialog( "close" );
        };
        dialog_div.show().dialog({
            width: 650,
            height: 500,
            dialogClass: 'glossary-widget-dialog',
            position: 'center',
            buttons: buttons,
            modal: true
        });
        load_tree($('.glossary-widget-tree', dialog_div),
                  $('.glossary-widget-tree-buttons', dialog_div));
    });
}

/**
 * Add a term to the target input when user selects an element in pick tree or
 * autocomplete list.
 *
 */
function add_value(term, skip_animation) {
    var value = $.trim(term);
    if (list_mode) {
        var name = form_input.attr('name');
        var exists = false;
        $('input', values_list).each(function() {
            if($(this).val() == value) {
                exists = true;
            }
        });

        if(! exists) {
            var x_link = $('<a>').attr('href', 'javascript:;');
            x_link.append($("<img>").attr({
                src: WWW_URL + "cross.gif",
                title:'Remove',
                alt: '[x]'
            })).addClass('tick-image icon-image');
            x_link.click(function(){
                var item = $(this).parent();
                text_content.css('backgroundColor', '#f88');
                item.slideUp(300, function() {
                    item.remove();
                });
            });

            var hidden_input = $("<input type='hidden'>");
            hidden_input.attr({name: name, value: value});

            var text_content = $('<span>').text(value);

            var item = $('<li>');
            item.append(text_content, '&nbsp;', x_link, hidden_input);

            item.appendTo(values_list);

            if(! skip_animation) {
                text_content.css('background-color', '#fc6');
                item.hide().slideDown(300, function() {
                    text_content.css('background-color', null);
                });
            }
        }
    }
    else {
        var terms = form_input.val().split(options['separator']+' ');
        if (value != '' && jQuery.inArray(value, terms) == -1){
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push(value);
            // add placeholder to get the comma-and-space at the end
            terms.push("");
            form_input.val(terms.join(options['separator']+' '));
            terms.pop();
        }

        var original_color = form_input.css('backgroundColor');
        form_input.animate({backgroundColor: "#FFF1E1"}, 300, function() {
            $(this).animate({backgroundColor: original_color}, 200);
        });
    }
}

/**
 * Load glossary tree nodes
*/
function load_tree(tree_container, tree_buttons_div) {
    var tree_url = (options['widget_url'] + '/glossary_tree?lang='
                    + options['lang']);
    var our_tree_obj;
    tree_container.tree({
        data:{
            type : "json",
            opts : {url : tree_url}
        },
        callback : {
            onload: function(tree_obj) {
                our_tree_obj = tree_obj; // easiest way to get tree object
            },
            onselect: function(node, tree_obj) {
                var node_value = $(node).attr('glossary-translation');
                if(! node_value) return;
                add_value(node_value);
            }
        },
        ui : {
            theme_name : "classic"
        },
        types : {
            "default" : {
                draggable: false,
                clickable: false
            },
            "insertable": {
                clickable: true
            }
        }
    });

    // expand all
    $('>a:first', tree_buttons_div).unbind('click').click(function(evt) {
        our_tree_obj.open_all();
    });

    // collapse all
    $('>a:last', tree_buttons_div).unbind('click').click(function(evt) {
        our_tree_obj.close_all($('> ul > li', tree_container));
    });
}


}
