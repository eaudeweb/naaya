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
	function check_answers(){
		var submit_ok = false;
		$('[name="answer_ids"]').each(function(){
			if ($(this).attr('checked') == true){
				submit_ok = true;
			}
		});
		if (submit_ok == true)
		{
			return true;
		}
		else{
			alert(gettext('Please select at least one report to generate statistics'));
			return false;
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
	});
}());
