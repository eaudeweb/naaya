function nyUrlConverterCallBack(url, node, on_save) {
	if (node != null && node.baseURI != null) {
		// tinyMCE seems to have problems with URLs that have anchors
		// so we'll use this workaround
		if (url.substring(0, node.baseURI.length + 1) == (node.baseURI + "#"))
		{
			return url.substring(node.baseURI.length);
		}
		if (url.substring(0, node.baseURI.length + 2) == (node.baseURI + "/#"))
		{
			return url.substring(node.baseURI.length + 1);
		}
	}
	// use the default tinyMCE conversion function
	var new_url = TinyMCE.prototype.convertURL(url, node, on_save);
	return new_url;
}
