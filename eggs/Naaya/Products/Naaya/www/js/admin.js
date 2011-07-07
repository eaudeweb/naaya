/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){

	set_up_info_boxes();

});

/**
 * Select all checkboxes from a datatable
*/

function selectAll(name){
	$('.datatable td.checkbox input[@name="' + name + '"][type="checkbox"]').attr('checked', $('.select-all').attr('checked'));
	return false;
}

function set_up_info_boxes() {
	$('div.admin-info-text').each(function() {
		var button = $('<a class="right info-link">').text("Details").click(toggle_info);
		button.attr('href', 'javascript:void(0);');
		$(this).before(button);
	});

	function toggle_info(evt) {
		evt.preventDefault();
		var info_div = $(this).siblings('div.admin-info-text');
		info_div.toggle();
	}
}
