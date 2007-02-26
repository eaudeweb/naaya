//import mx.events.EventDispatc;
import com.finsiel.gis.gml.*;
/* Class: com.finsiel.gis.gml.fGmlDrawLine

   Draw a group of lines into a specific container

   Coordinate transformation will be applied from line coordinates to container coordinates
  
   Functions:

addEventListener - Macromedia FLash event listener
removeEventListener - Macromedia FLash event listener
dispatchEvent - Macromedia FLash event dispatcher

Variables:

Float minx - Container minx
Float miny - Container miny
Float maxx - Container maxx
Float maxy - Container maxy

*/
class com.finsiel.gis.gml.fGmlDrawLine {
	//dispatchers
	public var addEventListener:Function;
	public var removeEventListener:Function;
	public var dispatchEvent:Function;
	private var d_arr:Array;
	private var dr_arr:Array;
	private var d_map:MovieClip;
	private var gml_container:MovieClip;
	private var minx:Number;
	private var miny:Number;
	private var maxx:Number;
	private var maxy:Number;
	private var intervalId:Number;
	private var intervalId_d:Number;
	private var duration:Number = 20;
	private var duration_d:Number = 10;
	private var _myMB;
	private var s_arr:Array;
	private var current_ent:Number;
	/* Function: fGmlDrawLine
	
	   Basic constructor
	
	   Parameters:
	
	  	d_array - array of objects consistind of coordinate pairs
	  	d_container - a map container see <http://www.bliki.com/flashims/>
	myMB - event dispatcher listener
	
	
	   Returns:
	
	      Nothing.
	
	*/
	public function fGmlDrawLine(d_array:Array, d_container:MovieClip, myMB, _s_arr:Array) {
		//mx.events.EventDispatcher.initialize(this);
		d_arr = d_array;
		d_map = d_container;
		s_arr = _s_arr;
		_myMB = myMB;
		current_ent = 0;
	}
	public function check_ready() {
		current_ent = 0;
		gml_container = new MovieClip();
		gml_container = spy();
		beginInterval();
	}
	public function stop_draw() {
		clearInterval(intervalId_d);
	}
	public function begin_draw() {
		var my_mapex:Object = d_map.getMapextend();
		minx = new Number(my_mapex.minx);
		miny = new Number(my_mapex.miny);
		maxx = new Number(my_mapex.maxx);
		maxy = new Number(my_mapex.maxy);
	}
	private function select_draw(i) {
		var draw_inside:Number = 0;
		var e_maxx:Number = d_arr[i].bb.b_maxx;
		var e_maxy:Number = d_arr[i].bb.b_maxy;
		var e_minx:Number = d_arr[i].bb.b_minx;
		var e_miny:Number = d_arr[i].bb.b_miny;
		if (e_minx<=this.maxx && e_maxx>=this.minx && e_miny<=this.maxy && e_maxy>=this.miny) {
			draw_inside = 1;
		}
		if (draw_inside == 1) {
			draw_now(d_arr[i], d_arr[i].id);
		}
	}
	function sendmes(mess:Object) {
		_myMB.sendMessage(mess);
	}
	private function draw_now(p:Object, id:Number) {
		var thisObj = this;
		var cm:MovieClip = new MovieClip();
		cm = gml_container.hook_overlap.createEmptyMovieClip("m"+id, gml_container.hook_overlap.getNextHighestDepth());
		cm.onMouseMove = function() {
			if (_root.ph_mouse.hitTest(cm)) {
				if (cm._parent._parent._name eq thisObj.gml_container._name) {
					thisObj.sendmes({obj:cm._name, typ:"onMouseMove"});
				}
			}
		};
		cm.onMouseDown = function() {
			if (_root.ph_mouse.hitTest(cm)) {
				if (cm._parent._parent._name eq thisObj.gml_container._name) {
					thisObj.sendmes({obj:cm._name, typ:"onMouseDown"});
				}
			}
		};
		cm.onMouseUp = function() {
			if (_root.ph_mouse.hitTest(cm)) {
				if (cm._parent._parent._name eq thisObj.gml_container._name) {
					thisObj.sendmes({obj:cm._name, typ:"onMouseUp"});
				}
			}
		};
		//var fh = new fUtilHover(cm, thisObj._myMB);
		var ds = new fGmlStyleLine(d_map, _myMB);
		ds.style(cm, p, s_arr[id]);
	}
	public function spy():MovieClip {
		var gml_co:MovieClip = new MovieClip();
		var lm:Number = new Number();
		lm = 0;
		var p_name;
		for (var property in d_map) {
			if (typeof d_map[property] == "movieclip") {
				p_name = d_map[property]._name;
				if (p_name.substr(0, 9) eq 'rastermap') {
					var clm:Number = new Number();
					clm = Number(p_name.substr(9, 100));
					if (clm>lm) {
						lm = clm;
					}
				}
			}
		}
		for (var property in d_map) {
			if (typeof d_map[property] == "movieclip") {
				p_name = d_map[property]._name;
				if (p_name eq String("rastermap"+lm)) {
					gml_co = d_map[property];
					break;
				}
			}
		}
		return (gml_co);
	}
	private function beginInterval():Void {
		if (intervalId != null) {
			clearInterval(intervalId);
		}
		intervalId = setInterval(this, "executeCallback", duration);
	}
	public function executeCallback():Void {
		if (gml_container._alpha>=1) {
			clearInterval(intervalId);
			//create container
			gml_container.createEmptyMovieClip("hook_overlap", gml_container.getNextHighestDepth());
			begin_draw();
			beginInterval_d();
		}
	}
	private function beginInterval_d():Void {
		if (intervalId_d != null) {
			clearInterval(intervalId_d);
		}
		intervalId_d = setInterval(this, "executeCallback_d", duration_d);
	}
	public function executeCallback_d():Void {
		if (current_ent<d_arr.length) {
			//trace(current_ent);
			select_draw(current_ent);
			current_ent++;
		} else {
			clearInterval(intervalId_d);
		}
	}
}
