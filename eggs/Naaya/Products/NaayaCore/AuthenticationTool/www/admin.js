/**
 * User management
*/
$(document).ready(function(){
	/**
	* Show `<Label> per page` when Javascript is enabled
	* (.paginator-details)
	*/
	$('.paginator-details').show();
	$('#search-users').focus();
	$("#search-users-form").attr('action', $("#search-users-form").attr('href'));
	setupSearchUsers();

	$('.revoke-role, .deluser, .delbutton').live('click', function(e){
		return confirm(gettext("Are you sure?"));
	});
	/**
	 * Intercept items/page select change
	*/
	$('#per-page').live('change', function(){
		setupSearchUsers();
		$("#search-users-form").submit();
	});

	//Intercept pagination links
	$('.paginator-pages, .paginator-next, .paginator-previous').live('click', function(e){
		e.preventDefault();
		var data = unserialize($(this).find('a').attr('href').split('?')[1]);
		setupSearchUsers({'per_page': data['per_page'], 'page': data['page'],
						 'skey': data['skey'], 'rkey': data['rkey']});
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

	$('.sort_link').live('click', function(e) {
		e.preventDefault();
        ldap_refresh_users_fieldset($(this).attr('href'));
    });
    ldap_user_search_form();
});

/**
 * Setup user search ajax form. Additional post data can be provided to
 * accommodate sort order, pagination and others
*/
function setupSearchUsers(data){
	var local_data = {
		'template': $('#template').val(),
		'all_users': $('#all_users').val(),
		'per_page': $('#per-page').val()
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

			$('.paginator-details').show();
			$('.deluser').show();

			//Hide delete users button when no users are present
			if ($('#all_users').length == 0 &&
				$('.user-results table').hasClass('empty')){
				$('.deluser').hide();
			}
			toggleLoader();
		}
	});
}

/**
 * Ajax loader
*/
function toggleLoader(){
	$('.loader').toggle();
	$('.ajax-loader').show();
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

function ldap_refresh_users_fieldset(url) {
    $('#users_roles_waiting_response').show();
    $('#users_roles_error_response').hide();

    $.ajax({
        url: url,
        success: function(data) {
            var html = $('#middle_port', $(data)).html();
			$('#middle_port').html(html);
            $('#users_roles_waiting_response').hide();
        },
        error: function() {
            $('#users_roles_waiting_response').hide();
            $('#users_roles_error_response').show();
        }
    });
}

function ldap_user_search_form() {
    $('#frmRoles').ajaxForm({
		beforeSubmit: function() {
			$('#waiting_for_search_results').show();
			$('#search_results_parent').hide();
			$('#error_on_search_results').hide();
		},
		success: function(data) {
			var html = $('#search_results_parent', $(data)).html();
			$('#search_results_parent').html(html);
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
