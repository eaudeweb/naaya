	function myFileBrowser (field_name, url, type, win) {
		tinyMCE.activeEditor.windowManager.open({
			file: files_page,
			title: 'My File Browser',
			width: 420,
			height: 400,
			resizable: "yes",
			inline: "yes",  // This parameter only has an effect if you use the inlinepopups plugin!
			close_previous: "no"
		}, {
			window: win,
			input: field_name
		});
		return false;
	}
	tinyMCE.init({
				language : "en",
				mode : "textareas",
				theme : "advanced",
				editor_deselector : "mceNoEditor",
				plugins : "safari,spellchecker,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
				theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect,fontsizeselect",
				theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
				theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,|,sub,sup,|,charmap,iespell,advhr,|,ltr,rtl,|,fullscreen,styleprops,cite",
				theme_advanced_toolbar_location : "top",
				theme_advanced_toolbar_align : "left",
				theme_advanced_statusbar_location : "bottom",
				theme_advanced_path_location : "bottom",
				plugin_insertdate_dateFormat : "%Y-%m-%d",
				plugin_insertdate_timeFormat : "%H:%M:%S",
				extended_valid_elements : "hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
				theme_advanced_blockformats : "p,div,h2,h3,h4,h5,h6,blockquote",
				theme_advanced_resize_horizontal : false,
				theme_advanced_resizing : true
				});