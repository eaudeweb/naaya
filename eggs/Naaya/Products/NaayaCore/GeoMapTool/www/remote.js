var xmlhttp;

function trim(str)
{
	var ret;
	if(typeof(str) != "string") str = str + "";
	return str.replace(/(^\s+)|(\s+$)/gi, ""); 
}

function initXMLdoc() {
	xmlhttp = null;
	if (window.XMLHttpRequest) {
		xmlhttp=new XMLHttpRequest()
	}
	else if (window.ActiveXObject) {
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
}

function loadXMLDoc(url, handler) {
	initXMLdoc();
	function wrapper()
	{
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
				handler();
				return true;
			} else {
				alert('Naaya GeoMapTool: there was a problem retrieving the XML data:\n' + xmlhttp.statusText);
				return false;
			}
		}
	}
	if (xmlhttp != null)
	{
		xmlhttp.onreadystatechange = wrapper;
		xmlhttp.open("GET", url, true);
		xmlhttp.send(null);
	}
}

function processRequest() {
	if (xmlhttp.readyState == 4) {
		if (xmlhttp.status == 200) {
			// process data here...
			return true;
		} else {
			alert('There was a problem retrieving the XML data:\n' + xmlhttp.statusText);
			return false;
		}
	}
}



/*
 * The following function is based on the YUI Library.
 * Copyright (c) 2008, Yahoo! Inc. All rights reserved.
 * Code licensed under the BSD License:
 * http://developer.yahoo.net/yui/license.txt
 * version: 2.5.1
 */

/**
* @description This method assembles the form label and value pairs and
* constructs an encoded string.
* asyncRequest() will automatically initialize the transaction with a
* a HTTP header Content-Type of application/x-www-form-urlencoded.
* @method setForm
* @public
* @static
* @param {string || object} form id or name attribute, or form object.
* @return {string} string of the HTML form field name and value pairs..
*/
function encodeForm(formId)
{
	var oForm;
	var sFormData = '';
	if(typeof formId == 'string'){
		// Determine if the argument is a form id or a form name.
		// Note form name usage is deprecated, but supported
		// here for backward compatibility.
		oForm = (document.getElementById(formId) || document.forms[formId]);
	}
	else if(typeof formId == 'object'){
		// Treat argument as an HTML form object.
		oForm = formId;
	}
	else{
		return;
	}

	var oElement, oName, oValue, oDisabled;
	var hasSubmit = false;

	// Iterate over the form elements collection to construct the
	// label-value pairs.
	for (var i=0; i<oForm.elements.length; i++){
		oElement = oForm.elements[i];
		oDisabled = oElement.disabled;
		oName = oElement.name;
		oValue = oElement.value;

		// Do not submit fields that are disabled or
		// do not have a name attribute value.
		if(!oDisabled && oName)
		{
			switch(oElement.type)
			{
				case 'select-one':
				case 'select-multiple':
					for(var j=0; j<oElement.options.length; j++){
						if(oElement.options[j].selected){
							if(window.ActiveXObject){
								sFormData += encodeURIComponent(oName) + '=' + encodeURIComponent(oElement.options[j].attributes['value'].specified?oElement.options[j].value:oElement.options[j].text) + '&';
							}
							else{
								sFormData += encodeURIComponent(oName) + '=' + encodeURIComponent(oElement.options[j].hasAttribute('value')?oElement.options[j].value:oElement.options[j].text) + '&';
							}
						}
					}
					break;
				case 'radio':
				case 'checkbox':
					if(oElement.checked){
						sFormData += encodeURIComponent(oName) + '=' + encodeURIComponent(oValue) + '&';
					}
					break;
				case 'file':
					// stub case as XMLHttpRequest will only send the file path as a string.
				case undefined:
					// stub case for fieldset element which returns undefined.
				case 'reset':
					// stub case for input type reset button.
				case 'button':
					// stub case for input type button elements.
					break;
				case 'submit':
					// stub case for submit type button elements.
					break;
				default:
					sFormData += encodeURIComponent(oName) + '=' + encodeURIComponent(oValue) + '&';
			}
		}
	}

	sFormData = sFormData.substr(0, sFormData.length - 1);

	return sFormData;
}
