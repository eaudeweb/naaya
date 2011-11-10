/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){

	set_up_info_boxes();
	jQuery("a.suggest_translation").click(add_suggestion);
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
		var info_div = $(this).closest('tr').next();
		info_div.toggle();
	}
}

/**
 * Translate Messages: add an external translate suggestion
*/

function add_suggestion(){
	var jthis = jQuery(this);
	var lang = jthis.attr("name");
	var suggestion = jthis.attr("name");
	jQuery("form[name='translate_" + lang
	       + "'] textarea[name='translation:utf8:ustring']").val(jthis.text());
}
