function ShowHide(theSelect){
	if(theSelect.options[theSelect.options.selectedIndex].value == ''){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'none';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'string_field'){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'block';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'text_field'){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'block';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'email_field'){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'block';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'date_field'){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'block';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'checkbox_field'){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'block';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'selection_field'){
		document.getElementById('div_body_text').style.display = 'none';
		document.getElementById('div_selection_values').style.display = 'block';
		document.getElementById('div_mandatory').style.display = 'block';
	}
	if(theSelect.options[theSelect.options.selectedIndex].value == 'body_text'){
		document.getElementById('div_body_text').style.display = 'block';
		document.getElementById('div_selection_values').style.display = 'none';
		document.getElementById('div_mandatory').style.display = 'none';
	}
}