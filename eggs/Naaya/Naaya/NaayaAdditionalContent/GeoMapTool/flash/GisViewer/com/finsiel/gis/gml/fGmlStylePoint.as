import com.finsiel.gis.gml.*;
/* Class: com.finsiel.gis.gml.fGmlStylePoint

   Draw the point using a specified style

*/
class com.finsiel.gis.gml.fGmlStylePoint {
	/* Function: fGmlStylePoint
	
	   Basic constructor
	
	   Returns:
	
	      Nothing.
	
	*/
	private var d_map:MovieClip;
	private var _myMB:Object;
	//public var p_style:fGmlStyle
	public function fGmlStylePoint(_d_map:MovieClip, myMB) {
		d_map = _d_map;
		_myMB = myMB;
	}
	function sendmes(mess:Object) {
		_myMB.sendMessage(mess);
	}
	public function style(w_mc:MovieClip, p:Object, st:Object) {
		var thisObj = this;
		var ent_no:Number = Number(w_mc._name.substr(1, 1000000));
		thisObj.sendmes({typ:"gmlPointDrawn", entity:ent_no});
		trace("draw" )
		trace (st.stHref)
		var d_w:Number = st.stWidth/2;
		var d_h:Number = st.stHeight/2;
		var angleDelta = Math.PI/4;
		var angleMedio = angleDelta/2;
		var xCtrlDist = d_w/Math.cos(angleMedio);
		var yCtrlDist = d_h/Math.cos(angleMedio);
		var dx:Number = d_map.mapPointToScreenPoint(p).x;
		var dy:Number = d_map.mapPointToScreenPoint(p).y;
		switch (st.stShape) {
		case "rectangle" :
			w_mc.lineStyle(st.stOutlineWidth, st.stOutlineColor, st.stAlpha, true, "none", "round", "miter", 1);
			w_mc.beginFill(st.stColor, st.stAlpha);
			w_mc.moveTo(dx-d_w, dy-d_h);
			w_mc.lineTo(dx+d_w, dy-d_h);
			w_mc.lineTo(dx+d_w, dy+d_h);
			w_mc.lineTo(dx-d_w, dy+d_h);
			w_mc.lineTo(dx-d_w, dy-d_h);
			w_mc.endFill();
			
			var ic:MovieClip = new MovieClip();
			ic = w_mc.createEmptyMovieClip("icon_holder", w_mc.getNextHighestDepth());

			
			
			
			
			ic.lineStyle(st.stOutlineWidth, st.stOutlineColor, st.stAlpha, true, "none", "round", "miter", 1);
			ic.beginFill(st.stColor, st.stAlpha);
			ic.moveTo(dx-d_w, dy-d_h);
			ic.lineTo(dx+d_w, dy-d_h);
			ic.lineTo(dx+d_w, dy+d_h);
			ic.lineTo(dx-d_w, dy+d_h);
			ic.lineTo(dx-d_w, dy-d_h);
			ic.endFill();
			
			
			
			ic.loadMovie(st.stHref)
			ic._width =st.stWidth 
			ic._height=st.stHeight
			ic._x =d_map.mapPointToScreenPoint(p).x-st.stWidth/2
			ic._y =d_map.mapPointToScreenPoint(p).y-st.stHeight/2
			
			//w_mc.lineStyle(st.stOutlineWidth, st.stOutlineColor, 60, true, "none", "round", "miter", 1);
			//w_mc.beginFill(st.stColor, st.stAlpha);
			//w_mc.moveTo(dx-d_w, dy-d_h);
			//w_mc.lineTo(dx+d_w, dy-d_h);
			//w_mc.lineTo(dx+d_w, dy+d_h);
			//w_mc.lineTo(dx-d_w, dy+d_h);
			//w_mc.lineTo(dx-d_w, dy-d_h);
			//w_mc.endFill();
			
			break;
		case "cross" :
			w_mc.lineStyle(st.stOutlineWidth, st.stOutlineColor, st.stAlpha, true, "none", "round", "miter", 1);
			//w_mc.beginFill(st.stColor, st.stAlpha);
			w_mc.moveTo(dx, dy+d_h);
			w_mc.lineTo(dx, dy-d_h);
			w_mc.moveTo(dx+d_w, dy);
			w_mc.lineTo(dx-d_w, dy);
			break;
		case "triangle" :
			w_mc.lineStyle(st.stOutlineWidth, st.stOutlineColor, st.stAlpha, true, "none", "round", "miter", 1);
			w_mc.beginFill(st.stColor, st.stAlpha);
			w_mc.moveTo(dx-d_w, dy+d_h);
			w_mc.lineTo(dx+d_w, dy+d_h);
			w_mc.lineTo(dx, dy-d_h);
			w_mc.lineTo(dx-d_w, dy+d_h);
			w_mc.endFill();
			break;
		case "circle" :
			w_mc.lineStyle(st.stOutlineWidth, st.stOutlineColor, st.stAlpha, true, "none", "round", "miter", 1);
			w_mc.beginFill(st.stColor, st.stAlpha);
			var rx, ry, ax, ay;
			var angle = 0;
			w_mc.moveTo(dx+d_w, dy);
			for (var i = 0; i<8; i++) {
				angle += Math.PI/4;
				rx = dx+Math.cos(angle-angleMedio)*(xCtrlDist);
				ry = dy+Math.sin(angle-angleMedio)*(yCtrlDist);
				ax = dx+Math.cos(angle)*d_w;
				ay = dy+Math.sin(angle)*d_h;
				w_mc.curveTo(rx, ry, ax, ay);
			}
			break;
		}
	}
}
