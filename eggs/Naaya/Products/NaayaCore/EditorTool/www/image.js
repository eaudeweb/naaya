/**
 * Operations on image preparation after being selected. Sets various image
 * attributes such as: border, padding, margin, title etc.
 */
function ImagePreparer() {
	this.imgObject = null;
	this.url = null;
	this.oWidth = 0;
	this.oHeight = 0;
	this.ctrls = {};
	this.valid = false;
	this.properties = {};

	/**
	 * Initialization method
	 * @param controls: controls used to gather data from
	 */
	this.init = function(controls) {
		for (key in controls) {
			this.ctrls[key] = document.getElementById(controls[key]);
		}
	};

	this.getCtrlValue = function(ctrlId, defaultValue) {
		if(defaultValue == null) { defaultValue = ''; }
		var ret = defaultValue;
		try {
			var value = this.ctrls[ctrlId].value;
			ret = value.replace(/^\s*([\S\s]*?)\s*$/, '$1');
		} catch(e) {}
		if(ret == '') {
			ret = defaultValue;
		}
		return ret
	}

	this.isCtrlChecked = function(ctrlId) {
		var ret = false;
		try {
			ret = this.ctrls[ctrlId].checked != '';
		} catch(e) {}
		return ret;
	}

	/**
	 * Update preview image
	 */
	this.update = function() {
		this.valid = false;
		var T = this;
		this.url = this.getCtrlValue('url_file');
		
		this.imgObject = new Image();
		this.imgObject.onLoad = function() {
			T.ctrls['img_preview'].src = T.url;
			setTimeout(function() {
				if(T.getCtrlValue('img_width') == '') {
					T.ctrls['img_width'].value = T.imgObject.width;
					T.oWidth = T.imgObject.width;
				} else {
					T.oWidth = T.getCtrlValue('img_width');
				}
				if(T.getCtrlValue('img_height') == '') {
					T.ctrls['img_height'].value = T.imgObject.height;
					T.oHeight = T.imgObject.height;
				} else {
					T.oHeight = T.getCtrlValue('img_height');
				}

				T.ctrls['preview'].style.display = 'block';
				T.ctrls['img_proportional'].checked = 'on';
				T.valid = true;
			}, 1000);
		}();
		this.imgObject.src = this.url;
	};


	this.updateTitle = function() {
		this.ctrls['img_preview'].title = this.getCtrlValue('title');
	};

	this.updateBorder = function() {
		var value = this.getCtrlValue('img_border', 0);
		if (value != 'thin' && value != 'medium' && value != 'thick') {
			value += 'px';
		}
		this.ctrls['img_preview'].style.border = value + ' solid black';
	}

	this.updateWidth = function() {
		var w = this.getCtrlValue('img_width');
		if(w != '') {
			this.ctrls['img_preview'].style.width = w + 'px';
			if(this.isCtrlChecked('img_proportional')) {
				var h = Math.floor(parseInt(w) * this.oHeight / this.oWidth);
				this.ctrls['img_preview'].style.height = h + 'px';
				this.ctrls['img_height'].value = h;
			}
		}
	};

	this.updateHeight = function() {
		var h = this.getCtrlValue('img_height');
		if(h != '') {
			this.ctrls['img_preview'].style.height = h + 'px';
			if(this.isCtrlChecked('img_proportional')) {
				var w = Math.floor(parseInt(h) * this.oWidth / this.oHeight);
				this.ctrls['img_preview'].style.width = w + 'px';
				this.ctrls['img_width'].value = w;
			}
		}
	};

	this.updateAlignment = function() {
		var value = this.ctrls['img_alignment'].options[this.ctrls['img_alignment'].selectedIndex].value;
		if(value == 'left' || value == 'right') {
			if(jQuery.support.cssFloat) {
				this.ctrls['img_preview'].style.cssFloat = value;
			} else {
				this.ctrls['img_preview'].style.styleFloat = value;
			}
		} else {
			if(jQuery.support.cssFloat) {
				this.ctrls['img_preview'].style.cssFloat = '';
			} else {
				this.ctrls['img_preview'].style.styleFloat = '';
			}
			this.ctrls['img_preview'].style.verticalAlign = value;
		}
	};

	this.updateHSpace = function() {
		var value = this.getCtrlValue('img_hspace', 0);
		this.ctrls['img_preview'].style.marginLeft = value + 'px';
		this.ctrls['img_preview'].style.marginRight = value + 'px';
	};

	this.updateVSpace = function() {
		var value = this.getCtrlValue('img_vspace', 0);
		this.ctrls['img_preview'].style.marginTop = value + 'px';
		this.ctrls['img_preview'].style.marginBottom = value + 'px';
	};

	this.insert = function() {
		var ed = tinyMCEPopup.editor;
		// Fixes crash in Safari
		if (tinymce.isWebKit) { ed.getWin().focus(); }
		tinyMCEPopup.restoreSelection();

		args = {'src' : this.url, 'style' : ''};
		var title = this.getCtrlValue('title');
		if(title != '') { args['title'] = title; }

		var border = this.getCtrlValue('img_border');
		if(border != '') {
			if (border != 'thin' && border != 'medium' && border != 'thick') {
				border += 'px';
			}
			args['style'] += 'border: ' + border + ' solid black; ';
		}

		var width = this.getCtrlValue('img_width');
		if(width != '') {
			args['style'] += 'width: ' + width + 'px; ';
			args['width'] = width;
		}

		var height = this.getCtrlValue('img_height');
		if(height != '') {
			args['style'] += 'height: ' + height + 'px; ';
			args['height'] = height;
		}

		var hspace = this.getCtrlValue('img_hspace');
		var vspace = this.getCtrlValue('img_vspace');
		margin = hspace != '' ? hspace + 'px ' : '0px ';
		margin += vspace != '' ? vspace + 'px; ' : '0px; ';
		args['style'] += 'margin: ' + margin;

		var alignment = this.ctrls['img_alignment'].options[this.ctrls['img_alignment'].selectedIndex].value;
		if(alignment == 'left' || alignment == 'right') {
			args['style'] += 'float: ' + alignment + '; ';
		} else {
			args['style'] += 'vertical-align: ' + this.properties['alignment'] + '; ';
		}
		var node = ed.selection.getNode();
		if(node && node.nodeName == 'IMG') {
			ed.dom.setAttribs(node, args);
		} else {
			ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : 1});
			ed.dom.setAttribs('__mce_tmp', args);
			ed.dom.setAttrib('__mce_tmp', 'id', '');
			ed.execCommand('mceRepaint');
			ed.undoManager.add();
		}
		tinyMCEPopup.close();
	}

	this.cancel = function() {
		tinyMCEPopup.close();
	}
}

function filter_images(absolute_url, document_url, album_url) {
	var query = $("#query").val();
	location.href=absolute_url+'/select_image?document='+document_url+'&src=album&query='+query+'&album='+album_url;
}
