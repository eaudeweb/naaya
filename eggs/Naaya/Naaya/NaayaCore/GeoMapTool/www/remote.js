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
	if (xmlhttp != null)
	{
		xmlhttp.onreadystatechange = handler;
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