$(document).ready(function(){
	$('#allocate_keywords').click(function(e){
		e.preventDefault();
		fAllocateKeywords();
	});
		console.log($('.select-all'));
	$('.keywords-select-all').click(function(e){
		//Select toggle for all items
		var checked = !$(this).attr('checked');
		$('.checked_paths').attr('checked', !checked);
	});
});

function fAllocateKeywords(){
	if ($("#folderfile_list td.checkbox input[type=checkbox]:checked").length == 0){
		mesg = gettext('Please select on or more items for which you want to allocate keywords');
		alert(mesg);
		return false;
	}
	document.objectItems.action="allocate_keywords_html";
	document.objectItems.submit();
}
