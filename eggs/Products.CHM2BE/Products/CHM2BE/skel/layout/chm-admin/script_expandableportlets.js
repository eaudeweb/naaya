<tal:block replace="python:request.RESPONSE.setHeader('content-type', 'text/javascript')"/>
<tal:block condition="python:False">
	/*Expandable portlets*/
</tal:block>


var ep_co_portlet_count = 0;
var ep_collapsed_portlets = new Array();

var ep_ex_portlet_count = 0;
var ep_expanded_portlets = new Array();

var EP_COLLAPSED = -1;
var EP_COLLAPSED_IGNOREPATH = -2;
var EP_EXPANDED = 1;
var EP_EXPANDED_IGNOREPATH = 2;

var em_img_expand = new Image()
em_img_expand.src = ep_expand_path

var em_img_collapse = new Image()
em_img_collapse.src = ep_collapse_path

if(window.onload) {
	document.ep_old_onload = window.onload
}
window.onload = ep_init

function ep_init() {
	var i;
	for(i in ep_collapsed_portlets) {
		ep_f_collapsePortlet(ep_collapsed_portlets[i])
	}
	for(i in ep_expanded_portlets) {
		ep_f_setImage(ep_expanded_portlets[i])
	}
	if(document.ep_old_onload)
		document.ep_old_onload()
}

function cookieCreate(p_name,p_value,p_days) {
	if (p_days) {
		var l_date = new Date();
		l_date.setTime(l_date.getTime()+(p_days*86400000));
		var l_expires = "; expires="+l_date.toGMTString();
	} else {
		var l_expires = "";
	}
	document.cookie = p_name+"="+p_value+l_expires+"; path=/";
}


function cookieRead(p_name) {
	var i;
	var l_name = p_name + "=";
	var ca = document.cookie.split(';');
	for(var i=0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(l_name) == 0) return c.substring(l_name.length,c.length);
	}
	return null;
}


function cookieErase(p_name) {
	cookieCreate(p_name,"",-1);
}

function getExpandableElement(p_ob) {
	<tal:block condition="python:False">
	/*
		For this CHM skin return the second DIV element in the second ancestor.
	*/
	</tal:block>
	var i, l_count=0;
	var l_temp = p_ob.parentNode.parentNode.childNodes;
	for(i in l_temp) {
		if(l_temp[i].tagName == 'DIV') {
			l_count ++;
			if(l_count == 2)
				return l_temp[i]
		}
	}
}

function ep_f_collapsePortlet(p_id, p_status) {
	if(!p_status)
		p_status = EP_COLLAPSED
	var ob = document.getElementById(p_id)
	if(ob) {
		ep_f_setImage(p_id, true)
		ob.ep_expanded = p_status
		getExpandableElement(ob).old_style_display = getExpandableElement(ob).style.display
		getExpandableElement(ob).style.display = 'none'
	}
}

function ep_f_expandPortlet(p_id, p_status) {
	if(!p_status)
		p_status = EP_EXPANDED
	var ob = document.getElementById(p_id)
	if(ob) {
		ep_f_setImage(p_id, false)
		ob.ep_expanded = p_status
		getExpandableElement(ob).style.display = getExpandableElement(ob).old_style_display
	}
}

function ep_f_setImage(p_id, p_expand) {
	var ob = document.getElementById(p_id)
	if(ob) {
		if(p_expand) {
			ob.src = em_img_expand.src;
			ob.alt = 'Expand'
			ob.title = 'Expand'
		} else {
			ob.src = em_img_collapse.src;
			ob.alt = 'Collapse'
			ob.title = 'Collapse'
		}
	}
}

function ep_f_expandOrCollapse(p_id, ignorepath) {
	var ob = document.getElementById(p_id)
	if(ob) {
		if(ignorepath) {
			t_status = EP_EXPANDED;
		} else {
			t_status = EP_EXPANDED_IGNOREPATH;
		}
		if(!ob.ep_expanded)ob.ep_expanded = t_status;
		if(ob.ep_expanded == EP_EXPANDED || ob.ep_expanded == EP_EXPANDED_IGNOREPATH) {
			if(ignorepath){
				ep_f_collapsePortlet(ob.id, EP_COLLAPSED_IGNOREPATH)
			} else {
				ep_f_collapsePortlet(ob.id)
			}
		} else {
			if(ignorepath) {
				ep_f_expandPortlet(ob.id, EP_EXPANDED_IGNOREPATH)
			} else {
				ep_f_expandPortlet(ob.id)
			}
		}
		var old_cookie = cookieRead('ep_expanded_portlets');
		var new_cookie='';
		var add_cookie = ep_path + '|' + p_id + '|' + ob.ep_expanded;


		if (!old_cookie)
		{
			new_cookie = add_cookie;
		}
		else
		{
			new_cookie = ep_f_computeCookie(old_cookie, add_cookie);
		}

		cookieCreate('ep_expanded_portlets', new_cookie, 10);
	}
}

function ep_f_computeCookie(p_old_cookie, p_add_cookie) {
	var i,b;
	var l_cookies = p_old_cookie.split('*');
	var l_add_details = p_add_cookie.split('|');
	var l_details;
	for(i in l_cookies) {
		l_details = l_cookies[i].split('|');
		if(l_details[1]==l_add_details[1]) {
			l_cookies[i] = p_add_cookie;
			return l_cookies.join('*')
		}
	}
	return p_old_cookie + '*' + p_add_cookie;
}
