/**
 * User management
*/
$(document).ready(function(){
	$('#search-users').focus();
	setupSearchUsers();

	/**
	 * Intercept items/page select change
	*/
	$('#per-page').live('change', function(){
		setupSearchUsers({'per_page': $(this).val()});
		$("#search-users-form").submit();
	});

	//Intercept pagination links
	$('.paginator-pages, .paginator-next, .paginator-previous').live('click', function(e){
		e.preventDefault();
		var data = unserialize($(this).find('a').attr('href'));

		setupSearchUsers({'per_page': data['per_page'], 'page': data['page']});
		$("#search-users-form").submit();
		setupSearchUsers();
	});

	$('.sort-key').live('click', function(e){
		e.preventDefault();
		var data = unserialize($(this).attr('href').split('?')[1]);
		setupSearchUsers(data);
		$("#search-users-form").submit();
		setupSearchUsers();
	});

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


    ldap_onclick_sort_links();
    ldap_onclick_group_links();
    ldap_user_search_form();
});

/**
 * Setup user search ajax form. Additional post data can be provided to
 * acomodate sort order, pagination and others
*/
function setupSearchUsers(data){
	var local_data = {
		'template': $('#template').val(),
		'all_users': $('#all_users').val()
	};

	if (data){//Extend default post key/values if additional data provided
		for (i in data){
			local_data[i] = data[i]
		}
	}

	$("#search-users-form").ajaxForm({
		data: local_data,
		beforeSubmit: function(arr, form, options) {
			toggleLoader();
		},
		success: function(data) {
			$('.user-results').replaceWith(data);
			toggleLoader();
		}
	});
}

function toggleLoader(){
	$('.loader').toggle();
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
			load_js_tree();
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


