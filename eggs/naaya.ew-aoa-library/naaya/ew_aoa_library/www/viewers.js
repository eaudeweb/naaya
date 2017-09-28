(function(){
	function filter_by_searchbox() {
		var searchString = $('#searchbox').val();
		if (searchString.length > 0){
			reset_checkboxes();
			$('.datatable tbody tr').hide();
			$('.datatable tr:icontains('+searchString+')').show();
		}
		else {
		  $('.datatable tr').show();
		}
	}
	function select_checkboxes(){
		$('[name="answer_ids"]').each(function(){
			if ($(this).parent().parent().css('display') != 'none')
			{
				$(this).attr('checked', 'checked');
			}
		});
		$('#reset_checkboxes').attr('checked', 'checked');
	}
	function reset_checkboxes(){
		$('[name="answer_ids"]').removeAttr('checked');
		$('#reset_checkboxes').removeAttr('checked');
	}
	function show_filters(){
		$('#advanced_filters').show();
		$('#show_filters').hide();
		$('#hide_filters').show();
	}
	function hide_filters(){
		$('#advanced_filters').hide();
		$('#show_filters').show();
		$('#hide_filters').hide();
	}
	function display_topics(selected_value){
		if (selected_value == null)
		{
			$('label[for="topics"]').hide();
			$('[name="topics"]').hide();
		}
		else{
			$('label[for="topics"]').css('display', 'block');
			$('[name="topics"]').show();
			$('[name="topics"] option').hide();
			for (i=0; i<selected_value.length; i++){
				$('.'+selected_value[i]).show();
			}
		}
	}

	$(document).ready(function(){
		$('#javascript_label').hide();
		$('#filter_box').show();
		/*Search in page*/
		$.expr[':'].icontains = function(obj, index, meta, stack){
			return (obj.textContent || obj.innerText || jQuery(obj).text() || '').toLowerCase().indexOf(meta[3].toLowerCase()) >= 0;
		};
		$('#searchbox').keyup(filter_by_searchbox);
		if ($('#searchbox').val()) {
			filter_by_searchbox();
		}
		if ($('#answers_filter').val() == 'False'){
			select_toggle = 'Off'
		}
		else{
			select_toggle = 'On'
		};
		if (select_toggle == 'On'){
			select_checkboxes();
			show_filters();
		}
		$('#reset_checkboxes').click(function(){
			if (select_toggle == 'Off'){
				select_toggle = 'On';
				select_checkboxes();
			}
			else{
				select_toggle = 'Off';
				reset_checkboxes();
			}
		});
		$('#show_filters').click(function(){
			show_filters();
		});
		$('#hide_filters').click(function(){
			hide_filters();
		});
		display_topics($('[name="themes"]').val());
		$('[name="themes"]').change(function(){
			display_topics($('[name="themes"]').val());
			$('[name="topics"] option').removeAttr('selected');
		});
		$('.update_geo_location').change(function(){
			select_box = $(this).parent().parent().find('input[name="answer_ids"]');
			update_geo_location = $.trim($(this).val());
			if (update_geo_location.length>0){
				select_box.attr('checked', 'checked');
			}
			else{
				select_box.removeAttr('checked');
			}
		});
		$('#show_only_missing').removeAttr('checked');
		$('#show_only_missing').change(function(){
			if ($('#show_only_missing:checked').length == 1){
				$('.missing_coordinates').each(function(){
					if ($(this).val() == 0){
						$(this).parent().parent().remove();
					}
				});
			}
			else{
				window.setTimeout('location.reload()', 1);
			}
		});
		$('form[name="select_for_report"]').submit(function(){
			var submit_ok = false;
			if ($('[name="answer_ids"]:checked').length > 0)
			{
				return true;
			}
			else{
				alert(gettext('Please select at least one report!'));
				return false;
			}
		});
		function verify_relevance(){
			var checked = $('[name="answer_ids"]:checked');
			if(checked.length>0){
				$('[name="answer_ids"]').each(function(){
					if ($(this).attr('checked') != true){
						$(this).parent().parent().hide();
					}
				});
				var has_address = false;
				$('[name="geo_location:utf8:ustring"]:visible').each(function(){
					if($(this).val()){
						has_address = true;
					};
				});
				return has_address;
			}
		}
		$('input[name="update_locations:method"]').click(function(){
			if(verify_relevance()){
				$('[name="answer_ids"]').each(function(){
					if ($(this).attr('checked') != true){
						$(this).parent().parent().remove();
					}
				});
				$('[name="geo_location:utf8:ustring"]').each(function(){
					if(!$(this).val()){
						$(this).parent().parent().remove();
					};
				});
			}
			return true;
		});
	});
}());
