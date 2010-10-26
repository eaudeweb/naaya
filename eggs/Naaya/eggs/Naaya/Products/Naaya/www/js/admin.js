/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){

});

/**
 * Select all checkboxes from a datatable
*/

function selectAll(name){
	$('.datatable td.checkbox input[@name="' + name + '"][type="checkbox"]').attr('checked', $('.select-all').attr('checked'));
	return false;
}
