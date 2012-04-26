$(document).ready(function() {
	show_hide($('#f_format_availability_url').parent(),
			  ['f_format_availability_paper_or_web_web']);
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_url').parent(),
				  ['f_format_availability_paper_or_web_web']);
	});

	show_hide($('select[name="structure_indicators_estimation"]').parent().parent(),
			  ['f_structure_indicator_based_Yes']);
	$('input[name="structure_indicator_based"]').change(function(){
		show_hide($('select[name="structure_indicators_estimation"]').parent().parent(),
				  ['f_structure_indicator_based_Yes']);
	});

	show_hide($('#f_structure_eea_indicators_estimated_no').parent().parent(),
			  ['f_structure_eea_indicators_Yes']);
	$('input[name="structure_eea_indicators"]').change(function(){
		show_hide($('#f_structure_eea_indicators_estimated_no').parent().parent(),
				  ['f_structure_eea_indicators_Yes']);
	});

	show_hide($('#f_structure_indicators_usage_evaluation_method').parent(),
			  ['f_structure_indicators_usage_to_evaluate_Most50',
			   'f_structure_indicators_usage_to_evaluate_Some50']);
	$('input[name="structure_indicators_usage_to_evaluate"]').change(function(){
		show_hide($('#f_structure_indicators_usage_evaluation_method').parent(),
			  ['f_structure_indicators_usage_to_evaluate_Most50',
			   'f_structure_indicators_usage_to_evaluate_Some50']);
	});

	function show_hide(field, dependent_by){
		var found = false;
		for (i=0; i<dependent_by.length;i++){
			if ($('#'+dependent_by[i]+':checked').length > 0){
				found = true;
			}
		}
		if (found){
			$(field).show();
		}
		else{
			$(field).hide();
		}
	}
})
