// 1.6.3
if (ie6w.jstest == 'true' && ie6w.test == 'true') { alert('IE6W:Begin'); }

function convertehtml(str) {
	return str.replace(/&quot;/g,'"').replace(/&amp;/g,"&").replace(/&lt;/g,"<").replace(/&gt;/g,">");
}

var Client = {
	Engine: {'name': 'unknown', 'version': ''},	
	Features: {}
};

Client.Features.xhr = !!(window.XMLHttpRequest);
Client.Features.xpath = !!(document.evaluate);
if (window.opera) {
	Client.Engine.name = 'opera';
}else if (window.ActiveXObject) {
	Client.Engine = {'name': 'ie', 'version': (Client.Features.xhr) ? 7 : 6};
}else if (!navigator.taintEnabled) {
	Client.Engine = {'name': 'webkit', 'version': (Client.Features.xpath) ? 420 : 419};
}else if (document.getBoxObjectFor != null) {
	Client.Engine.name = 'gecko';
}

Client.Engine[Client.Engine.name] = Client.Engine[Client.Engine.name + Client.Engine.version] = true;

jQuery(document).ready(function() {
	if ((jQuery.browser.msie && jQuery.browser.version<=6 && (Client.Engine.ie && !Client.Engine.ie7)) || (ie6w.test == 'true')) {
		jQuery('body').prepend('<div id="ie6w_div"><div id="ie6w_icon"><img src="' + ie6w.url + '/images/warning-32.png" width="30" height="28" /></div><div id="ie6w_text"><strong><font color=RED>' + convertehtml(ie6w.t1) + '</font></strong>: ' + convertehtml(ie6w.t2) + '</div><div id="ie6w_browsers"></div></div>');
		jQuery('#ie6w_div').css({
			"overflow": "hidden",
			"z-index": "1500",
			"left": "0px",
			"top": "0px",
			"height": "34px",
			"width": "100%",
			"background-color": "#FFFF00",
			"font-family": "Verdana, Arial, Helvetica, sans-serif",
			"font-size": "11px",
			"color": "#000000",
			"clear": "both",
			"border-bottom-width": "1px",
			"border-bottom-style": "solid",
			"border-bottom-color": "#000000"
		}).width(jQuery(window).width());
		jQuery('#ie6w_div #ie6w_icon').css({
			"overflow": "hidden",
			"position": "absolute",
			"left": "0px",
			"top": "0px",
			"height": "28px",
			"width": "30px",
			"padding": "3px"
		});
		var ie6w_b = 0;
		if(ie6w.ie=='true') {
			ie6w_b++;
			jQuery('#ie6w_div #ie6w_browsers').prepend('<a href="' + ie6w.ieu + '" target="_blank"><img src="' + ie6w.url + '/img/ie.gif" alt="get IE7!" width="28" height="28" border="0" /></a>');
		}
		if(ie6w.safari=='true') {
			ie6w_b++;
			jQuery('#ie6w_div #ie6w_browsers').prepend('<a href="' + ie6w.safariu + '" target="_blank"><img src="' + ie6w.url + '/img/safari.gif" alt="get Safari!" width="28" height="28" border="0" /></a>');
		}
		if(ie6w.chrome=='true') {
			ie6w_b++;
			jQuery('#ie6w_div #ie6w_browsers').prepend('<a href="' + ie6w.chromeu + '" target="_blank"><img src="' + ie6w.url + '/img/chrome.gif" alt="get Chrome!" width="28" height="28" border="0" /></a>');
		}
		if(ie6w.opera=='true') {
			ie6w_b++;
			jQuery('#ie6w_div #ie6w_browsers').prepend('<a href="' + ie6w.operau + '" target="_blank"><img src="' + ie6w.url + '/img/opera.gif" alt="get Opera!" width="28" height="28" border="0" /></a>');
		}
		if(ie6w.firefox=='true') {
			ie6w_b++;
			jQuery('#ie6w_div #ie6w_browsers').prepend('<a href="' + ie6w.firefoxu + '" target="_blank"><img src="' + ie6w.url + '/img/firefox.gif" alt="get Firefox!" width="28" height="28" border="0" /></a>');
		}
		jQuery('#ie6w_div #ie6w_browsers').css({
			"overflow": "hidden",
			"position": "absolute",
			"right": "0px",
			"top": "0px",
			"height": "28px",
			"width": "146px",

			"padding": "3px"
		}).width((ie6w_b *28)+12);
		jQuery('#ie6w_div #ie6w_text').css({
			"overflow": "hidden",
			"position": "absolute",
			"left": "36px",
			"top": "0px",
			"height": "28px",
			"width": "650px",
			"padding": "3px",
			"text-align": "left"
		}).width(jQuery(window).width() - jQuery('#ie6w_div #ie6w_icon').outerWidth() - jQuery('#ie6w_div #ie6w_browsers').outerWidth() - 6);
	}
});

if (ie6w.jstest == 'true' && ie6w.test == 'true') {
	alert('IE6W:End');
}