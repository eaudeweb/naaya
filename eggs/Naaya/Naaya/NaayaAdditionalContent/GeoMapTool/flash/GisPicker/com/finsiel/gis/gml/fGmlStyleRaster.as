import com.finsiel.gis.gml.*;
/* Class: com.finsiel.gis.gml.fGmlStyleRaster

   Draw the raster

*/
class com.finsiel.gis.gml.fGmlStyleRaster {
	/* Function: fGmlStyleRaster
	
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
	//public var p_style:fGmlStyle
	public function fGmlStyleRaster(_d_map:MovieClip, myMB:Object) {
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
		var r_x:Number;
		var r_y:Number;
		r_x = p.resolution.resx;
		r_y = p.resolution.resy;
		var minx_sc:Number;
		var miny_sc:Number;
		var maxx_sc:Number;
		var maxy_sc:Number;
		minx_sc = Map2Screen({x:p.bb.b_minx, y:p.bb.b_miny}).x;
		miny_sc = Map2Screen({x:p.bb.b_minx, y:p.bb.b_miny}).y;
		maxx_sc = Map2Screen({x:p.bb.b_maxx, y:p.bb.b_maxy}).x;
		maxy_sc = Map2Screen({x:p.bb.b_maxx, y:p.bb.b_maxy}).y;
		var sx = Math.abs(minx_sc-maxx_sc)*100/p.resolution.resx;
		var sy = Math.abs(miny_sc-maxy_sc)*100/p.resolution.resy;
		var mclListener:Object = new Object();
		mclListener.onLoadStart = function(target_mc:MovieClip) {
			thisObj.sendmes({typ:"gmlRasterStartLoading", entity:ent_no});
		};
		mclListener.onLoadComplete = function(target_mc:MovieClip) {
			w_mc._x = minx_sc;
			w_mc._y = maxy_sc;
			w_mc._xscale = sx;
			w_mc._yscale = sy;
			w_mc._alpha = st.stAlpha;
			thisObj.sendmes({typ:"gmlRasterLoaded", entity:ent_no});
		};
		mclListener.onLoadProgress = function(target_mc:MovieClip, bytesLoaded:Number, bytesTotal:Number) {
			var pr:Number = Math.round(bytesLoaded/bytesTotal*100);
			thisObj.sendmes({typ:"gmlonLoadProgress", val:pr, entity:ent_no});
		};
		var image_mcl:MovieClipLoader = new MovieClipLoader();
		image_mcl.addListener(mclListener);
		image_mcl.loadClip(p.raster, w_mc);
	}
	function Map2Screen(p:Object) {
		var d_pix:Number = Math.abs(m_minx-m_maxx)/760;
		var px:Number = (p.x-m_minx)/d_pix;
		var py:Number = 580-(p.y-m_miny)/d_pix;
		return {x:px, y:py};
	}
}
