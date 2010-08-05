function setScreenShots() {
	var imgs = document.getElementsByTagName('img');
	var ssSpan = document.createElement('span');
	ssSpan.className = 'ssSpan';
	for (var i=0;i<imgs.length;i++) {
		if (imgs[i].className != 'screenshot') continue;
		var currentSsSpan = ssSpan.cloneNode(true);
		if (imgs[i].alt)
			currentSsSpan.appendChild(document.createTextNode('Screenshot: ' + imgs[i].alt));
		else
			currentSsSpan.appendChild(document.createTextNode('Screenshot without alt text'));
		imgs[i].parentNode.insertBefore(currentSsSpan,imgs[i]);
	}
}