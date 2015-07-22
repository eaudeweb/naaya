import com.xfactorstudio.xml.xpath.*;
import com.finsiel.gis.gml.fUtilTrim;
class com.finsiel.gis.gml.fGmlPrepare {
	//dispatchers
	public var addEventListener:Function;
	public var removeEventListener:Function;
	private var _myMB;
	public var _elementparse:Number = 0;
	public var dispatchEvent:Function;
	public var _gmlPath:String;
	public var _gmlType:String;
	public var _gmlXML:XML;
	public var _gmlString:String = new String();
	public var _gmlIof:Number = 0;
	public var _gmlFields:Array;
	private var _gmlDataArray:Array = new Array();
	public var _gmlObjDataArray:Array = new Array();
	public var _gmlGeomDataArray:Array = new Array();
	private var _gmlMaxEntity:Number = 5000;
	public var _gmlBB:Object;
	private var intervalId_read:Number;
	private var intervalId_data_array:Number;
	private var duration_read:Number = 1;
	//try to read at each 5 ms
	private var _gmlCurEntity:Number = 1;
	private var _gmlFieldType:String;
	//first entitity to be read
	function fGmlPrepare(myMB) {
		mx.events.EventDispatcher.initialize(this);
		_gmlXML = new XML();
		_myMB = myMB;
	}
	function get gmlXML() {
		return (this._gmlXML);
	}
	function get gmlBB() {
		return (this._gmlBB);
	}
	function get gmlFields() {
		return (this._gmlFields);
	}
	function get gmlDataArray() {
		return (this._gmlDataArray);
	}
	function get gmlObjDataArray() {
		return (this._gmlObjDataArray);
	}
	function get gmlGeomDataArray() {
		return (this._gmlGeomDataArray);
	}
	///---------------------
	function set gmlPath(str:String) {
		this._gmlPath = str;
	}
	function get gmlPath() {
		return (this._gmlPath);
	}
	///---------------------
	function get gmlType() {
		return (this._gmlType);
	}
	function set gmlType(str:String) {
		this._gmlType = str;
	}
	///---------------------
	public function gmlRead():Void {
		var thisObj:fGmlPrepare = this;
		var bytesTotal:Number = _gmlXML.getBytesTotal();
		var eventObject:Object = {target:this, type:'done', mes:'gmlRequesting', ext_mes:this._gmlPath};
		thisObj.dispatchEvent(eventObject);
		_gmlXML = new XML();
		_gmlXML.ignoreWhite = true;
		_gmlXML.onLoad = function(success:Boolean) {
			if (success) {
				clearInterval(load_intervalID);
				thisObj.gmlType = thisObj.assign_gmlType();
				thisObj.assign_BB();
				thisObj.assign_gmlFields();
				thisObj.assign_data();
			} else {
				var eventObject:Object = {target:this, type:'done', mes:'gmlFailed', ext_mes:'ext_gmlFailed'};
				thisObj.dispatchEvent(eventObject);
			}
		};
		var checkProgress = function (_gmlXML:XML) {
			var bytesLoaded:Number = _gmlXML.getBytesLoaded();
			var bytesTotal:Number = _gmlXML.getBytesTotal();
			var percentLoaded:Number = Math.floor((bytesLoaded/bytesTotal)*100);
			var eventObject:Object = {target:this, type:'done', mes:'percent_loaded', ext_mes:percentLoaded};
			thisObj.dispatchEvent(eventObject);
		};
		_gmlXML.load(this._gmlPath);
		var load_intervalID:Number = setInterval(checkProgress, 20, _gmlXML);
	}
	private function assign_BB() {
		var BB_minx:Number = Number(XPath.selectNodes(_gmlXML, "/gml:FeatureCollection/gml:boundedBy/child::*/gml:coord/gml:X/text()")[0]);
		var BB_maxx:Number = Number(XPath.selectNodes(_gmlXML, "/gml:FeatureCollection/gml:boundedBy/child::*/gml:coord/gml:X/text()")[1]);
		var BB_miny:Number = Number(XPath.selectNodes(_gmlXML, "/gml:FeatureCollection/gml:boundedBy/child::*/gml:coord/gml:Y/text()")[0]);
		var BB_maxy:Number = Number(XPath.selectNodes(_gmlXML, "/gml:FeatureCollection/gml:boundedBy/child::*/gml:coord/gml:Y/text()")[1]);
		_gmlBB = {BB_minx:BB_minx, BB_miny:BB_miny, BB_maxx:BB_maxx, BB_maxy:BB_maxy};
	}
	private function assign_gmlType():String {
		var data_type:String;
		var is_raster:String;
		var is_point:String;
		var is_line:String;
		var is_poly:String;
		var is_multiline:String;
		var is_multipoly:String;
		var classXML:XML = new XML(XPath.selectNodes(this._gmlXML, "/gml:FeatureCollection/gml:featureMember[1]")[0]);
		is_point = XPath.selectNodes(classXML, "/gml:featureMember/child::*/child::*/gml:Point")[0];
		is_line = XPath.selectNodes(classXML, "/gml:featureMember/child::*/child::*/gml:LineString")[0];
		is_multiline = XPath.selectNodes(classXML, "/gml:featureMember/child::*/child::*/gml:MultiLineString")[0];
		is_poly = XPath.selectNodes(classXML, "/gml:featureMember/child::*/child::*/gml:Polygon")[0];
		is_multipoly = XPath.selectNodes(classXML, "/gml:featureMember/child::*/child::*/gml:MultiPolygon")[0];
		is_raster = XPath.selectNodes(classXML, "/gml:featureMember/child::*/child::*/gml:Raster")[0];
		if (is_point<>undefined) {
			data_type = "point";
		} else {
			if (is_line<>undefined) {
				data_type = "line";
			} else {
				if (is_poly<>undefined) {
					data_type = "poly";
				} else {
					if (is_multiline<>undefined) {
						data_type = "line";
					} else {
						if (is_multipoly<>undefined) {
							data_type = "poly";
						} else {
							if (is_raster<>undefined) {
								data_type = "raster";
							}
						}
					}
				}
			}
		}
		trace(data_type);
		return (data_type);
	}
	//to check
	private function assign_gmlFields() {
		_gmlFields = new Array();
		var clArray:Array = XPath.selectNodes(this._gmlXML, "/gml:FeatureCollection/gml:featureMember[1]/node()/node()");
		for (var i = 0; i<clArray.length; i++) {
			//trace(String(clArray[i]).substr(0, 19))
			if (String(clArray[i]).substr(0, 22)<>"<gml:geometryProperty>") {
				if (String(clArray[i]).substr(0, 18)<>"<geometryProperty>") {
					var field:String = new String();
					field = String(clArray[i]);
					//trace("----------------------------------");
					//trace("cimp: "+field);
					//trace("index: "+field.indexOf("/>", 0));
					if (field.indexOf(" />", 0)<>-1) {
						var end:Number = Number(field.indexOf(" />", 0));
						_gmlFields.push(String(clArray[i]).substring(1, end));
						//trace("extract: |"+(String(clArray[i]).substring(1, end))+"|");
					} else {
						var end:Number = String(clArray[i]).indexOf(">", 0);
						_gmlFields.push(String(clArray[i]).substr(1, end-1));
						//trace("extract |"+(String(clArray[i]).substr(1, end-1))+"|");
					}
				}
			}
		}
		_gmlFields.push("GML_ID");
	}
	//assign data by interval to prevent browser freezing - maximum 5000 entities
	private function pushelement(ent:XML, no:Number) {
		this._gmlDataArray[no] = ent;
	}
	function sendmes(mess:Object) {
		_myMB.sendMessage(mess);
	}
	private function assign_data() {
		_gmlString = String(_gmlXML);
		beginInterval_read();
	}
	private function beginInterval_read():Void {
		if (intervalId_read != null) {
			clearInterval(intervalId_read);
		}
		intervalId_read = setInterval(this, "executeCallback_read", duration_read);
	}
	public function executeCallback_read():Void {
		var thisObj = this;
		var ent:XML = new XML();
		if (_gmlCurEntity<_gmlMaxEntity) {
			var poz1 = thisObj._gmlString.indexOf("<gml:featureMember>", thisObj._gmlIof);
			var poz2 = thisObj._gmlString.indexOf("</gml:featureMember>", thisObj._gmlIof);
			var gmlSelement:String = thisObj._gmlString.substr(poz1, poz2-poz1)+"</gml:featureMember>";
			if (poz1 == -1) {
				trace("SToP ENTITIES");
				//thisObj.create_obj_data_array();
				//thisObj.create_geom_data_array();
				var eventObject:Object = {target:this, type:'done', mes:'gmlLoaded', ext_mes:'ext_gmlLoaded'};
				thisObj.dispatchEvent(eventObject);
				clearInterval(intervalId_read);
			} else {
				if (gmlSelement<>"</gml:featureMember>") {
					thisObj.pushelement(gmlSelement, _gmlCurEntity);
					//thisObj._gmlObjDataArray.push(create_object(gmlSelement, _gmlCurEntity));
					thisObj.create_obj_data_array(gmlSelement, _gmlCurEntity);
					thisObj.create_geom_data_array(gmlSelement, _gmlCurEntity);
					thisObj.sendmes({obj:_gmlCurEntity, typ:"gmlElementLoaded"});
					_gmlCurEntity++;
					thisObj._gmlIof = poz2+19;
				}
			}
		} else {
			trace("SToP full entiries");
			//thisObj.create_obj_data_array();
			//thisObj.create_geom_data_array();
			var eventObject:Object = {target:this, type:'done', mes:'gmlLoaded', ext_mes:'ext_gmlLoaded'};
			thisObj.dispatchEvent(eventObject);
			clearInterval(intervalId_read);
		}
	}
	//assign data by interval to prevent browser freezing
	private function create_obj_data_array(tXML:String, id:Number) {
		this._gmlObjDataArray.push(create_object(tXML, id));
	}
	private function create_object(tXML:String, id:Number):Object {
		var myObj:Object = new Object();
		var att_number:Number = gmlFields.length;
		for (var j = att_number-1; j>=0; j--) {
			var str2:String = tXML.split("<"+gmlFields[j]+">")[1].split("</"+gmlFields[j]+">")[0];
			myObj[gmlFields[j]] = str2;
		}
		myObj[gmlFields[att_number-1]] = id;
		return myObj;
	}
	private function create_geom_data_array(elem_xml, i) {
		switch (this._gmlType) {
		case "point" :
			this._gmlGeomDataArray.push(create_point(elem_xml, i));
			break;
		case "line" :
			this._gmlGeomDataArray.push(create_line(elem_xml, i));
			break;
		case "poly" :
			this._gmlGeomDataArray.push(create_poly(elem_xml, i));
			break;
		case "raster" :
			this._gmlGeomDataArray.push(create_raster(elem_xml, i));
			break;
		}
	}
	private function create_point(tXML:String, GMLID:Number):Object {
		var tr = new fUtilTrim();
		var myObj:Object = new Object();
		//var str1:String = tXML.split("<gml:geometryProperty><gml:Point><gml:coordinates>")[1];
		//var str2:String = str1.split("</gml:coordinates>")[0];
		var txXML:XML = new XML(tXML);
		txXML.ignoreWhite = true;
		var coo:String = new String();
		coo = String(XPath.selectNodes(txXML, "/gml:featureMember/child::*/child::*/gml:Point/gml:coordinates/text()")[0]);
		var sp_arr:Array = tr.LRtrim(coo).split(",");
		myObj['x'] = sp_arr[0];
		myObj['y'] = sp_arr[1];
		myObj['id'] = GMLID;
		myObj['bb'] = {b_minx:Number(sp_arr[0]), b_miny:Number(sp_arr[1]), b_maxx:Number(sp_arr[0]), b_maxy:Number(sp_arr[1])};
		return myObj;
	}
	private function create_line(tXML:String, GML_ID:Number):Object {
		var tr = new fUtilTrim();
		//variables for bounding box
		var b_minx:Number;
		var b_miny:Number;
		var b_maxx:Number;
		var b_maxy:Number;
		//entity
		var myEntObj:Array = new Array();
		//vertex
		var myVertexObj:Object = new Object();
		//final object
		var myObj:Object = new Object();
		//chech if is multiline or single linr
		var ms:String = "unknown";
		var ms:String = tXML.split("gml:MultiLineString")[1];
		if (ms == undefined) {
			var txXML:XML = new XML(tXML);
			txXML.ignoreWhite = true;
			var coo:String = new String();
			//extract coordinates
			coo = String(XPath.selectNodes(txXML, "/gml:featureMember/child::*/child::*/gml:LineString/gml:coordinates/text()")[0]);
			var cooarray:Array = new Array();
			var cooarray = coo.split(" ");
			//create reference for boundingbox
			b_minx = Number(cooarray[0].split(",")[0]);
			b_maxx = Number(cooarray[0].split(",")[0]);
			b_miny = Number(cooarray[0].split(",")[1]);
			b_maxy = Number(cooarray[0].split(",")[1]);
			//part
			var myPartObj:Array = new Array();
			for (var i = 0; i<cooarray.length; i++) {
				//create vertex list
				var coox:Number = Number(cooarray[i].split(",")[0]);
				var cooy:Number = Number(cooarray[i].split(",")[1]);
				myVertexObj = {x:coox, y:cooy};
				//push vertexes iside part
				myPartObj.push(myVertexObj);
				//reassign bb
				if (coox<b_minx) {
					b_minx = coox;
				}
				if (cooy<b_miny) {
					b_miny = cooy;
				}
				if (coox>b_maxx) {
					b_maxx = coox;
				}
				if (cooy>b_maxy) {
					b_maxy = cooy;
				}
			}
			//push part inside entity
			myEntObj.push(myPartObj);
			//create line object
			myObj['geom'] = myEntObj;
			myObj['id'] = GML_ID;
			myObj['bb'] = {b_minx:b_minx, b_miny:b_miny, b_maxx:b_maxx, b_maxy:b_maxy};
		} else {
			var txXML:XML = new XML(tXML);
			txXML.ignoreWhite = true;
			var parts:Array = new Array();
			parts = XPath.selectNodes(txXML, "/gml:featureMember/child::*/child::*/gml:MultiLineString/gml:lineStringMember/gml:LineString/gml:coordinates/text()");
			//create reference for boundingbox
			b_minx = Number(parts[0].split(" ")[0].split(",")[0]);
			b_maxx = Number(parts[0].split(" ")[0].split(",")[0]);
			b_miny = Number(parts[0].split(" ")[0].split(",")[1]);
			b_maxy = Number(parts[0].split(" ")[0].split(",")[1]);
			for (var j = 0; j<parts.length; j++) {
				var cooarray:Array = new Array();
				var cooarray = parts[j].split(" ");
				var myPartObj:Array = new Array();
				for (var i = 0; i<cooarray.length; i++) {
					//create vertex list
					var coox:Number = Number(cooarray[i].split(",")[0]);
					var cooy:Number = Number(cooarray[i].split(",")[1]);
					myVertexObj = {x:coox, y:cooy};
					//push vertexes iside part
					myPartObj.push(myVertexObj);
					//reassign bb
					if (coox<b_minx) {
						b_minx = coox;
					}
					if (cooy<b_miny) {
						b_miny = cooy;
					}
					if (coox>b_maxx) {
						b_maxx = coox;
					}
					if (cooy>b_maxy) {
						b_maxy = cooy;
					}
				}
				myEntObj.push(myPartObj);
			}
			//create line object
			myObj['geom'] = myEntObj;
			myObj['id'] = GML_ID;
			myObj['bb'] = {b_minx:b_minx, b_miny:b_miny, b_maxx:b_maxx, b_maxy:b_maxy};
		}
		return myObj;
	}
	private function create_poly(tXML:String, GML_ID:Number):Object {
		var tr = new fUtilTrim();
		//variables for bounding box
		var b_minx:Number;
		var b_miny:Number;
		var b_maxx:Number;
		var b_maxy:Number;
		//entity
		var myEntObj:Array = new Array();
		//vertex
		var myVertexObj:Object = new Object();
		//final object
		var myObj:Object = new Object();
		//chech if is multipoly or single poly
		var ms:String = "unknown";
		var ms:String = tXML.split("gml:MultiPolygon")[1];
		if (ms == undefined) {
			var txXML:XML = new XML(tXML);
			txXML.ignoreWhite = true;
			var coo:String = new String();
			//extract coordinates
			coo = String(XPath.selectNodes(txXML, "/gml:featureMember/child::*/child::*/gml:Polygon/gml:outerBoundaryIs/gml:LinearRing/gml:coordinates/text()")[0]);
			var cooarray:Array = new Array();
			var cooarray = coo.split(" ");
			//create reference for boundingbox
			b_minx = Number(cooarray[0].split(",")[0]);
			b_maxx = Number(cooarray[0].split(",")[0]);
			b_miny = Number(cooarray[0].split(",")[1]);
			b_maxy = Number(cooarray[0].split(",")[1]);
			//part
			var myPartObj:Array = new Array();
			for (var i = 0; i<cooarray.length; i++) {
				//create vertex list
				var coox:Number = Number(cooarray[i].split(",")[0]);
				var cooy:Number = Number(cooarray[i].split(",")[1]);
				myVertexObj = {x:coox, y:cooy};
				//push vertexes iside part
				myPartObj.push(myVertexObj);
				//reassign bb
				if (coox<b_minx) {
					b_minx = coox;
				}
				if (cooy<b_miny) {
					b_miny = cooy;
				}
				if (coox>b_maxx) {
					b_maxx = coox;
				}
				if (cooy>b_maxy) {
					b_maxy = cooy;
				}
			}
			//push part inside entity
			myEntObj.push(myPartObj);
			//create line object
			myObj['geom'] = myEntObj;
			myObj['id'] = GML_ID;
			myObj['bb'] = {b_minx:b_minx, b_miny:b_miny, b_maxx:b_maxx, b_maxy:b_maxy};
		} else {
			var txXML:XML = new XML(tXML);
			txXML.ignoreWhite = true;
			var parts:Array = new Array();
			parts = XPath.selectNodes(txXML, "/gml:featureMember/child::*/child::*/gml:MultiPolygon/gml:polygonMember/gml:Polygon/gml:outerBoundaryIs/gml:LinearRing/gml:coordinates/text()");
			//create reference for boundingbox
			b_minx = Number(parts[0].split(" ")[0].split(",")[0]);
			b_maxx = Number(parts[0].split(" ")[0].split(",")[0]);
			b_miny = Number(parts[0].split(" ")[0].split(",")[1]);
			b_maxy = Number(parts[0].split(" ")[0].split(",")[1]);
			for (var j = 0; j<parts.length; j++) {
				var cooarray:Array = new Array();
				var cooarray = parts[j].split(" ");
				var myPartObj:Array = new Array();
				for (var i = 0; i<cooarray.length; i++) {
					//create vertex list
					var coox:Number = Number(cooarray[i].split(",")[0]);
					var cooy:Number = Number(cooarray[i].split(",")[1]);
					myVertexObj = {x:coox, y:cooy};
					//push vertexes iside part
					myPartObj.push(myVertexObj);
					//reassign bb
					if (coox<b_minx) {
						b_minx = coox;
					}
					if (cooy<b_miny) {
						b_miny = cooy;
					}
					if (coox>b_maxx) {
						b_maxx = coox;
					}
					if (cooy>b_maxy) {
						b_maxy = cooy;
					}
				}
				myEntObj.push(myPartObj);
			}
			//create line object
			myObj['geom'] = myEntObj;
			myObj['id'] = GML_ID;
			myObj['bb'] = {b_minx:b_minx, b_miny:b_miny, b_maxx:b_maxx, b_maxy:b_maxy};
		}
		return myObj;
	}
	private function create_raster(tXML:String, GML_ID:Number):Object {
		var tr = new fUtilTrim();
		//variables for bounding box
		var b_minx:Number;
		var b_miny:Number;
		var b_maxx:Number;
		var b_maxy:Number;
		//entity
		var myEntObj:Array = new Array();
		//vertex
		var myVertexObj:Object = new Object();
		//final object
		var myObj:Object = new Object();
		//chech if is multipoly or single poly
		var txXML:XML = new XML(tXML);
		txXML.ignoreWhite = true;
		var coo:String = new String();
		//extract coordinates
		coo = String(XPath.selectNodes(txXML, "/gml:featureMember/child::*/child::*/gml:Raster/gml:outerBoundaryIs/gml:LinearRing/gml:coordinates/text()")[0]);
		var cooarray:Array = new Array();
		var cooarray = coo.split(" ");
		//create reference for boundingbox
		b_minx = Number(cooarray[0].split(",")[0]);
		b_maxx = Number(cooarray[0].split(",")[0]);
		b_miny = Number(cooarray[0].split(",")[1]);
		b_maxy = Number(cooarray[0].split(",")[1]);
		//part
		var myPartObj:Array = new Array();
		for (var i = 0; i<cooarray.length; i++) {
			//create vertex list
			var coox:Number = Number(cooarray[i].split(",")[0]);
			var cooy:Number = Number(cooarray[i].split(",")[1]);
			myVertexObj = {x:coox, y:cooy};
			//push vertexes iside part
			myPartObj.push(myVertexObj);
			//reassign bb
			if (coox<b_minx) {
				b_minx = coox;
			}
			if (cooy<b_miny) {
				b_miny = cooy;
			}
			if (coox>b_maxx) {
				b_maxx = coox;
			}
			if (cooy>b_maxy) {
				b_maxy = cooy;
			}
		}
		//push part inside entity
		myEntObj.push(myPartObj);
		//create line object
		myObj['geom'] = myEntObj;
		myObj['id'] = GML_ID;
		myObj['bb'] = {b_minx:b_minx, b_miny:b_miny, b_maxx:b_maxx, b_maxy:b_maxy};
		myObj['raster'] = String(XPath.selectNodes(txXML, "/gml:featureMember/child::*/gml:source/text()")[0]);
		var resx:Number = Number(XPath.selectNodes(txXML, "/gml:featureMember/child::*/gml:resx/text()")[0]);
		var resy:Number = Number(XPath.selectNodes(txXML, "/gml:featureMember/child::*/gml:resy/text()")[0]);
		myObj['resolution'] = {resx:resx, resy:resy};
		return myObj;
	}
}
