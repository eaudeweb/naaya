// !!!!!! the coordinates transcalculation form Lambert Asimuthal Equal Area are quite similar wilth Azimuthal Equidistant
// The function Convert_Azimuthal_Equidistant_To_Geodetic converts Azimuthal_Equidistant projection
// (easting and northing) coordinates to geodetic (latitude and longitude)
// coordinates, according to the current ellipsoid and Azimuthal_Equidistant projection
// coordinates.  If any errors occur, the error code(s) are returned by the
// function, otherwise AZEQ_NO_ERROR is returned.
// Easting           : Easting (X) in meters                  (input)
// Northing          : Northing (Y) in meters                 (input)
// Latitude          : Latitude (phi) in radians              (output)
// Longitude         : Longitude (lambda) in radians          (output)
// decimals			 :Number of decimals for DD 				(input)
// format:			 :MATH using minus for negative, GEOG using E/W;N/S
// type				 :DD 15.4848; DMS 15*18'48''
//--example input
//var cur_x:Number = main_map.elastic._xmouse
//var cur_y:Number = main_map.elastic._ymouse
//var screen_Point:Object = main_map.screenPointToMapPoint({x:cur_x, y:cur_y});
//dcoo = transcalc(rc(screen_Point.x), rc(screen_Point.y) ,"DMS","GEOG",2)
//coox_txt.text = dcoo.Lat
//cooy_txt.text =dcoo.Long
//--end example
//Curent parameters									 */
// PROJCS["ETRS-LAEA5220",
//GEOGCS["ETRS89",
//DATUM["<custom>",
//SPHEROID["GRS_1980",	6378137.0,298.257222101]],
//PRIMEM["Greenwich",0.0],
//UNIT["Degree",0.0174532925199433]],
//PROJECTION["Lambert_Azimuthal_Equal_Area"],
//PARAMETER["False_Easting",5071000.0],
//PARAMETER["False_Northing",3210000.0],
//PARAMETER["Central_Meridian",20.0],
//PARAMETER["Latitude_Of_Origin",52.0],UNIT["Meter",1.0]]
class com.finsiel.gis.gml.fUtilCooConvS {
	//in radioans
	// = {Lat:Latitude_output, Long:Longitude_output};
	function fUtilCooConvS() {
	}
	public function convert(_Easting:Number, _Northing:Number, _decimals:Number):Object {
		var dx:Number;
		var dy:Number;
		var rho:Number;
		/* height above ellipsoid */
		var c:Number;
		/* angular distance from center */
		var sin_c:Number;
		var cos_c:Number;
		var dy_sinc:Number;
		var a:Number = 6378137.0;
		var f:Number = 1/298.257223563;
		var Ra:Number = 6371007.1810824;
		var Azeq_False_Easting:Number = 4321000.0;
		var Azeq_False_Northing:Number = 3210000.0;
		var PI:Number = 3.14159265358979323;
		var PI_OVER_2:Number = (PI/2.0);
		var TWO_PI:Number = (2.0*PI);
		var ONE:Number = (1.0*PI/180);
		//in radians
		var Azeq_Origin_Lat:Number = (52.0*PI/180.0);
		var Azeq_Origin_Long:Number = (10.0*PI/180.0);
		var abs_Azeq_Origin_Lat:Number = (52.0*PI/180.0);
		var Easting:Number = Number(_Easting);
		var Northing:Number = Number(_Northing);
		//var type:String = _type;
		//var format:String = _format;
		var decimals:Number = _decimals;
		var Longitude:Number;
		var Latitude:Number;
		var Azeq_Delta_Easting = 0;
		var Azeq_Delta_Northing = 0;
		var Sin_Azeq_Origin_Lat:Number = Math.sin(Azeq_Origin_Lat);
		var Cos_Azeq_Origin_Lat:Number = Math.cos(Azeq_Origin_Lat);
		var Error_Code:String = "AZEQ_NO_ERROR";
		//if ((Easting<(Azeq_False_Easting-Azeq_Delta_Easting)) || (Easting>(Azeq_False_Easting+Azeq_Delta_Easting))) {
		// Easting out of range  
		//Error_Code += "AZEQ_EASTING_ERROR";
		//}
		//if ((Northing<(Azeq_False_Northing-Azeq_Delta_Northing)) || (Northing>(Azeq_False_Northing+Azeq_Delta_Northing))) {
		// Northing out of range 
		//Error_Code += " AZEQ_NORTHING_ERROR";
		//}
		//trace(Error_Code);          
		if (Error_Code == "AZEQ_NO_ERROR") {
			var dy:Number = Northing-Azeq_False_Northing;
			var dx:Number = Easting-Azeq_False_Easting;
			//trace("delta" + dx + "/"+dy)
			var rho:Number = Math.sqrt(dx*dx+dy*dy);
			if (Math.abs(rho)<=0.0000000001) {
				Latitude = Azeq_Origin_Lat;
				Longitude = Azeq_Origin_Long;
			} else {
				var c:Number = rho/Ra;
				sin_c = Math.sin(c);
				cos_c = Math.cos(c);
				dy_sinc = dy*sin_c;
				//dy_sinc = dy*sin_c;
				Latitude = Math.asin((cos_c*Sin_Azeq_Origin_Lat)+((dy_sinc*Cos_Azeq_Origin_Lat)/rho));
				if (Math.abs(abs_Azeq_Origin_Lat-PI_OVER_2)<0.0000000001) {
					if (Azeq_Origin_Lat>=0.0) {
						Longitude = Azeq_Origin_Long+Math.atan2(dx, -dy);
					} else {
						Longitude = Azeq_Origin_Long+Math.atan2(dx, dy);
					}
				} else {
					Longitude = Azeq_Origin_Long+Math.atan2((dx*sin_c), ((rho*Cos_Azeq_Origin_Lat*cos_c)-(dy_sinc*Sin_Azeq_Origin_Lat)));
				}
			}
			if (Latitude>PI_OVER_2) {
				/* force distorted values to 90, -90 degrees */
				Latitude = PI_OVER_2;
			} else if (Latitude<-PI_OVER_2) {
				Latitude = -PI_OVER_2;
			}
			if (Longitude>PI) {
				Longitude -= TWO_PI;
			}
			if (Longitude<-PI) {
				Longitude += TWO_PI;
			}
			if (Longitude>PI) {
				/* force distorted values to 180, -180 degrees */
				Longitude = PI;
			} else if (Longitude<-PI) {
				Longitude = -PI;
			}
		}
		Latitude = (Latitude*180.0/PI);
		Longitude = (Longitude*180.0/PI);
		//trace("in1"+Latitude + "/"+Longitude )
		//starting diplay work
		//number of decimals
		var Latitude_display:Number;
		var Longitude_display:Number;
		var decim:Number;
		decim = Math.pow(10, decimals);
		Latitude_display = (Math.ceil(Latitude*decim))/decim;
		Longitude_display = (Math.ceil(Longitude*decim))/decim;
		var Latitude_output:String;
		var Longitude_output:String;
		if (Latitude_display<=0) {
			Latitude_output = conv(Latitude_display)+"S";
		}
		if (Latitude_display>0) {
			Latitude_output = conv(Latitude_display)+"N";
		}
		if (Longitude_display<=0) {
			Longitude_output = conv(Longitude_display)+"W";
		}
		if (Longitude_display>0) {
			Longitude_output = conv(Longitude_display)+"E";
		}
		//trace("in2"+Latitude_output + "/" + Longitude_output)   
		return ({lat:Latitude_output, lon:Longitude_output});
	}
	function conv(val:Number):String {
		val = Math.abs(val);
		var gr:Number;
		gr = Math.floor(val);
		var mi:Number;
		mi = (val-gr)*60;
		var min:Number;
		min = Math.floor(mi);
		var se:Number;
		se = (mi-min)*60;
		var sec:Number;
		sec = Math.floor(se);
		var gr_disp:String;
		var min_disp:String;
		var sec_disp:String;
		if (gr.toString().length == 1) {
			gr_disp = "0"+gr.toString();
		} else {
			gr_disp = gr.toString();
		}
		
		
		if (min.toString().length == 1) {
			min_disp = "0"+min.toString();
		} else {
			min_disp = min.toString();
		}
		if (sec.toString().length == 1) {
			sec_disp = "0"+sec.toString();
		} else {
			sec_disp = sec.toString();
		}
		var conv_str = gr_disp+min_disp+sec_disp;
		return (conv_str);
	}
}
