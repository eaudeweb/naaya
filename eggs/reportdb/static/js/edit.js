$(document).ready(function() {

	if ($('#f_format_report_type_portaldynamicsource:checked').length > 0){
		$('#f_format_availability_paper_or_web_paperonly')
			.attr('disabled', 'disabled');
		if($('#f_format_availability_paper_or_web_paperonly:checked').length > 0){
			$('#f_format_availability_paper_or_web_paperonly')
				.removeAttr('checked');
		}
	}
	$('input[name="format_report_type"]').change(function(){
		if ($('#f_format_report_type_portaldynamicsource:checked').length > 0){
			$('#f_format_availability_paper_or_web_paperonly')
				.attr('disabled', 'disabled');
			if($('#f_format_availability_paper_or_web_paperonly:checked').length > 0){
				$('#f_format_availability_paper_or_web_paperonly')
					.removeAttr('checked');
			}
		}
		else{
			$('#f_format_availability_paper_or_web_paperonly')
				.removeAttr('disabled');
		}
	})
	show_hide($('#f_format_availability_url').parent(),
			['f_format_availability_paper_or_web_webonly',
			'f_format_availability_paper_or_web_webandprint']);
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_url').parent(),
				['f_format_availability_paper_or_web_webonly',
				'f_format_availability_paper_or_web_webandprint']);
	});
	show_hide($('#f_format_availability_costs_withcosts').parent(),
			['f_format_availability_paper_or_web_paperonly',
			'f_format_availability_registration_required_1']);
	if ($('input[name="format_availability_costs"]:visible').length == 0){
		$('#f_format_availability_costs_free').attr('checked', 'checked');
	}
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_costs_withcosts').parent(),
				['f_format_availability_paper_or_web_paperonly',
				'f_format_availability_registration_required_1']);
		if ($('input[name="format_availability_costs"]:visible').length == 0){
			$('#f_format_availability_costs_free').attr('checked', 'checked');
		}
	});
	$('input[name="format_availability_registration_required"]').change(function(){
		show_hide($('#f_format_availability_costs_withcosts').parent(),
				['f_format_availability_paper_or_web_paperonly',
				'f_format_availability_registration_required_1'], 'slow');
		if ($('input[name="format_availability_costs"]:visible').length == 0){
			$('#f_format_availability_costs_free').attr('checked', 'checked');
		}
	});

	$('#f_format_availability_registration_required_1').parent().hide();
	/*show_hide($('#f_format_availability_registration_required_1').parent(),
			['f_format_availability_paper_or_web_webonly',
			'f_format_availability_paper_or_web_webandprint']);
	$('input[name="format_availability_paper_or_web"]').change(function(){
		show_hide($('#f_format_availability_registration_required_1').parent(),
				['f_format_availability_paper_or_web_webonly',
				'f_format_availability_paper_or_web_webandprint']);
	});*/

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
				['f_format_report_type_portaldynamicsource']);
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

	var subregions_dict;//regions_dict, all_countries;
	/*$.ajax({
		url: 'get_regions',
		dataType: "json",
		async: false,
		success: function(data){
			regions_dict = data;
		}
	});
	$.ajax({
		url: 'get_countries',
		dataType: "json",
		async: false,
		success: function(data){
			all_countries = data;
		}
	});*/
	$.ajax({
		url: 'get_subregions',
		dataType: "json",
		async: false,
		success: function(data){
			subregions_dict = data;
		}
	});

	//process_regions(true);
	process_countries(true);
	process_subregions(true);

	/*$('#f_header_region').change(function(){
		process_countries();
		process_subregions();
	});*/

	$('#f_header_country').change(function(){
		//process_regions();
		process_subregions();
	});

	$('#f_header_subregion').change(function(){
		//process_regions();
		process_countries();
		process_subregions();
	});

	if ($('#f_header_country option').length == 1)
	{
		setTimeout(function(){
				$('#f_header_country').select2('disable');
		}, 1);
	}

	/*function process_regions(onload){
		var selected_regions = get_list('region', true);
		var selected_countries = get_list('country', true);
		$.each(selected_regions, function(index, region){
			var invalid_region = true;
			var region_countries = regions_dict[region];
			$.each(region_countries, function(index, country){
				var sel_index = indexOf(country, selected_countries);
				if(sel_index !== -1){
					invalid_region = false;
				}
			});
			if (invalid_region === true){
				$('#f_header_region option[value="'+region+'"]').removeAttr('selected');
				$('#f_header_region').select2();
			}
		});
	}*/

	function process_countries(onload){
		if (onload)
		{
			$.ajax({
				url: 'get_countries',
				dataType: "json",
				async: false,
				success: function(data)
				{
					for (var i=0;i<data.length;i++)
					{
						$('#f_header_country option').each(function(){
							if (indexOf(this.value, data) == -1)
								$(this).remove()
						})
					}
					if (data.length == 1)
					{
						$('#f_header_country option[value="'+data[0]+'"]')
							.attr('selected', 'selected');
						$('#f_header_country').select2('disable');
					}
				}
			});
		}
		else {
			//var selected_regions = get_list('region', true);
			var selected_countries = get_list('country', true);
			var selected_subregions = get_list('subregion', true);
			/*$.each(selected_regions, function(index, region){
				var new_region = true;
				$.each(regions_dict[region], function(index, country){
					if (indexOf(country, selected_countries) !== -1){
						new_region = false;
						return false;
					}
				});
				if (new_region === true){
					$.each(regions_dict[region], function(index, country){
						$('#f_header_country option[value="'+country+'"]')
							.attr('selected', 'selected');
					});
					$('#f_header_country').select2();
				}
			});*/
			$.each(selected_countries, function(index,country){
				if(subregions_dict[country] !== undefined){
					var country_subregions = subregions_dict[country];
					var invalid_country = true;
					$.each(country_subregions, function(index, subregion){
						var sel_index = indexOf(subregion, selected_subregions);
						if (sel_index !== -1){
							invalid_country = false;
						}
					});
					if(invalid_country === true){
						$('#f_header_country option[value="'+country+'"]').removeAttr('selected');
						$('#f_header_country').select2();
					}
				}
			});
		}
	}

	function process_subregions(onload){
		var selected_countries = get_list('country', true);
		var selected_subregions = get_list('subregion', true);
		var subregions = get_list('subregion', false);
		var changed = false;

		$.each(selected_subregions, function(index,subregion){
			var parent_country = get_parent_country(subregion);
			if(indexOf(parent_country, selected_countries) === -1){
				changed = true;
				$('#f_header_subregion option[value="'+subregion+'"]').remove();
				//$('#f_header_subregion option[value="'+subregion+'"]').removeAttr('selected');
			}
		});

		$.each(subregions_dict, function(country, subregions){
			var sel_index = indexOf(country, selected_countries);
			if (sel_index === -1){
				$.each(subregions, function(index, subregion){
					$('#f_header_subregion option[value="'+subregion+'"]').remove();
				})
			}
		});

		$.each(selected_countries, function(index, country){
			if (country in subregions_dict){
				var new_country = true;
				$.each(subregions_dict[country], function(index, subregion){
					if (indexOf(subregion, selected_subregions) !== -1){
						new_country = false;
						return false;
					}
				});
				if (new_country === true){
					changed = true;
					$.each(subregions_dict[country], function(index, subregion){
						$('#f_header_subregion')
							.append('<option value="'+subregion+'">'+subregion+'</option>');
						$('#f_header_subregion option[value="'+subregion+'"]')
							.attr('selected', 'selected');
					});
				}
			}
		});

		selected_subregions = get_list('subregion', true);
		if (selected_subregions.length === 0){
			$('#f_header_subregion').parent().parent().slideUp(300);
		}
		else if ($('#f_header_subregion').parent().parent().css('display') === 'none'){
			$('#f_header_subregion').parent().parent().slideDown(300);
		}

		if (changed && !onload){
			$('#f_header_subregion').select2();
		}
	}

	function get_parent_country(subregion){
		var parent_country;
		$.each(subregions_dict, function(country,subregions_list){
			if(indexOf(subregion, subregions_list) !== -1){
				parent_country = country;
				return false;
			}
		});
		return parent_country;
	}

	function get_list(list, selected){
		selected = selected || false;
		var selected_list = [];
		if (selected){
			$('#f_header_'+list+' option:selected').each(function(){
				selected_list.push($(this).val());
			});
		}
		else{
			$('#f_header_'+list).each(function(){
				selected_list.push($(this).val());
			});
		}
		return selected_list;
	}

	function get_selected_subregions(){
		var subregions_list = [];
		$('#f_header_subregion option:selected').each(function(){
			subregions_list.push($(this).val());
		});
		return subregions_list;
	}

	function get_selected_countries(){
		var countries_list = [];
		$('#f_header_country option:selected').each(function(){
			countries_list.push($(this).val());
		});
		return countries_list;
	}

	function show_hide(field, dependent_by, slow){
		if (dependent_by !== undefined)
		{
			var found = false;
			for (var i=0; i<dependent_by.length;i++){
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
	}

	function indexOf(string, array){
		if(array !== undefined)
		{
			var index = -1;
			for(var i=0; i<array.length; i++){
				if(array[i]===string){
					index = i;
					break;
				}
			}
			return index;
		}
	}

});
