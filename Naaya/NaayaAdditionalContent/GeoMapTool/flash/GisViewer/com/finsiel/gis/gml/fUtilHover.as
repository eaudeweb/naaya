import com.finsiel.gis.gml.*;
class com.finsiel.gis.gml.fUtilHover {
	private var intervalId:Number;
	private var duration:Number = 800;
	private var d_mc:MovieClip;
	private var i_x:Number;
	private var i_y:Number;
	private var myMB;
	private var hovered:String = "0";
	public function fUtilHover(_d_mc:MovieClip, _myMB:Object) {
		d_mc = _d_mc;
		myMB = _myMB;
		//clearInterval(intervalId);
		beginInterval();
	}
	function sendmes(mess:Object) {
		myMB.sendMessage(mess);
	}
	private function beginInterval():Void {
		i_x = 0;
		i_y = 0;
		clearInterval(intervalId);
		intervalId = setInterval(this, "executeCallback", duration);
	}
	public function executeCallback():Void {
		var thisObj = this;
		var dx = d_mc._xmouse-i_x;
		var dy = d_mc._ymouse-i_y;
		i_x = d_mc._xmouse;
		i_y = d_mc._ymouse;
		if (dx == 0 && dy == 0) {
			if (_root.ph_mouse.hitTest(d_mc)) {
				thisObj.sendmes({obj:d_mc._name, typ:"onHover"});
				clearInterval(intervalId);
				
			}
		}
	}
}
