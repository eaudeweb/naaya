import XMLRPC.*;

_root.country_name_ = "";
var RPCConn = new Connection();
var retRec:Object = new Object();

var colors = new Array();

//no information received
colors[-1] = new Array();
colors[-1][0] = 231;
colors[-1][1] = 231;
colors[-1][2] = 231;

//outside of this project
colors[0] = new Array();
colors[0][0] = 231;
colors[0][1] = 231;
colors[0][2] = 231;

//EEA countries
colors[1] = new Array();
colors[1][0] = 255;
colors[1][1] = 201;
colors[1][2] = 91;

//collaborating in other ways
colors[2] = new Array();
colors[2][0] = 255;
colors[2][1] = 153;
colors[2][2] = 51;

//using the CHM PTK
colors[3] = new Array();
colors[3][0] = 216;
colors[3][1] = 89;
colors[3][2] = 28;



xmlrpcserver += "";
trace(xmlrpcserver);
if(xmlrpcserver=="undefined" || xmlrpcserver==""){
	xmlrpcserver="http://biodiversity-chm.eea.eu.int/portal_europe/"
}

RPCConn.Server = xmlrpcserver;
//RPCConn.Quiet = true;
//Handle method response
RPCConn.OnLoad = function(methodResponse) {
	fillData(methodResponse)
};
//Clear old parameters, usually shouldn't be any
RPCConn.ClearParameters();
//apel cu parametru
//RPCConn.AddParameter("ro", XMLRPC.types.STRING);
//RPCConn.get_europe_country_info();

//apel fara parametru
//temp = RPCConn.get_europe_countries();
temp=RPCConn.get_flash_data();

country_info.description.vScrollPolicy = 'on';
country_info.description.html = true;
country_info.description.wordWrap = true;
country_info.description.scroll = true;
country_info.description.multiline = true;

vers1 = getVersion().split(" ")[1].split(",");
if (vers1[0]>=8)_root.updateWarning._visible = false;
_root.update_text = "In order to see this flash movie properly<br />you must update your Flash Player from<br /><a href='http://www.macromedia.com/go/getflashplayer'><u><font color='#6666ff'>Macromedia Flash Player Download Center</font></u></a>"

function fillData(param){
	for(i in param[0]){
		x = eval("_root.map.map0."+param[0][i]+"_");
		x.title = param[1][i];
	}

	for(i in param[2]){
		x = eval("_root.map.map0."+param[2][i][0]+"_");
		for(b=0;b<8;b++){
			if(typeof(param[2][i][b])=="undefined")param[2][i][b]="";
		}
		x.code         = param[2][i][0];
		x.title        = param[2][i][1];
		x.organisation = param[2][i][2];
		x.contact      = param[2][i][3];
		x.state        = param[2][i][4];
		x.countryUrl   = param[2][i][5];
		x.countryHost  = param[2][i][6];
		x.CBDURL       = param[2][i][7];

		if(x.state>1)x.useHandCursor = true;

		colorCountry(x,False);
	}

}


codes = new Array("dk_","ee_","gr_","al_","cz_","de_","be_","fr_","bg_","hu_","tr_","ro_","is_","no_","se_","fi_","lv_","lt_","pl_","sk_","yu_","mk_","mo_","ba_","hr_","sl_","at_","it_","ch_","lu_","nl_","uk_","ie_","es_","pt_","ru_","md_","ua_","by_","cy_","mt_","asia_");


_root.country_info._visible = false;

_root.onMouseMove = function() {
	_root.country_name._x = _root._xmouse-_root.country_name._width/2+5;
	tempy = _root._ymouse+20;
	if((tempy)>340){
		tempy -= 40;
	}
	_root.country_name._y = tempy;

	if(not(_root.country_info._visible)){
		ob = _root.country_info
		ob._x = _root._xmouse;
		ob._y = _root._ymouse;
		ob._x = Math.min(ob._x,414);
		ob._x = Math.max(ob._x,80);
		ob._y = Math.min(ob._y,272);
		ob._y = Math.max(ob._y,90);
	}
}

function colorCountry(obj, over) {
	var objstate = obj.state
	objColor = new Color(obj);
	colorTransform = new Object();

	if(over){
		colorTransform = { 
			ra: 100,
			rb: colors[objstate][0]+10,
			ga: 100,
			gb: colors[objstate][1]+10,
			ba: 100,
			bb: colors[objstate][2]+10,
			aa: 100,
			ab: 0
		};
	}else{
		colorTransform = { 
			ra: 100,
			rb: colors[objstate][0],
			ga: 100,
			gb: colors[objstate][1],
			ba: 100,
			bb: colors[objstate][2],
			aa: 100,
			ab: 0
		};
	}


	objColor.setTransform(colorTransform);
}

for(i=0;i<codes.length;i++){
	x = eval("_root.map.map0."+codes[i]);
	x.useHandCursor = false;
	x.state = -1;
	colorCountry(x,false)


	x.onRollOver = function() {
		if(this.title+" "!="undefined "){
			_root.country_name_ = this.title;
		}

		if(this.state>1){
			_root.colorCountry(this, true);
		}
	}

	x.onRollOut = function() {
		
		_root.country_name_ = "";
		if(this.state>1){
			_root.colorCountry(this, false);
		}
	}

	x.onPress = function() {
		if(this.state>1){
			_root.country_info._visible = true;
			_root.country_name_ = "";
			popWindow(this)
		}
	}
}


function popWindow(obj){
	ob = country_info.description;
	ob.htmlText  = ""
	if(obj.title        !="")ob.htmlText += "<font size='14pt' color='#ff9900'><b>"+obj.title+"</b></font><br>";
	if(obj.organisation !="")ob.htmlText += "<font size='10pt' color='#666666'><u>Organisation</u>: </font><font size='10pt' color='#666666'>"+obj.organisation+"</font><br>";
	if(obj.contact      !="")ob.htmlText += "<font size='10pt' color='#666666'><u>Contact</u>: </font><font size='10pt' color='#666666'>"+obj.contact+"</font><br>";
	if(obj.countryUrl   !="")ob.htmlText += "<font size='10pt' color='#666666'><u>URL</u>: </font><a href='"+obj.countryUrl+"'><u><font size='10pt' color='#6666cc'>"+obj.countryUrl+"</font></u></a><br>";
	if(obj.countryHost  !="")ob.htmlText += "<font size='10pt' color='#666666'><u>Host</u>: </font><font size='10pt' color='#666666'>"+obj.countryHost+"</font><br>";
	if(obj.CBDURL       !="")ob.htmlText += "<font size='10pt' color='#666666'><u>CBD URL</u>: </font><font size='10pt' color='#666666'>"+obj.CBDURL+"</font><br>";
}

country_info.x_close.onPress = function(){
	_root.country_info._visible = false;	
}