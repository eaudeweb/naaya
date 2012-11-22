$(document).ready(function(){
 /**
 * Used for selenium testing in case of ajax
 * Use it in the tests like this:
 *  selenium.wait_for_condition('window.selenium_ready==true', 100)
 */
window.selenium_ready = true;
$.ajaxSetup({
    beforeSend : function(xhr, opts){ 
        window.selenium_ready = false; 
    },
    complete: function(XMLHttpRequest, textStatus){ 
        window.selenium_ready = true; 
    }
});

/**
 * Toggle checkboxes
 *
 * For a element (link, checkbox..) `.toggle-all` given it's `rel` attribute 
 * toggle all checkboxes with `class` = `rel`
 */
$('.toggle-all').live('click', function(e){
    var self = $(this);
    var rel = self.attr("rel");
    var checked = self.hasClass('toggled');
    self.toggleClass('toggled');

    if(this.tagName.toLowerCase() == 'a'){
        e.preventDefault();
    }
    if(checked){
        $("input." + rel).attr('checked', 'checked');
    }else{
        $("input." + rel).removeAttr('checked');
    }
});

//image preview
$("a.preview").click(function(e) {
	e.preventDefault();
});
$("a.preview").hover(function (e) {
	$("body").append("<div id='preview' style='position: absolute; border:1px solid #aaa'>"
					+ "<img src='" + this.href + "'"
					+ " style='max-height: 120px; max-width: 120px' />"
					+ "</div>");
	$("#preview")
		.css("top", (e.pageY - 10) + "px")
		.css("left", (e.pageX + 10) + "px")
		.fadeIn("fast");
},
function () {
	$("#preview").remove();
});
$("a.preview").mousemove(function(e){
	$("#preview")
		.css("top",(e.pageY - 10) + "px")
		.css("left",(e.pageX + 10) + "px");
});

});

/**
 * Replaces all links with rel="external" to target="_blank"
 * This is done to ensure html strict validation
*/
function externalLinks() {
    if (!document.getElementsByTagName) return;
    var anchors = document.getElementsByTagName("a");
    for (var i=0; i<anchors.length; i++) {
        var anchor = anchors[i];
        if (anchor.getAttribute("rel") == "external") {
            anchor.target = "_blank";
            anchor.style.display = "inline";
        }
        else {
            anchor.style.display = "";
        }
    }
}
window.onload = externalLinks;

function gettext(msgid) {
    // Translates javascript strings
    if(typeof(naaya_i18n_catalog) == 'undefined') {
        return msgid;
    }
    var value = naaya_i18n_catalog[msgid];
    if (typeof(value) == 'undefined') {
       return msgid;
    } else {
       return (typeof(value) == 'string') ? value : value[0];
    }
}

function Linkify(inputText) {
    //URLs starting with http://, https://, or ftp://
    var replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    var replacedText = inputText.replace(replacePattern1, '<a class="linkified" href="$1">$1</a>');

    //URLs starting with www. (without // before it, or it'd re-link the ones done above)
    var replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    var replacedText = replacedText.replace(replacePattern2, '$1<a class="linkified" href="http://$2">$2</a>');

    //Change email addresses to mailto:: links
    var replacePattern3 = /(^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9\-\.]+?\.[a-zA-Z]{2,6}$)/gim;
    var replacedText = replacedText.replace(replacePattern3, '<a class="linkified" href="mailto:$1">$1</a>');

    return replacedText
}

/**
*
*  URL decode
*  http://www.webtoolkit.info/
*
* Use jQuery serialize to encode
*
**/
function url_decode(utftext) {
    utftext = unescape(utftext)
    var string = "";
    var i = 0;
    var c = c1 = c2 = 0;
    while ( i < utftext.length ) {
        c = utftext.charCodeAt(i);
        if (c < 128) {
            string += String.fromCharCode(c);
            i++;
        }
        else if((c > 191) && (c < 224)) {
            c2 = utftext.charCodeAt(i+1);
            string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
            i += 2;
        }
        else {
            c2 = utftext.charCodeAt(i+1);
            c3 = utftext.charCodeAt(i+2);
            string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
            i += 3;
        }
    }
    return string;
}

/**
 * Unserialize. Transform uri query into a dictionary
 * TODO: Treat cases for variables such as xxxx[]=2233 or yyy[ddda]=111
*/
function unserialize(data){
    var return_dict = {};
    var rows = data.split('&');
    $.each(rows, function(i, row){
        var key_val = url_decode(row).split('=');
        return_dict[key_val[0]] = key_val[1];
    });
    return return_dict;
}

/**
 * Redirect user to the specfied URL
*/
function redirect(redirect_URL) {
    return window.location = redirect_URL;
}

/**
 * Set and check cookie consent... cookie
*/
$(document).ready(function(){
	checkCookie();

	function setCookie(c_name,value,expires){
	  // set time, it's in milliseconds
	  var today = new Date();
	  today.setTime( today.getTime() );
	  if ( expires ){
		expires = expires * 1000 * 60 * 60 * 24;
	  }
	  var expires_date = new Date( today.getTime() + (expires) );
	  var path = '/';
	  document.cookie=c_name + "=" + escape(value) +
		( ( expires ) ? ";expires=" + expires_date.toGMTString() : "" ) +
		( ( path ) ? ";path=" + path : "" );
	}

	function getCookie(c_name){
	  var i,x,y,ARRcookies=document.cookie.split(";");
	  for (i=0;i<ARRcookies.length;i++){
		x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
		y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
		x=x.replace(/^\s+|\s+$/g,"");
		if (x==c_name){
		  return unescape(y);
		}
	  }
	}

	function checkCookie(){
	  var consent=getCookie("naaya_disclaimer");
	  if (consent==null){
		$('#disclaimer').slideDown(1000);
	  }
	  else{
		if($('#disclaimer:visible')){
		  $('#disclaimer').slideUp(333);
		}
		else{
		  $('#disclaimer').hide();
		}
	  }
	}

	function deleteCookie(name){
	  path = '/'
	  document.cookie = name + "=" +
		( ( path ) ? ";path=" + path : "") +
		";expires=Thu, 01-Jan-1970 00:00:01 GMT";
	}

	$('#acknowledge').click(function(){
	  setCookie("naaya_disclaimer", true, 365);
	  checkCookie();
	});
})
