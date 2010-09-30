/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){
    $('.autocomplete').each(function(){
        var source = $(this).parents('form').attr('href').
        replace(/http:\/\/[^\/]+\//, '');
        var template = $('#template').val();
        var used = false;
        var content;

        $(this).autocomplete({
            minLenght: 0,
            source: function(request, response) {
                toggleLoader();
                data = {
					query: request.term,
                    template: template,
                    skey: 'name',
                    rkey: 1
				};
                if($('#all_users').length){
                    data['all_users'] = $('#all_users').val();
                }
                $.get(source, data, function(data){
                    $('.datatable').replaceWith(data);
                    toggleLoader();
                });
			},
            search: function(event, ui){
                used = true;
            }
        });

        $(this).keyup(function(keyCode){
            if($(this).val() == ''){
                $(this).autocomplete("search", ' ');
            }
        });
    });
    add_onclick_second_tabs();
    add_onclick_sort_links();
    add_onclick_group_links();
});

function toggleLoader(){
    $('.ajax-loader').toggle();
}

/**
 * Functions for LDAPUserFolder
*/
function select_second_tab(tabid) {
    $('.second_tab_set a.current_sub').removeClass('current_sub');
    if (tabid) {
        $('#'+tabid).addClass('current_sub');
    }
}

function add_onclick_sort_links() {
    $('.sort_link').click(function() {
        show_ldap_users_fieldset($(this).attr('href'));
        return false;
    });
}

function add_onclick_second_tabs() {
    $('.second_tab').click(function() {
        show_ldap_section($(this).attr('id'), $(this).attr('href'));
        return false;
    });
}

function add_onclick_group_links() {
    $('.group_link').click(function() {
        show_ldap_section('', $(this).attr('href'));
        return false;
    });
}

function show_ldap_section(tabid, url) {
    select_second_tab(tabid);

    $('#section_wating_response').show();
    $('#section_parent').hide();

    $.ajax({
        url: url,
        success: function(data) {
            var html = $("#section_parent", $(data)).html();
            $('#section_parent').html(html);

            if (tabid == 'link_manage_all') {
                add_onclick_sort_links();
                add_onclick_group_links();
            }

            $('#section_wating_response').hide();
            $('#section_parent').show();
        },
        error: function() {
            $('#section_wating_response').hide();
            $('#section_error_response').show();
        }
    });
}

function show_ldap_users_fieldset(url) {
    $('#users_roles_wating_response').show();

    $.ajax({
        url: url,
        success: function(data) {
            var html = $("#users_field", $(data)).html();
            $('#users_field').html(html);

            add_onclick_sort_links();

            $('#users_roles_wating_response').hide();
        },
        error: function() {
            $('#users_roles_wating_response').hide();
            $('#users_roles_error_response').show();
        }
    });
}
/**
 * End Functions for LDAPUserFolder
*/
