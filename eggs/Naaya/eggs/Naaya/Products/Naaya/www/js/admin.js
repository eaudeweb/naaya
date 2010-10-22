/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){
	$('.datatable td.checkbox input[type="checkbox"]').click(function(){
		if($(this).attr('class') != 'select-all'){
			if($(this).attr('checked') == false){
				$('.select-all').attr('checked', false);
				$(this).attr('checked', false);
			}else {
				var not_all = false;
				
				$.each($('.datatable td.checkbox input[type="checkbox"]'), function(i, e){
					if($(this).attr('checked') == false){
						not_all = true;
					}
				});
				
				if(not_all == false){
					$('.select-all').attr('checked', true);
				}
			}
		}
	});
	
    $('.autocomplete').each(function(){
        var source = $(this).parents('form').attr('href').
        replace(/http:\/\/[^\/]+\//, '');
        var template = $('#template').val();
        var content;

        var self = $(this)

        self.autocomplete({
            minLength: 3,
            delay: 500,
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
                if($('#all_users').length){
                    data['all_users'] = $('#all_users').val();
                }
                $.get(source, data, function(data){
                    $('.datatable').replaceWith(data);
                    toggleLoader();
                });
			}
        });
	});
});
	
function toggleLoader(){
    $('.loader').toggle();
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

    ldap_onclick_second_tabs();
}

function ldap_ajax_section_manage_all() {
    ldap_onclick_sort_links();
    ldap_onclick_group_links();
    ldap_user_roles_revoke_form();
    ldap_group_roles_revoke_form();
}

function ldap_ajax_section_assign_to_users() {
    ldap_user_search_form();
}

function ldap_ajax_section_assign_to_groups() {
    ldap_group_roles_assign_form();
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

function ldap_onclick_second_tabs() {
    $('.second_tab').click(function() {
        ldap_refresh_section($(this).attr('id'), $(this).attr('href'));
        return false;
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

function ldap_user_roles_revoke_form() {
    $('#users_table').ajaxForm({
    beforeSubmit: function() {
        $('#users_roles_waiting_response').show();
        $('#users_roles_error_response').hide();
    },
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

function ldap_group_roles_revoke_form() {
    $('#groups_table').ajaxForm({
    beforeSubmit: function() {
        $('#groups_roles_waiting_response').show();
        $('#groups_roles_error_response').hide();
    },
    success: function(data) {
            ldap_show_section(data);
            ldap_ajax_section_manage_all();

            $('#groups_roles_waiting_response').hide();
    },
    error: function() {
        $('#groups_roles_waiting_response').hide();
        $('#groups_roles_error_response').show();
    }
    });
}

function ldap_show_user_search_results(data) {
    var html = $('#search_results_parent', $(data)).html();
    $('#search_results_parent').html(html);

    ldap_user_roles_assign_form();
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

function ldap_user_roles_assign_form() {
    $('#search_results_form').ajaxForm({
    beforeSubmit: function() {
        var firstuser = $('input[name="name:list"]:checked').val();
        if (!firstuser) {
            $('#portal_users_empty').show();
        } else {
            $('#portal_users_empty').hide();
        }
        var roles = $('#portal_roles').val();
        if (!roles) {
            $('#portal_roles_empty').show();
        } else {
            $('#portal_roles_empty').hide();
        }
        if (!firstuser || !roles) {
            return false;
        }
        $('#assign_users_waiting_response').show();
        $('#assign_users_error_response').hide();
    },
    success: function(data) {
        ldap_show_section(data);
        ldap_ajax_section_assign_to_users();

        $('#assign_users_waiting_response').hide();
    },
    error: function() {
        $('#assign_users_waiting_response').hide();
        $('#assign_users_error_response').show();
    }
    });
}

function ldap_group_roles_assign_form() {
    $('#group_roles_form').ajaxForm({
    beforeSubmit: function() {
        var group = $('#ldap_group').val();
        var roles = $('#portal_roles').val();
        if (!group) {
            $('#ldap_group_empty').show();
        } else {
            $('#ldap_group_empty').hide();
        }
        if (!roles) {
            $('#portal_roles_empty').show();
        } else {
            $('#portal_roles_empty').hide();
        }
        if (!group || !roles) {
            return false;
        }
        $('#assign_groups_waiting_response').show();
        $('#assign_groups_error_response').hide();
    },
    success: function(data) {
        ldap_show_section(data);
        ldap_ajax_section_assign_to_groups();

        $('#assign_groups_waiting_response').hide();
    },
    error: function() {
        $('#assign_groups_waiting_response').hide();
        $('#assign_groups_error_response').show();
    }
    });
}


/**
 * End Functions for LDAPUserFolder
*/

/**
 * Show Items Per Page
 *
 * @param		string		url
*/
function showPerPageItems(url){
	per_page = parseInt($('#per-page').val());
	if(per_page == 0){
		alert("Please choose a number from 'Items per page' list!");
		return false;
	}
	
	return window.location = url + '?per_page=' + per_page;
}

/**
 * Select all checkboxes from a datatable
*/

function selectAll(name){
	$('.datatable td.checkbox input[@name="' + name + '"][type="checkbox"]').attr('checked', $('.select-all').attr('checked'));
	return false;
}