$(document).ready(function() {
	show_hide('f_format_availability_url', 1, 'f_format_availability_paper_or_web_web');
	$('#f_format_availability_paper_or_web_web').change(function(){
		show_hide('f_format_availability_url', 1, 'f_format_availability_paper_or_web_web');
	});
	$('#f_format_availability_paper_or_web_paperonly').change(function(){
		show_hide('f_format_availability_url', 1, 'f_format_availability_paper_or_web_web');
	});

	show_hide('f_structure_eea_indicators_estimated_no', 2, 'f_structure_eea_indicators_Yes');
	$('#f_structure_eea_indicators_Yes').change(function(){
		show_hide('f_structure_eea_indicators_estimated_no', 2, 'f_structure_eea_indicators_Yes');
	});
	$('#f_structure_eea_indicators_No').change(function(){
		show_hide('f_structure_eea_indicators_estimated_no', 2, 'f_structure_eea_indicators_Yes');
	});

	function show_hide(field_id, hide_parents, dependent_by){
		if ($('#'+dependent_by+':checked').length > 0){
			if (hide_parents == 1){
				$('#'+field_id).parent().show();
			}
			else if (hide_parents == 2){
				$('#'+field_id).parent().parent().show();
			}
		}
		else{
			$('#'+field_id).val("");
			if (hide_parents == 1){
				$('#'+field_id).parent().hide();
			}
			else if (hide_parents == 2){
				$('#'+field_id).parent().parent().hide();
			}
		}
}
})
