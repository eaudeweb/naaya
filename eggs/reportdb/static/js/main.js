$(document).ready(function() {
	$('input[type="radio"]').dblclick(function(){
		$(this).removeAttr('checked');
	})
/*	$('#f_header_soer_cover').change(function(){
		var text = $('#f_header_soer_cover').val();
		$.get('/translate', {'text': text, dest_lang: 'en', src_lang: 'ro'}, 
		function(data){
			if (data.length>0){
				if ($('#f_details_original_name').val().length == 0 ||
					$('#f_details_original_name').val().split(': ')[0] == 'Google translation'){
					$('#f_details_original_name').val('Google translation: '+data);
				}
			}
		});
	})*/
})