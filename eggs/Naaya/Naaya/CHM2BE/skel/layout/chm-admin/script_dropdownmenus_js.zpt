<tal:block replace="python:request.RESPONSE.setHeader('content-type', 'text/javascript')"/>

	function getHeadingLink(p_ob){
		//returns the link in the main navigation bar
		var z = p_ob.id.split('_');
		return document.getElementById(Array(z[0], 'a', z[2]).join('_'))
	}
	function getSecondLink(p_ob){
		//returns a link in the dropdown, p_ob can be only the container LI element
		var z = p_ob.id.split('_');
		return document.getElementById(Array(z[0], 'a', z[2], z[3]).join('_'))
	}
	function getLiElement(p_ob){
		//returns the LI element in the first list
		var z = p_ob.id.split('_');
		return document.getElementById(Array(z[0], 'li', z[2]).join('_'))
	}
	function getUlElement(p_ob){
		//returns the second UL element
		var z = p_ob.id.split('_');
		return document.getElementById(Array(z[0], 'ul', z[2]).join('_'))
	}
	function getFirstLink(p_ob){
		//returns the first link in the dropdown
		var z = p_ob.id.split('_');
		return document.getElementById(Array(z[0], 'a', z[2], '0').join('_'))
	}

	function makeVisib(p_ob) {
		var ob = getLiElement(p_ob)
		if(ob){
			ob.visib++;
			if(ob.visib>0) {
				ob.className = 'over'
			} else {
				ob.className = ''
			}
		}
	}

	function takeVisib(p_ob) {
		var ob = getLiElement(p_ob)
		if(ob){
			ob.visib--;
			ob.visib = Math.max(ob.visib, 0)
			if(ob.visib>0) {
				ob.className = 'over'
			} else {
				ob.className = ''
			}
		}
	}

	startList = function() {
		if (document.getElementById) {
			ob = document.getElementById("nav2");
			ob.style.position = 'relative';
			navRoot = document.getElementById("linkgroups");

			for (i=0; i < navRoot.childNodes.length; i++) {
				node = navRoot.childNodes[i];
				if (node.nodeName=="LI") {
					//set the mouseover for IE
					if(document.all && !window.opera){
						node.onmouseover=function() {
							makeVisib(this)
						}
						node.onmouseout=function() {
							takeVisib(this)
						}
					}
					node.visib = 0

					//make the dropdown menu accessible through TAB key
					snode = getHeadingLink(node);
					if (snode) {
						snode.onfocus = function(){
							makeVisib(this)
						}
						snode.onblur  = function(){
							takeVisib(this)
						}
					}
					
					for (j=0; j < node.childNodes.length; j++) {
						node_div = node.childNodes[j];
						if (node_div.nodeName=="DIV") {

							for (k=0; k < node_div.childNodes.length; k++) {
								node_ul = node_div.childNodes[k];
								if (node_ul.nodeName=="UL") {

									for(b=0; b < node_ul.childNodes.length; b++){
										node_li = node_ul.childNodes[b];
										if (node_li.nodeName=="LI") {
											node_a = getSecondLink(node_li)
											node_a.onfocus = function(){
												makeVisib(this)
											}
											node_a.onblur = function(){
												takeVisib(this)
											}
										}
									}

								}
							}
						}
					}
				}
			}
		}
		//execute other potential scripts
		if(window.old_onload) {
			window.old_onload()
		}
	}
	window.old_onload = window.onload
	window.onload=startList;
