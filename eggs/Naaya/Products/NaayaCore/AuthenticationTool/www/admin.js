$(document).ready(function(){
	$('.revoke-role').live('click', function(e){
		return confirm(gettext("Are you sure you want to revoke this role?"));
	});
	$('.deluser').live('click', function(e){
		return confirm(gettext("Are you sure you want to remove this user?"));
	});
	$('.revoke_roles').live('click', function(e){
		return confirm(gettext("Are you sure you want to revoke these roles?"));
	});
	$('.delbutton').live('click', function(e){
		return confirm(gettext("Are you sure you want to remove this?"));
	});

	function show_hide_filter_locations() {
		if ($('#filter-roles option:selected').val() == 'noroles') {
			$('#filter-locations').parent().hide();
		} else {
			$('#filter-locations').parent().show();
		}
	}

	$('#filter-roles').change(show_hide_filter_locations);
	show_hide_filter_locations();
});
