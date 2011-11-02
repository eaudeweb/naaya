$(document).ready(function(){
	$('.revoke-role').live('click', function(e){
		return confirm(gettext("Are you sure you want to revoke this role?"));
	});
	$('.deluser').live('click', function(e){
		return confirm(gettext("Are you sure you want to remove this user?"));
	});
	$('.delbutton').live('click', function(e){
		return confirm(gettext("Are you sure you want to remove this?"));
	});
});
