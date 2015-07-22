class com.finsiel.gis.gml.fGmlStyle {
	private var _stHref:String;
	private var _stShape:String;
	private var _stWidth:Number;
	private var _stHeight:Number;
	private var _stColor:Number;
	private var _stOutlineColor:Number;
	private var _stOutlineWidth:Number;
	private var _stOutlineStyle:Number;
	private var _stAlpha:Number;
	private var _stFilter:Object;
	function fGmlStyle() {
	}
	
	function get stShape() {
		return (this._stShape);
	}
	function set stShape(str:String) {
		this._stShape = str;
	}
	//---
	function get stWidth() {
		return (this._stWidth);
	}
	function set stWidth(str:Number) {
		this._stWidth = str;
	}
	//--
	function get stHeight() {
		return (this._stHeight);
	}
	function set stHeight(str:Number) {
		this._stHeight = str;
	}
	//
	function get stColor() {
		return (this._stColor);
	}
	function set stColor(str:Number) {
		this._stColor = str;
	}
	//---
	function get stOutlineColor() {
		return (this._stOutlineColor);
	}
	function set stOutlineColor(str:Number) {
		this._stOutlineColor = str;
	}
	//---
	function get stOutlineStyle() {
		return (this._stOutlineStyle);
	}
	function set stOutlineStyle(str:Number) {
		this._stOutlineStyle = str;
	}
	//---
	function get stOutlineWidth() {
		return (this._stOutlineWidth);
	}
	function set stOutlineWidth(str:Number) {
		this._stOutlineWidth = str;
	}
	//---
	function get stAlpha() {
		return (this._stAlpha);
	}
	function set stAlpha(str:Number) {
		this._stAlpha = str;
	}
	//---
	function get stFilter() {
		return (this._stFilter);
	}
	function set stFilter(str:Object) {
		this._stFilter = str;
	}
	//
		//---
	function get stHref() {
		return (this._stHref);
	}
	function set stHref(str:String) {
		this._stHref = str;
	}

}
