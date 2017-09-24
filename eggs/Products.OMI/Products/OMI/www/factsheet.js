	function limitText(limitField, limitNum)
	{
		if (limitField.value.length > limitNum)
		{
			limitField.value = limitField.value.substring(0, limitNum);
		}
	}

	function add_from_input(selectleft, selectright)
	{
		selectleft = document.getElementById(selectleft);
		selectright = document.getElementById(selectright);
		var o = document.createElement( "option");
		o.text = selectleft.value;
		if (o.text != '') {
			o.value = selectleft.value;
			selectright.options[selectright.options.length] = o;
			selectleft.value='';
		}
	}

	function add(selectleft, selectright)
	{
		selectleft = document.getElementById(selectleft);
		selectright = document.getElementById(selectright);
		var i;
		for(i = 0; i < selectleft.options.length; i++)
		{
			if(selectleft.options[i].selected)
			{
				var attribute = selectleft.options[i].getAttribute("parent");
				var o = document.createElement( "option");
				o.text = selectleft.options[i].text;
				o.value = selectleft.options[i].value;
				o.setAttribute("parent", attribute);
				selectright.options[selectright.options.length] = o;
				selectleft.remove(i);
				i=i-1;
			}
		}
	}

	function remove(selectleft, selectright)
	{
		selectleft = document.getElementById(selectleft);
		selectright = document.getElementById(selectright);
		var node = selectright.firstChild;
		while(node)
		{
			if(node.selected)
			{
				var o = document.createElement( "option");
				o.innerHTML = node.firstChild.nodeValue;
				o.value = node.value;
				if(node.getAttribute("parent"))
				{
					var attribute = node.getAttribute("parent");
					o.setAttribute("parent", attribute);
					var node_left = document.getElementById(attribute);
					node_left.appendChild(o);
				}
				else
				{
					selectleft.appendChild(o);
				}
				var node_temp = node;
				node=node.nextSibling;
				selectright.removeChild(node_temp);
			}
			else
			{
				node=node.nextSibling;
			}
		}
	}

	function dosubmit(page)
	{
		if (page == 2)
		{
			var select_lists_right = ["themes_covered", "model_coverage", "model_resolution", "model_time_horizon", "model_time_steps", "dominant_analytical_techniques"];
			for (selectright in select_lists_right)
			{
				selectright = document.getElementById(select_lists_right[selectright]);
				var i;
				for( i = 0; i < selectright.options.length; i++)
				{
					selectright.options[i].selected = true;
				}
			}
		}
	}


	function removePicture(base_url, pic_id) {
		AjaxRequest.get(
			{
				'url' : base_url + '/removePicture',
				'pic_id' : pic_id,
				'onSuccess' : function(req) { 
					var oldImgCtrl = document.getElementById('pic_' + pic_id);
					if(oldImgCtrl != null) {
						oldImgCtrl.parentNode.removeChild(oldImgCtrl);
					}
				},
				'onError' : function() {
					alert('error removing ' + pic_id);
				}
			}
		);
	}