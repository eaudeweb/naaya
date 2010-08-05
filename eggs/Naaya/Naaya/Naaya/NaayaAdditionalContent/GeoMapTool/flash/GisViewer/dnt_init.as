import com.finsiel.gis.gml.*;
import com.xfactorstudio.xml.xpath.*;
import com.luxagraf.public_classes.LuxToolTip;
//
_global.style.setStyle("themeColor", 0xEFEBEF);
_global.style.setStyle("fontFamily", "Verdana");
_global.style.setStyle("fontSize", 9);
//
//var ext_gmldata = "http://ew-demo.finsiel.ro/portal_map/geomap_gml?time=vasile";
//var ext_bbdata = "http://ew-demo.finsiel.ro/portal_map/misc_/EWGeoMap/bounding.xml";
//var ext_stdata = "http://ew-demo.finsiel.ro/portal_map/symbols_xml";
//var ext_back = "destinet_test_backgr";
//var ext_server = "geonode-test.eea.eu.int";
//var ext_bbloc = "EU";
//ask for flashvars





//vars=http://ew-demo.finsiel.ro/portal_map/geomap_gml;http://ew-demo.finsiel.ro/portal_map/misc_/EWGeoMap/bounding.xml;http://ew-demo.finsiel.ro/portal_map/symbols_xml;destinet_test_backgr;geonode-test.eea.europa.eu;EU;vars=http://ew-demo.finsiel.ro/portal_map/geomap_gml;http://ew-demo.finsiel.ro/portal_map/misc_/EWGeoMap/bounding.xml;http://ew-demo.finsiel.ro/portal_map/symbols_xml;destinet_test_backgr;geonode-test.eea.europa.eu;EU;

Mouse.hide();
cur_finger_mc._visible = true;
cur_hand_mc._visible = false;
//vars = "http://ew-demo.finsiel.ro/portal_map/geomap_gml;http://ew-demo.finsiel.ro/portal_map/misc_/EWGeoMap/bounding.xml;http://ew-demo.finsiel.ro/portal_map/symbols_xml;gml_test_dtm;geonode-test.eea.eu.int;EU;";
//ew-demo.finsiel.ro/portal_map_originstance/geomap_gml;http://ew-demo.finsiel.ro/portal_map_originstance/misc_/EWGeoMap/bounding.xml;http://ew-demo.finsiel.ro/portal_map_originstance/symbols_xml;destinet_test_backgr;geonode-test.eea.eu.int;EU;" />
var vvars:String = vars;
var mouseover:Number = 0;
var my_date:Date = new Date();



