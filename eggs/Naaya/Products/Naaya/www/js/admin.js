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
	$('a.info-link').click(toggle_info);

	function toggle_info(evt) {
		evt.preventDefault();
		var info_div = $(this).siblings('div.admin-info-text');
		info_div.toggle();
	}
}
