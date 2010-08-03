/**
 * Cookie utils
*/
function createCookie(name, value, days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

/**
 * Check cookies if bespin is enabled
 */
var editors = [];
bespin_enabled = readCookie('bespin');
if (bespin_enabled == null){
    bespin_enabled = true;
    createCookie('bespin', bespin_enabled, 360);
}else{
    if(bespin_enabled == 'true'){
        bespin_enabled = true;
    }else{
        bespin_enabled = false;
    }
}

/**
 * Toogle bespin editor.
 * Enable - Bool
*/
function toggleBespin() {
    if (bespin_enabled){
        createCookie('bespin', false, 360);
        window.location.reload(true)
    }else{
        createCookie('bespin', true, 360);
        window.location.reload(true)
    }
}

function loadBespin(){
    var nodes = document.getElementsByTagName("textarea");
    if (bespin_enabled){
        for (var i=0; i<nodes.length; i++){
            bespin.useBespin(nodes[i]).then(function(env) {
                editors.push(env.editor);
            }, function(error) {
                throw new Error("Launch failed: " + error);
            });
        }
    }
}
window.onload = loadBespin
