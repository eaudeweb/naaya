/**
 * Returns a callback closure around nydocument_url.
 */
function getNyFileBrowserCallBack(nydocument_url) {
	function nyFileBrowserCallBack(field_name, url, type, win)
	{
		switch(type) {
			case "file":
				selectNyRelativeLink(field_name, url, win, nydocument_url)
				return true
			case "image":
				selectNyImage(field_name, url, win, nydocument_url)
				return true
		}
		return false
	}

	return nyFileBrowserCallBack
}