var ext_gmldata:String = vvars.split(';')[0]+"?time="+my_date.getTime();
//trace(ext_gmldata)
var ext_bbdata:String = vvars.split(';')[1];
var ext_stdata:String = vvars.split(';')[2];
var ext_back:String = vvars.split(';')[3];
var ext_server:String = vvars.split(';')[4];
var ext_bbloc:String = vvars.split(';')[5];
conn.serverName = ext_server;
conn.serviceName = ext_back;
data_gr_show._visible = false;
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
	//trace(p_eventObj.msgobj.typ);var onefound:Number = 0	
	switch (p_eventObj.msgobj.typ) {
	case "onMouseDown" :
		det_mc._visible = false;
		var ent_id:Number = Number(p_eventObj.msgobj.obj.substr(1, 1000));
		for (var i = 0; i<data_gr.length; i++) {
			if (data_gr.getItemAt(i).GML_ID == ent_id) {
				trace("mimi");
				data_gr.selectedIndex = i;
				data_gr.vPosition = i;
				data_gr_show.selectedIndex = i;
				data_gr_show.vPosition = i;
				break;
			}
		}
		var title:String = data_gr.getItemAt(i).title;
		var url:String = data_gr.getItemAt(i).url;
		var sym_label:String = data_gr.getItemAt(i).symbol_label;
		var sym_identif:String = data_gr.getItemAt(i).identifier;
		trace("Type:  ------------> "+sym_label);
		trace("title:  ------------> "+title);
		var disp:String = "";
		disp = disp+'Type: <B>          ('+sym_label+')</B><br>';
		disp = disp+'Title: <B>'+title+'</B><br>';
		disp = disp+'Loc. url: '+'<a href="'+url+'" target="_blank"><B><U><font color="#FF0000">'+url+'</font></U></B></a><br>';
		disp = disp+'Url: <B><a href="'+sym_identif+'" target="_blank"><U><font color="#FF0000">'+sym_identif+'</font></U>';
		//trace(disp)
		det_mc.data_txt.htmlText = disp;
		det_mc.data_txt.htmlText = disp;
		var parr:String = ext_stdata.substr(0, ext_stdata.length-11);
		trace(">>>>>>>>>>>>>"+parr+"getSymbolPicture?id="+data_gr.getItemAt(i).symbol_id);
		det_mc.sym_holder_mc.loadMovie(parr+"getSymbolPicture?id="+data_gr.getItemAt(i).symbol_id);
		//
		det_mc._x = _root.ph_mouse._x;
		det_mc._y = _root.ph_mouse._y;
		//
		if (det_mc._x>510) {
			det_mc._x = _root.ph_mouse._x-256;
		}
		trace(det_mc._y);
		if (det_mc._y>480) {
			det_mc._y = det_mc._y-70;
		}
		det_mc._visible = true;
		break;
	case "onMouseMove" :
		//sb_mc.sb1_txt.text = p_eventObj.msgobj.obj+" -> "+p_eventObj.msgobj.typ;
		//ccordinates diaply 
		break;
		//case "onHover" :
		//trace('tralalal');b_map
		//sb_mc.sb1_txt.text = p_eventObj.msgobj.obj+" -> "+p_eventObj.msgobj.typ;
		//my_geo_hint.showHint(p_eventObj.msgobj.obj+" -> "+p_eventObj.msgobj.typ);
		//break;
	case "gmlElementLoaded" :
		sb_mc.sb1_txt.text = "Processing GML object: "+p_eventObj.msgobj.obj;
		break;
	case "gmlRequesting" :
		sb_mc.sb1_txt.text = "Request GML file...";
		break;
	case "gmlRasterStartLoading" :
		sb_mc.sb1_txt.text = "Start loading tile "+p_eventObj.msgobj.entity+"...";
		break;
	case "gmlRasterLoaded" :
		sb_mc.sb1_txt.text = "Raster tile "+p_eventObj.msgobj.entity+" loaded.";
		break;
	case "gmlonLoadProgress" :
		sb_mc.sb1_txt.text = "Loading tile "+p_eventObj.msgobj.entity+", "+p_eventObj.msgobj.val+" % done.";
		break;
	case "gmlPolygonDrawn" :
		sb_mc.sb1_txt.text = "GML polygon "+p_eventObj.msgobj.entity+" drawn.";
		break;
	case "gmlLineDrawn" :
		sb_mc.sb1_txt.text = "GML line "+p_eventObj.msgobj.entity+" drawn.";
		break;
	case "gmlPointDrawn" :
		sb_mc.sb1_txt.text = "GML point "+p_eventObj.msgobj.entity+" drawn.";
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
		trace("TYPE: "+gmldata.gmlType);
		//
		sb_mc.sb1_txt.text = "Extract metadata...";
		var metaXML:XML = new XML(XPath.selectNodes(gmldata.gmlXML, "/gml:FeatureCollection/gml:metaDataProperty/met:info")[0]);
		trace(metaXML);
		//
		sb_mc.sb1_txt.text = "Push GML data inside datagrid...";
		data_gr.dataProvider = gmldata.gmlObjDataArray;
		//var col:mx.controls.gridclasses.DataGri
		var show_gr:Array = new Array();
		for (var i = 0; i<gmldata.gmlObjDataArray.length; i++) {
			var arritem:Object = new Object();
			arritem = {Title:gmldata.gmlObjDataArray[i].title, Type:gmldata.gmlObjDataArray[i].symbol_label, URL:gmldata.gmlObjDataArray[i].identifier, LocationURL:gmldata.gmlObjDataArray[i].url, Latitude:gmldata.gmlObjDataArray[i].latitude, Longitude:gmldata.gmlObjDataArray[i].longitude};
			show_gr.push(arritem);
		}
		data_gr_show.dataProvider = show_gr;
		sb_mc.sb1_txt.text = "GML ready.";
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
		if (gmldata.gmlType == "line") {
			l_draw();
		}
		if (gmldata.gmlType == "poly") {
			y_draw();
		}
		if (gmldata.gmlType == "raster") {
			r_draw();
		}
		break;
	case 'percent_loaded' :
		sb_mc.sb1_txt.text = "Loading GML, "+evtObj.ext_mes+"% done.";
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
	cur_finger_mc._x = _root._xmouse;
	cur_finger_mc._y = _root._ymouse;
	cur_hand_mc._x = _root._xmouse;
	cur_hand_mc._y = _root._ymouse;
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
			sb_mc.sb5_txt.text = c_result.lat+", "+c_result.lon;
			break;
		case "m" :
			sb_mc.sb5_txt.text = "X:"+(Math.ceil(screen_Point.x*1000))/1000+", Y:"+(Math.ceil(screen_Point.y*1000))/1000;
			break;
		case "dd" :
			var c_result:Object = new Object();
			c_result = gencoo.convert(screen_Point.x, screen_Point.y, "DD", "GEOG", 2);
			sb_mc.sb5_txt.text = c_result.lat+", "+c_result.lon;
			break;
		}
		//trace('move');
		//var c_result:Object = new Object();
		//c_result = gencoo.convert(screen_Point.x, screen_Point.y, "DMS", "GEOG", 2);
		//trace("out from"+c_result.lat+"/"+c_result.lon);
		//coox_txt.text = dcoo.Lat;
		//cooy_txt.text = dcoo.Long;
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
		//for (var k:Number = 0; k<=gmldata.gmlGeomDataArray.length; k++) {
		var symbol_id:Number = gmldata.gmlObjDataArray[k].symbol_id;
		var symHref:String = XPath.selectNodes(_stXML, "/symbols/symbol[id="+symbol_id+"]/picture/text()")[0];
		//trace(gmldata.gmlObjDataArray[k].symbol_id)
		//trace(symHref)
		ls.stHref = symHref;
		st_arr[gmldata.gmlGeomDataArray[k].id] = ls;
	}
}
function p_draw() {
	dp = new fGmlDrawPoint(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
function l_draw() {
	//trace(gmldata.gmlGeomDataArray)
	dl = new fGmlDrawLine(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
function y_draw() {
	//trace(gmldata.gmlGeomDataArray)
	dy = new fGmlDrawPoly(gmldata.gmlGeomDataArray, _root.b_map, myMB, st_arr);
}
function r_draw() {
	//trace(gmldata.gmlGeomDataArray)
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
	cur_finger_mc._visible = true;
	cur_hand_mc._visible = false;
	det_mc._visible = false;
	b_map.interaction = "zoomin";
	sb_mc.sb2_txt.text = "Map behaviour: Zoom in";
};
b_zo.onRelease = function() {
	cur_finger_mc._visible = true;
	cur_hand_mc._visible = false;
	det_mc._visible = false;
	b_map.interaction = "zoomout";
	sb_mc.sb2_txt.text = "Map behaviour: Zoom out";
};
b_pan.onRelease = function() {
	cur_finger_mc._visible = false;
	cur_hand_mc._visible = true;
	det_mc._visible = false;
	b_map.interaction = "pan";
	sb_mc.sb2_txt.text = "Map behaviour: Pan";
};
b_id.onRelease = function() {
	cur_finger_mc._visible = true;
	cur_hand_mc._visible = false;
	det_mc._visible = false;
	b_map.interaction = "none";
	sb_mc.sb2_txt.text = "Map behaviour: Identify";
};
b_za.onRelease = function() {
	det_mc._visible = false;
	b_map.processImage({minx:i_minx, miny:i_miny, maxx:i_maxx, maxy:i_maxy});
};
b_zs.onRelease = function() {
	det_mc._visible = false;
	trace("selectedIndex = "+data_gr.selectedIndex);
	var cellpres_id:Number = data_gr.selectedIndex;
	var ent_id:Number = data_gr.getItemAt(cellpres_id).GML_ID;
	trace(ent_id);
	switch (gmldata.gmlType) {
	case "point" :
		for (var i = 0; i<gmldata.gmlDataArray.length; i++) {
			if (gmldata.gmlGeomDataArray[i].id == ent_id) {
				var z_minx = gmldata.gmlGeomDataArray[i].bb.b_minx;
				var z_miny = gmldata.gmlGeomDataArray[i].bb.b_miny;
				var z_maxx = gmldata.gmlGeomDataArray[i].bb.b_maxx;
				var z_maxy = gmldata.gmlGeomDataArray[i].bb.b_maxy;
				trace(z_minx+"/"+z_miny);
				break;
			}
		}
		var buf:Number;
		buf = 5000.0;
		var my_mapex:Object = new Object({minx:z_minx-buf, miny:z_miny-buf, maxx:z_maxx+buf, maxy:z_maxy+buf});
		b_map.processImage(my_mapex);
		break;
	case "poly" :
		for (var i = 0; i<gmldata.gmlDataArray.length; i++) {
			if (gmldata.gmlGeomDataArray[i].id == ent_id) {
				var z_minx = gmldata.gmlGeomDataArray[i].bb.b_minx;
				var z_miny = gmldata.gmlGeomDataArray[i].bb.b_miny;
				var z_maxx = gmldata.gmlGeomDataArray[i].bb.b_maxx;
				var z_maxy = gmldata.gmlGeomDataArray[i].bb.b_maxy;
				break;
			}
		}
		var my_mapex:Object = new Object({minx:z_minx, miny:z_miny, maxx:z_maxx, maxy:z_maxy});
		//b_map.setMapextend();
		b_map.processImage(my_mapex);
		break;
	case "line" :
		for (var i = 0; i<gmldata.gmlDataArray.length; i++) {
			if (gmldata.gmlGeomDataArray[i].id == ent_id) {
				var z_minx = gmldata.gmlGeomDataArray[i].bb.b_minx;
				var z_miny = gmldata.gmlGeomDataArray[i].bb.b_miny;
				var z_maxx = gmldata.gmlGeomDataArray[i].bb.b_maxx;
				var z_maxy = gmldata.gmlGeomDataArray[i].bb.b_maxy;
				break;
			}
		}
		trace(z_minx+","+z_miny+","+z_maxx+","+z_maxy);
		var my_mapex:Object = new Object({minx:z_minx, miny:z_miny, maxx:z_maxx, maxy:z_maxy});
		//b_map.setMapextend();
		b_map.processImage(my_mapex);
		break;
	case "raster" :
		for (var i = 0; i<gmldata.gmlDataArray.length; i++) {
			if (gmldata.gmlGeomDataArray[i].id == ent_id) {
				var z_minx = gmldata.gmlGeomDataArray[i].bb.b_minx;
				var z_miny = gmldata.gmlGeomDataArray[i].bb.b_miny;
				var z_maxx = gmldata.gmlGeomDataArray[i].bb.b_maxx;
				var z_maxy = gmldata.gmlGeomDataArray[i].bb.b_maxy;
				break;
			}
		}
		var my_mapex:Object = new Object({minx:z_minx, miny:z_miny, maxx:z_maxx, maxy:z_maxy});
		//b_map.setMapextend();
		b_map.processImage(my_mapex);
		break;
	}
};
b_map.onStatus = function(status:Boolean, funcname:String, percdone:Number, msg:String) {
	if (funcname == "server_not_found" & percdone == 0) {
		_root.sb_mc.sb3_txt.text = "Server down, swapping...";
	}
	if (funcname == "service_not_found" & percdone == 0) {
		_root.sb_mc.sb3_txt.text = "Service down, swapping...";
	}
	if (funcname == "image_server_process" & percdone == 0) {
		_root.sb_mc.sb3_txt.text = "Map service busy.";
	}
	if (funcname == "image_server_process" & percdone == 100) {
		_root.sb_mc.sb3_txt.text = "Map service processing...";
	}
	if (funcname == "image_load" & percdone<100) {
		_root.sb_mc.sb3_txt.text = "Loading map, "+percdone+"% done.";
	}
	if (funcname == "image_load" & percdone == 100) {
		_root.sb_mc.sb3_txt.text = "Map loaded";
	}
};
//tooltips
//(target:MovieClip, depth:Number, font:String, fontSize:Number, color:Number, embedFlag:Boolean, borderColor:Number, fillColor)
//now lets say you have a button, 'my_btn' that you want to show a hint on the rollover event
b_zi.onRollOver = function() {
	my_hint.showHint("Zoom in");
};
b_zi.onRollOut = function() {
	my_hint.hideHint();
};
b_zo.onRollOver = function() {
	my_hint.showHint("Zoom out");
};
b_zo.onRollOut = function() {
	my_hint.hideHint();
};
b_pan.onRollOver = function() {
	my_hint.showHint("Pan");
};
b_pan.onRollOut = function() {
	my_hint.hideHint();
};
b_za.onRollOver = function() {
	my_hint.showHint("Zoom all");
};
b_za.onRollOut = function() {
	my_hint.hideHint();
};
b_id.onRollOver = function() {
	my_hint.showHint("Identify");
};
b_id.onRollOut = function() {
	my_hint.hideHint();
};
b_grid.onRollOver = function() {
	my_hint.showHint("Display data");
};
b_grid.onRollOut = function() {
	my_hint.hideHint();
};
b_zs.onRollOver = function() {
	my_hint.showHint("Zoom to selected");
};
b_zs.onRollOut = function() {
	my_hint.hideHint();
};
import mx.managers.PopUpManager;
import mx.containers.Window;
b_pref.onRelease = function() {
	win = PopUpManager.createPopUp(_root, Window, true, {closeButton:true, _x:225, _y:200, title:"Preferences", _width:320, _height:200, contentPath:"ref_mc"});
	lo = new Object();
	lo.click = function() {
		win.deletePopUp();
	};
	win.addEventListener("click", lo);
};
b_grid.onRelease = function() {
	det_mc._visible = false;
	data_gr_show._visible = not (data_gr_show._visible);
};
var dgListener:Object = new Object();
dgListener.cellPress = function(evt_obj:Object) {
	//var cell_str:String = "("+evt_obj.columnIndex+", "+evt_obj.itemIndex+")";
	//trace("The cell at "+cell_str+" has been clicked");
	data_gr.selectedIndex = evt_obj.itemIndex;
	data_gr.vPosition = evt_obj.itemIndex;
};
// Add listener.
data_gr_show.addEventListener("cellPress", dgListener);
