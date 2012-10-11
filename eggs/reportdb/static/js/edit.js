$(document).ready(function() {
	show_hide($('#f_format_availability_costs_withcosts').parent(),
			  ['f_format_availability_paper_or_web_paperonly',
			   'f_format_availability_registration_required_1']);
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_costs_withcosts').parent(),
				  ['f_format_availability_paper_or_web_paperonly',
				   'f_format_availability_registration_required_1']);
	});
	$('input[name="format_availability_registration_required"]').change(function(){
		show_hide($('#f_format_availability_costs_withcosts').parent(),
				  ['f_format_availability_paper_or_web_paperonly',
				   'f_format_availability_registration_required_1'], 'slow');
	});

	show_hide($('#f_format_availability_registration_required_1').parent(),
			  ['f_format_availability_paper_or_web_web']);
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_registration_required_1').parent(),
				  ['f_format_availability_paper_or_web_web']);
	});

	show_hide($('.static-source').parent().parent(),
			  ['f_format_report_type_reportstaticsource']);
	$('input[name="format_report_type"]').change(function(){
		show_hide($('.static-source').parent().parent(),
				  ['f_format_report_type_reportstaticsource']);
	});

	show_hide($('.dynamic-source').parent().parent(),
			  ['f_format_report_type_portalsdynamicsource']);
	$('input[name="format_report_type"]').change(function(){
		show_hide($('.dynamic-source').parent().parent(),
				  ['f_format_report_type_portalsdynamicsource']);
	});

	show_hide($('#f_format_availability_url').parent(),
			  ['f_format_availability_paper_or_web_web']);
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_url').parent(),
				  ['f_format_availability_paper_or_web_web']);
	});

	show_hide($('select[name="structure_indicators_estimation"]').parent().parent(),
			  ['f_structure_indicator_based_Yes'], 'slow');
	$('input[name="structure_indicator_based"]').change(function(){
		show_hide($('select[name="structure_indicators_estimation"]').parent().parent(),
				  ['f_structure_indicator_based_Yes'], 'slow');
	});

	show_hide($('.indicators-table').parent().parent(),
			  ['f_structure_indicator_based_Yes'], 'slow');
	$('input[name="structure_indicator_based"]').change(function(){
		show_hide($('.indicators-table').parent().parent(),
			  ['f_structure_indicator_based_Yes'], 'slow');
	});

	show_hide($('#f_structure_indicators_usage_evaluation_method').parent(),
			  ['f_structure_indicators_usage_to_evaluate_Most50',
			   'f_structure_indicators_usage_to_evaluate_Some50']);
	$('input[name="structure_indicators_usage_to_evaluate"]').change(function(){
		show_hide($('#f_structure_indicators_usage_evaluation_method').parent(),
			  ['f_structure_indicators_usage_to_evaluate_Most50',
			   'f_structure_indicators_usage_to_evaluate_Some50']);
	});

	function show_hide(field, dependent_by, slow){
		var found = false;
		for (i=0; i<dependent_by.length;i++){
			if ($('#'+dependent_by[i]+':checked').length > 0){
				found = true;
			}
		}
		if (found){
			if (slow){
				$(field).slideDown();
			}
			else{
				$(field).show();
			}
		}
		else{
			if (slow){
				$(field).slideUp();
			}
			else{
				$(field).hide();
			}
		}
	}
})
