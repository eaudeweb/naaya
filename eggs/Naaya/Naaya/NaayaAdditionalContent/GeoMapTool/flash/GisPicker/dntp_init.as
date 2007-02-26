import com.finsiel.gis.gml.*;
import com.xfactorstudio.xml.xpath.*;
import com.luxagraf.public_classes.*;
//
//_global.style.setStyle("themeColor", 0xEFEBEF);
//_global.style.setStyle("fontFamily", "Verdana");
//_global.style.setStyle("fontSize", 10);
//
//var ext_gmldata = "http://ew-demo.finsiel.ro/portal_map/geomap_gml";
//var ext_bbdata = "http://ew-demo.finsiel.ro/portal_map/misc_/EWGeoMap/bounding.xml";
//var ext_stdata = "http://ew-demo.finsiel.ro/portal_map/symbols_xml";
//var ext_back = "gml_test_dtm";
//var ext_server = "geonode-test.eea.eu.int";
//var ext_bbloc = "EU";
//ask for flashvars
var vvars:String = vars;
var mouseover:Number = 0;
var ext_gmldata:String = vvars.split(';')[0];
var ext_bbdata:String = vvars.split(';')[1];
var ext_stdata:String = vvars.split(';')[2];
var ext_back:String = vvars.split(';')[3];
var ext_server:String = vvars.split(';')[4];
var ext_bbloc:String = vvars.split(';')[5];
conn.serverName = ext_server;
conn.serviceName = ext_back;
//variables
var my_hint:LuxToolTip = new LuxToolTip(_root, 1.000, "Verdana", 10, 0x000000);
var my_geo_hint:LuxToolTip = new LuxToolTip(_root, 1.000, "Verdana", 10, 0x000000);
myMB = new fUtilMessageBroadcaster(myMB);
var gmldata:fGmlPrepare = new fGmlPrepare(myMB);
var dp:fGmlDrawPoint = new fGmlDrawPoint();
var dl:fGmlDrawLine = new fGmlDrawLine();
var dz:fGmlDrawPoly = new fGmlDrawPoly();
var dr:fGmlDrawRaster = new fGmlDrawRaster();
var gencoo:fUtilCooConv = new fUtilCooConv();
var gencooS:fUtilCooConvS = new fUtilCooConvS();
var st_arr:Array = new Array();
gmldata.gmlPath = ext_gmldata;
var cur_ent:String;
//coordinates display
var coo_d:String = "dms";
// instantiate a MessageBroadcaster:
// define an object to listen to myMB:
//loading bounding box
var i_minx:Number;
var i_miny:Number;
var i_maxx:Number;
var i_maxy:Number;
_bbXML = new XML();
_bbXML.ignoreWhite = true;
_bbXML.onLoad = function(success:Boolean) {
	if (success) {
		gmldata.gmlRead();
	} else {
		//var eventObject:Object = {target:this, type:'done', mes:'gmlFailed', ext_mes:'ext_gmlFailed'};
		//thisObj.dispatchEvent(eventObject);
	}
};
_bbXML.load(ext_bbdata);
//end bb
//styles
_stXML = new XML();
_stXML.ignoreWhite = true;
_stXML.onLoad = function(success:Boolean) {
	if (success) {
		trace("style xmlx loaded");
		trace(_stXML);
		//		gmldata.gmlRead();
	} else {
		//var eventObject:Object = {target:this, type:'done', mes:'gmlFailed', ext_mes:'ext_gmlFailed'};
		//thisObj.dispatchEvent(eventObject);
	}
};
_stXML.load(ext_stdata);
//end styles
myObj = {};
myObj.message = function(p_eventObj) {
	var ent_id:Number = Number(p_eventObj.msgobj.obj.substr(1, 1000));
	//trace(p_eventObj.msgobj.typ);
	switch (p_eventObj.msgobj.typ) {
	case "onMouseDown" :
		break;
	case "onMouseMove" :
		break;
	case "gmlElementLoaded" :
		sb5_txt.text = "Processing GML object: "+p_eventObj.msgobj.obj;
		break;
	case "gmlRequesting" :
		sb5_txt.text = "Request GML file...";
		break;
	case "gmlRasterStartLoading" :
		sb5_txt.text = "Start loading tile "+p_eventObj.msgobj.entity+"...";
		break;
	case "gmlRasterLoaded" :
		sb5_txt.text = "Raster tile "+p_eventObj.msgobj.entity+" loaded.";
		break;
	case "gmlonLoadProgress" :
		sb5_txt.text = "Loading tile "+p_eventObj.msgobj.entity+", "+p_eventObj.msgobj.val+" % done.";
		break;
	case "gmlPolygonDrawn" :
		sb5_txt.text = "GML polygon "+p_eventObj.msgobj.entity+" drawn.";
		break;
	case "gmlLineDrawn" :
		sb5_txt.text = "GML line "+p_eventObj.msgobj.entity+" drawn.";
		break;
	case "gmlPointDrawn" :
		sb5_txt.text = "GML point "+p_eventObj.msgobj.entity+" drawn.";
		break;
	}
};
myMB.addEventListener("message", myObj);
var myListnerObj:Object = new Object();
myListnerObj.done = function(evtObj) {
	//trace(evtObj.mes)
	switch (evtObj.mes) {
	case "gmlLoaded" :
		trace("gmlLoaded");
		//
		sb5_txt.text = "Extract metadata...";
		sb5_txt.text = "GML ready.";
		if (ext_bbloc == "GML") {
			i_minx = Number(gmldata.gmlBB.BB_minx);
			i_miny = Number(gmldata.gmlBB.BB_miny);
			i_maxx = Number(gmldata.gmlBB.BB_maxx);
			i_maxy = Number(gmldata.gmlBB.BB_maxy);
		} else {
			var selXML:XML = new XML(XPath.selectNodes(_bbXML, "/countries/country[code='"+ext_bbloc+"']")[0]);
			selXML.ignoreWhite = true;
			i_minx = Number(XPath.selectNodes(selXML, "/country/minx/text()")[0]);
			i_miny = Number(XPath.selectNodes(selXML, "/country/miny/text()")[0]);
			i_maxx = Number(XPath.selectNodes(selXML, "/country/maxx/text()")[0]);
			i_maxy = Number(XPath.selectNodes(selXML, "/country/maxy/text()")[0]);
		}
		b_map.processImage({minx:i_minx, miny:i_miny, maxx:i_maxx, maxy:i_maxy});
		create_style(gmldata.gmlType);
		if (gmldata.gmlType == "point") {
			p_draw();
		}
		break;
	case 'percent_loaded' :
		sb5_txt.text = "Loading GML, "+evtObj.ext_mes+"% done.";
		break;
	case "gmlRequesting" :
		trace("loading");
		break;
	case "gmlFailed" :
		trace("failed");
		break;
	}
};
_root.onMouseMove = function() {
	ph_mouse._x = _root._xmouse;
	ph_mouse._y = _root._ymouse;
	//coordinates display
	if (mouseover == 1) {
		var cur_x:Number = b_map.elastic._xmouse;
		var cur_y:Number = b_map.elastic._ymouse;
		if (cur_x<=0) {
			cur_x = 0;
		}
		if (cur_x>=b_map._width) {
			cur_x = b_map._width;
		}
		if (cur_y<=0) {
			cur_y = 0;
		}
		if (cur_y>=b_map._height) {
			cur_y = b_map._height;
		}
		var screen_Point:Object = b_map.screenPointToMapPoint({x:cur_x, y:cur_y});
		switch (coo_d) {
		case "dms" :
			var c_result:Object = new Object();
			c_result = gencoo.convert(screen_Point.x, screen_Point.y, "DMS", "GEOG", 2);
			sb5_txt.text = c_result.lat+", "+c_result.lon;
			break;
		case "m" :
			sb5_txt.text = "X:"+(Math.ceil(screen_Point.x*1000))/1000+", Y:"+(Math.ceil(screen_Point.y*1000))/1000;
			break;
		case "dd" :
			var c_result:Object = new Object();
			c_result = gencoo.convert(screen_Point.x, screen_Point.y, "DD", "GEOG", 2);
			sb5_txt.text = c_result.lat+", "+c_result.lon;
			break;
		}
	}
};
myListnerObj.loaded = function(evtObj) {
	sb1_txt.text = evtObj.mes;
};
gmldata.addEventListener("done", myListnerObj);
gmldata.addEventListener("loaded", myListnerObj);
//gmldata.gmlRead();
function create_style(dataType:String) {
	//define a style array
	for (var k:Number = 0; k<=gmldata.gmlGeomDataArray.length; k++) {
		var ls:fGmlStyle = new fGmlStyle();
		//ls.stShape = "triangle";
		//ls.stShape = "circle";
		//ls.stShape = "cross";
		//switch 
		ls.stShape = "rectangle";
		ls.stWidth = 16;
		ls.stHeight = 16;
		//ls.stColor = Math.round(Math.random()*0xFFFFFF);
		ls.stOutlineStyle = 2;
		ls.stOutlineWidth = 2;
		ls.stAlpha = 0;
		switch (dataType) {
		case "line" :
			ls.stColor = 0xFF0000;
			break;
		case "poly" :
			ls.stColor = 0xEAEAAE;
			ls.stOutlineColor = 0xFF0000;
			break;
		case "point" :
			ls.stColor = 0xEAEAAE;
			ls.stOutlineColor = 0xFF0000;
			break;
		}
		var symbol_id:Number = gmldata.gmlObjDataArray[k].symbol_id;
		var symHref:String = XPath.selectNodes(_stXML, "/symbols/symbol[id="+symbol_id+"]/picture/text()")[0];
		ls.stHref = symHref;
		st_arr[gmldata.gmlGeomDataArray[k].id] = ls;
	}
}
function p_draw() {
	dp = new fGmlDrawPoint(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
function l_draw() {
	dl = new fGmlDrawLine(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
function y_draw() {
	dy = new fGmlDrawPoly(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
function r_draw() {
	dr = new fGmlDrawRaster(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
b_map.onRollOver = function() {
	mouseover = 1;
};
b_map.onRollOut = function() {
	mouseover = 0;
};
b_map.onBeforeChange = function() {
	det_mc._visible = false;
	if (gmldata.gmlType == "point") {
		dp.stop_draw();
	}
	if (gmldata.gmlType == "line") {
		dl.stop_draw();
	}
	if (gmldata.gmlType == "poly") {
		dy.stop_draw();
	}
	if (gmldata.gmlType == "raster") {
		dr.stop_draw();
	}
};
b_map.onDone = function() {
	if (gmldata.gmlType == "point") {
		dp.check_ready();
	}
	if (gmldata.gmlType == "line") {
		dl.check_ready();
	}
	if (gmldata.gmlType == "poly") {
		dy.check_ready();
	}
	if (gmldata.gmlType == "raster") {
		dr.check_ready();
	}
};
clr_p_btn.onRelease = function() {
	_root.b_map.interaction = "none";
};
b_zi.onRelease = function() {
	b_map.interaction = "zoomin";
};
b_zo.onRelease = function() {
	b_map.interaction = "zoomout";
};
b_pan.onRelease = function() {
	b_map.interaction = "pan";
};
b_pin.onRelease = function() {
	b_map.interaction = "none";
};
b_za.onRelease = function() {
	b_map.processImage({minx:i_minx, miny:i_miny, maxx:i_maxx, maxy:i_maxy});
};
b_map.onStatus = function(status:Boolean, funcname:String, percdone:Number, msg:String) {
	if (funcname == "server_not_found" & percdone == 0) {
		_sb5_txt.text = "Server down, swapping...";
	}
	if (funcname == "service_not_found" & percdone == 0) {
		sb5_txt.text = "Service down, swapping...";
	}
	if (funcname == "image_server_process" & percdone == 0) {
		sb5_txt.text = "Map service busy.";
	}
	if (funcname == "image_server_process" & percdone == 100) {
		sb5_txt.text = "Map service processing...";
	}
	if (funcname == "image_load" & percdone<100) {
		sb5_txt.text = "Loading map, "+percdone+"% done.";
	}
	if (funcname == "image_load" & percdone == 100) {
		sb5_txt.text = "Map loaded";
	}
};
b_zi.onRollOver = function() {
	mouseover == 0
	my_hint.showHint("Zoom in");
};
b_zi.onRollOut = function() {
	mouseover == 1
	my_hint.hideHint();
};
b_zo.onRollOver = function() {
		mouseover == 0
	my_hint.showHint("Zoom out");
};
b_zo.onRollOut = function() {
		mouseover == 1
	my_hint.hideHint();
};
b_pan.onRollOver = function() {
		mouseover == 0
	my_hint.showHint("Pan");
};
b_pan.onRollOut = function() {
		mouseover == 1
	my_hint.hideHint();
};
b_za.onRollOver = function() {
		mouseover == 0
	my_hint.showHint("Zoom all");
};
b_za.onRollOut = function() {
		mouseover == 1
	my_hint.hideHint();
};
b_pin.onRollOver = function() {
		mouseover == 0
	my_hint.showHint("Pin point");
};
b_pin.onRollOut = function() {
		mouseover == 1
	my_hint.hideHint();
};
b_map.onMouseDown = function() {
	trace("DOWN");
	if (_root.b_map.interaction == "none" and mouseover==1) {
		trace("pin");
		ph_mouse._x = _root._xmouse;
		ph_mouse._y = _root._ymouse;
		//coordinates display
		if (mouseover == 1) {
			var cur_x:Number = b_map.elastic._xmouse;
			var cur_y:Number = b_map.elastic._ymouse;
			if (cur_x<=0) {
				cur_x = 0;
			}
			if (cur_x>=b_map._width) {
				cur_x = b_map._width;
			}
			if (cur_y<=0) {
				cur_y = 0;
			}
			if (cur_y>=b_map._height) {
				cur_y = b_map._height;
			}
			var screen_Point:Object = b_map.screenPointToMapPoint({x:cur_x, y:cur_y});
			switch (coo_d) {
			case "dms" :
				var c_result:Object = new Object();
				c_result = gencooS.convert(screen_Point.x, screen_Point.y, 2);
				//sb5_txt.text = c_result.lat+", "+c_result.lon;
				break;
			case "m" :
				//sb5_txt.text = "X:"+(Math.ceil(screen_Point.x*1000))/1000+", Y:"+(Math.ceil(screen_Point.y*1000))/1000;
				break;
			case "dd" :
				var c_result:Object = new Object();
				c_result = gencooS.convert(screen_Point.x, screen_Point.y, 2);
				//sb5_txt.text = c_result.lat+", "+c_result.lon;
				break;
			}
		}
		sb5_txt.text = c_result.lat+", "+c_result.lon;
		//trace(c_result.lat+", "+c_result.lon)
		//FSCommand("pickpoint",c_result.lat+", "+c_result.lon)
		getURL('javascript:pickpoint("'+c_result.lat+","+c_result.lon +'")')

	}
};
