/**
 * User management
*/
$(document).ready(function(){
    $('.autocomplete').each(function(){
        var source = $(this).parents('form').attr('href').
        replace(/http:\/\/[^\/]+\//, '');
        var template = $('#template').val();
        var content;

        var self = $(this)

        self.autocomplete({
            minLength: 3,
            delay: 300,
            source: function(request, response) {
                toggleLoader();
                var search_query = window.location.search;
                if (search_query[0] == '?'){ //remove first ?
                    search_query = search_query.substr(1);
                }
                data = unserialize(search_query); //utils.js
                data['query']=request.term;
                data['template'] = template;
                data['role'] = $('#filter-roles').val();
                if ($('#all_users').length){
                    data['all_users'] = $('#all_users').val();
                }
                $.get(source, data, function(data){
                    $('.datatable').replaceWith(data);
                    toggleLoader();
                });
			}
        });

        self.keyup(function(keyCode){
            if ($(this).val() == ''){
                $(this).autocomplete("search", '   ');
            }
        });

        $('#filter-roles').change(function(e){
			if (self.val() == ''){
				self.autocomplete('search', '   ');
			}else{
				self.autocomplete('search', self.val());
			}
        });
    });
    ldap_onclick_sort_links();
    ldap_onclick_group_links();
    ldap_user_search_form();
});
function toggleLoader(){
    $('.ajax-loader').toggle();
    if ($('#autocomplete-query').attr("disabled") === true){
        $('#autocomplete-query').attr("disabled", "");
        $('#autocomplete-query').focus();
    }else{
        $('#autocomplete-query').attr("disabled", "disabled");
    }
}

function emptyLocation(){
   if (document.forms['frmUsersRoles'].loc[0].checked == true)
       document.forms['frmUsersRoles'].location.value = '';
}

function pickLocation(){
   document.forms['frmUsersRoles'].loc[1].checked = true;
}

function setupWin(url, theWidth, theHeight){
   pickLocation();
   wwinn=window.open(url,'wwinn','width='+theWidth+',height='+theHeight+',scrollbars,top=50,left=600');
   wwinn.focus();
   return true;
}

function createKey(key){
   document.forms['frmUsersRoles'].location.value = key;
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

function ldap_show_section(data) {
    var html = $('#middle_port', $(data)).html();
    $('#middle_port').html(html);
}

function ldap_ajax_section_manage_all() {
    ldap_onclick_sort_links();
    ldap_onclick_group_links();
}

function ldap_ajax_section_assign_to_users() {
    ldap_user_search_form();
}

function ldap_ajax_section_assign_to_groups() {
}

function ldap_refresh_section(tabid, url) {
    select_second_tab(tabid);
    $('#section_wating_response').show();
    $('#section_parent').hide();
    $('#section_error_response').hide();

    $.ajax({
        url: url,
        success: function(data) {
            ldap_show_section(data);

            if (tabid == 'link_manage_all') {
                ldap_ajax_section_manage_all();
            } else if (tabid == 'link_assign_to_users') {
                ldap_ajax_section_assign_to_users();
            } else if (tabid == 'link_assign_to_groups') {
                ldap_ajax_section_assign_to_groups();
            }

            $('#section_wating_response').hide();
        },
        error: function() {
            $('#section_wating_response').hide();
            $('#section_error_response').show();
        }
    });
}

function ldap_onclick_sort_links() {
    $('.sort_link').click(function() {
        ldap_refresh_users_fieldset($(this).attr('href'));
        return false;
    });
}

function ldap_onclick_group_links() {
    $('.group_link').click(function() {
        ldap_refresh_section('', $(this).attr('href'));
        return false;
    });
}

function ldap_refresh_users_fieldset(url) {
    $('#users_roles_waiting_response').show();
    $('#users_roles_error_response').hide();

    $.ajax({
        url: url,
        success: function(data) {
            ldap_show_section(data);
            ldap_ajax_section_manage_all();

            $('#users_roles_waiting_response').hide();
        },
        error: function() {
            $('#users_roles_waiting_response').hide();
            $('#users_roles_error_response').show();
        }
    });
}

function ldap_show_user_search_results(data) {
    var html = $('#search_results_parent', $(data)).html();
    $('#search_results_parent').html(html);
}

function ldap_user_search_form() {
    $('#frmRoles').ajaxForm({
    beforeSubmit: function() {
        $('#waiting_for_search_results').show();
        $('#search_results_parent').hide();
        $('#error_on_search_results').hide();
    },
    success: function(data) {
        ldap_show_user_search_results(data);

        $('#waiting_for_search_results').hide();
        $('#search_results_parent').show();
    },
    error: function() {
        $('#error_on_search_results').show();
        $('#waiting_for_search_results').hide();
    }
    });
}

/**
 * End Functions for LDAPUserFolder
*/
