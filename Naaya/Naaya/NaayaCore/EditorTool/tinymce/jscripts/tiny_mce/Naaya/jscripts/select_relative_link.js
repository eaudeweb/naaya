function init() {
	var isMSIE = (navigator.appName == "Microsoft Internet Explorer");
	if (!isMSIE) {
		tinyMCEPopup.resizeToContent();
	}
}

function selectNyRelativeLink(field_name, url, win, nydocument_url) {
	tinyMCE.openWindow({
		file : "../../Naaya/relative_link.zpt",
		title : "Add/Edit Relative Link",
		width : 420,
		height : 280,
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

function returnNyRelativeLink() {
	var url = getCheckedValue(document.insertLink.url)
	var win = tinyMCE.getWindowArg("window")
	win.document.getElementById(tinyMCE.getWindowArg("input")).value = url
	tinyMCEPopup.close()
}


function getCheckedValue(radioObj) {
	if(!radioObj)
		return ""
	var radioLength = radioObj.length
	if(radioLength == undefined)
		if(radioObj.checked)
			return radioObj.value
		else
			return ""
	for(var i = 0; i < radioLength; i++) {
		if(radioObj[i].checked) {
			return radioObj[i].value
		}
	}
	return ""
}
