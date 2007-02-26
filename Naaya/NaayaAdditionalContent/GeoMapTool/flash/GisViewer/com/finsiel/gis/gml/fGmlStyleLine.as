import com.finsiel.gis.gml.*;
/* Class: com.finsiel.gis.gml.fGmlStyleLine

   Draw the line using a specified style

*/
class com.finsiel.gis.gml.fGmlStyleLine {
	/* Function: fGmlStyleLine
	
	   Basic constructor
	
	   Returns:
	
	      Nothing.
	
	*/
	private var d_map:MovieClip;
	private var m_minx:Number;
	private var m_miny:Number;
	private var m_maxx:Number;
	private var m_maxy:Number;
	private var _myMB:Object;
	public function fGmlStyleLine(_d_map:MovieClip,myMB:Object) {
		d_map = _d_map;
		_myMB = myMB;
		var my_mapex:Object = d_map.getMapextend();
		m_minx = new Number(my_mapex.minx);
		m_miny = new Number(my_mapex.miny);
		m_maxx = new Number(my_mapex.maxx);
		m_maxy = new Number(my_mapex.maxy);
	}
	function sendmes(mess:Object) {
		_myMB.sendMessage(mess);
	}
	public function style(w_mc:MovieClip, p:Object, st:Object) {
		var thisObj = this;
		var ent_no:Number = Number(w_mc._name.substr(1, 1000000));
		var ldx:Number;
		var ldy:Number;
		w_mc.lineStyle(st.stWidth, st.stColor, st.stAlpha, false, "none", "round", "miter", 1);
		for (var i = 0; i<p.geom.length; i++) {
			var part = p.geom[i];
			var dx:Number = Map2Screen(part[1]).x;
			var dy:Number = Map2Screen(part[1]).y;
			ldx = dx;
			ldy = dy;
			w_mc.moveTo(dx, dy);
			for (var j = 0; j<part.length; j++) {
				var cx:Number = Map2Screen(part[j]).x;
				var cy:Number = Map2Screen(part[j]).y;
				var diffx:Number = Math.abs(cx-ldx);
				var diffy:Number = Math.abs(cy-ldy);
				var delta_d:Number = Math.sqrt(diffx*diffx+diffy*diffy);
				if (delta_d>=1.5) {
					w_mc.lineTo(cx, cy);
					ldx = cx;
					ldy = cy;
				}
			}
		}
		thisObj.sendmes({typ:"gmlLineDrawn", entity:ent_no});
	}
	function Map2Screen(p:Object) {
		
		var d_pix:Number = Math.abs(m_minx-m_maxx)/760;
		var px:Number = (p.x-m_minx)/d_pix;
		var py:Number = 580-(p.y-m_miny)/d_pix;
		
		return {x:px, y:py};
	}
}
