function selectNyImage(field_name, url, win, nydocument_url) {
	tinyMCE.openWindow({
		file : "../../Naaya/image_upload_dialog.zpt?document=" + nydocument_url,
		title : "File Browser",
		width : 420,
		height : 400,
		close_previous : "no"
	}, {
		window : win,
		input : field_name,
		resizable : "yes",
		scrollbars : "yes",
		inline : "yes",  // This parameter only has an effect if you use the inlinepopups plugin!
		editor_id : tinyMCE.selectedInstance.editorId
	});
}

function returnImageUrl(url) {
	var win = tinyMCE.getWindowArg("window");
	var inp_src = tinyMCE.getWindowArg("input");
	var image_url = win.document.getElementById(inp_src);
	image_url.value = url;
	win.showPreviewImage(image_url.value);
	// update image dimensions
	if (win.getImageData){
		win.getImageData()
	}
	tinyMCEPopup.close()
}
