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
    var replacedText = inputText.replace(replacePattern1, '<a href="$1">$1</a>');

    //URLs starting with www. (without // before it, or it'd re-link the ones done above)
    var replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    var replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2">$2</a>');

    //Change email addresses to mailto:: links
    var replacePattern3 = /(^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9\-\.]+?\.[a-zA-Z]{2,6}$)/gim;
    var replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

    return replacedText
}
