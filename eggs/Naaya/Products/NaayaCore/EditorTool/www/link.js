function init() {
	var inst = tinyMCEPopup.editor;
	var selLink = inst.dom.getParent(inst.selection.getNode(), 'A');
	if(selLink !== null) {
		var url = inst.dom.getAttrib(selLink, 'href');
		if(url !== null && url !== '') {
			document.getElementById('url').value = url;
		}
		var title = inst.dom.getAttrib(selLink, 'title');
		if(title !== null && title !== '') {
			document.getElementById('title').value = title;
		}
		var target = inst.dom.getAttrib(selLink, 'target');
		if(target !== null && target == '_new') {
			document.getElementById('target').selectedIndex = 1;
		}
	}
}

function insert_link() {
	var ctrl_url = document.getElementById('url');
	var inst = tinyMCEPopup.editor;
	var elm;

	elm = inst.selection.getNode();
	checkPrefix(ctrl_url);
	var elm = inst.dom.getParent(elm, 'A');
	// Remove element if there is no href
	if (!ctrl_url.value) {
		tinyMCEPopup.execCommand('mceBeginUndoLevel');
		i = inst.selection.getBookmark();
		inst.dom.remove(elm, 1);
		inst.selection.moveToBookmark(i);
		tinyMCEPopup.execCommand('mceEndUndoLevel');
		tinyMCEPopup.close();
		return;
	}
	tinyMCEPopup.execCommand('mceBeginUndoLevel');
	// Create new anchor elements
	if (elm == null) {
		inst.getDoc().execCommand('unlink', false, null);
		tinyMCEPopup.execCommand('CreateLink', false, '#mce_temp_url#', {skip_undo : 1});
		elementArray = tinymce.grep(inst.dom.select('a'), function(n) {return inst.dom.getAttrib(n, 'href') == '#mce_temp_url#';});
		for (i=0; i<elementArray.length; i++)
			setAllAttribs(elm = elementArray[i]);
	} else {
		setAllAttribs(elm);
	}

	// Don't move caret if selection was image
	if (elm.childNodes.length != 1 || elm.firstChild.nodeName != 'IMG') {
		inst.focus();
		inst.selection.select(elm);
		inst.selection.collapse(0);
		tinyMCEPopup.storeSelection();
	}
	tinyMCEPopup.execCommand('mceEndUndoLevel');
	tinyMCEPopup.close();
}

function setAllAttribs(link) {
	var inst = tinyMCEPopup.editor;
	var dom = tinyMCEPopup.editor.dom;
	var val = getCtrlValue('url');
	dom.setAttrib(link, 'href', val);
	var title = getCtrlValue('title');
	if(title != '') {
		dom.setAttrib(link, 'title', title);
	}
	var tCtrl = document.getElementById('target');
	var target = tCtrl.options[tCtrl.selectedIndex].value;
	dom.setAttrib(link, 'target', target);
}

function checkPrefix(n) {
	if (n.value && Validator.isEmail(n) && !/^\s*mailto:/i.test(n.value) && confirm(tinyMCEPopup.getLang('advlink_dlg.is_email')))
		n.value = 'mailto:' + n.value;

	if (/^\s*www\./i.test(n.value) && confirm(tinyMCEPopup.getLang('advlink_dlg.is_external')))
		n.value = 'http://' + n.value;
}

function getCtrlValue(ctrlId, defaultValue) {
	if(defaultValue == null) { defaultValue = ''; }
	var ret = defaultValue;
	try {
		var value = document.getElementById(ctrlId).value;
		ret = value.replace(/^\s*([\S\s]*?)\s*$/, '$1');
	} catch(e) {}
	if(ret == '') {
		ret = defaultValue;
	}
	return ret
}
