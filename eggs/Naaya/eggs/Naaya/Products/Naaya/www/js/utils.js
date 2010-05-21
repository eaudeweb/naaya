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
