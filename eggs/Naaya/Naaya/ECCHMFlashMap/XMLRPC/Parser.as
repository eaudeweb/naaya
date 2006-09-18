/*////////////////////////////////////////////////////////////////////////////////////////////// 
   XMLRPC.Parser Version 0.1 (for ActionScript 2.0)
   Last Modified: 12-02-2004
   First Modified: 01-30-2004
   
   :::::::::
   
   Contact Information:
   Matt Shaw <matt@dopelogik.com>

//////////////////////////////////////////////////////////////////////////////////////////////*/

import XMLRPC.common;

class XMLRPC.Parser {
    
    private var _VERSION:String = "0.1.0";
	private var _PRODUCT:String = "XMLRPC.Parser";
    private var _TRACE_LEVEL:Number = 3;
    
	/*//////////////////////////////////////////////////////////////////////
	Parse()
	?:		Parses XML node, based on RPC spec
	IN:		XML Node from RPC Response
	OUT:	Returns UnMarshalled Object;		
 	//////////////////////////////////////////////////////////////////////*/
	 // public function Parse (node:XMLNode,val:Object):Object { 
		// DTrace("Parse(): >> " + node.nodeName,3); 
		// for (var sibNode = node; sibNode != null; sibNode=sibNode.nextSibling) {  
			// switch(sibNode.nodeName) { 
			// case "array" : DTrace("Parse(): >> Begin Array",3); 
				// return _parseXml(sibNode.firstChild,[])  
			// case "struct" : DTrace("Parse(): >> Begin Struct",3); 
				// return _parseXml(sibNode.firstChild,{})  
			// case "member" : val[sibNode.firstChild.firstChild.nodeValue]=_parseXml(sibNode.firstChild.nextSibling) 
				// DTrace("Parse(): Struct item "+sibNode.firstChild.firstChild.nodeValue + ":" + val[sibNode.firstChild.firstChild.nodeValue],3); 
				// if (sibNode.nextSibling==undefined){ 
				// DTrace("Parse(): << End Struct",3); 
				// } 
				// break; 
			// case "value" : if (sibNode.parentNode.nodeName=="data") { 
				// val.push(_parseXml(sibNode.firstChild)) 
				// DTrace("Parse(): adding data to array: "+val[val.length-1],3); 
				// if (sibNode.nextSibling==undefined){ 
				// DTrace("Parse(): << End Array",3); 
				// } 
				// } else { 
				// return _parseXml(sibNode.firstChild,val) 
				// } 
				// break;  
			// case null : return sibNode.nodeValue 
			// default : return _parseXml(sibNode.firstChild,val)  
		 
			// }  
		// } 
		// return val  
	// } 
	public function Parse(node:XMLNode):Object {
		var Data:Object;
		//trace("====================================================== "+ node);
		if (node.nodeType == 3) {
			return node.nodeValue;
		}
		if (node.nodeType == 1) {
			if ((node.nodeName == "methodResponse") || (node.nodeName == "value") || (node.nodeName == "param") || (node.nodeName == "fault") || (node.nodeName == "params") || (node.nodeName == "array")) {
				DTrace("Parse(): >> " + node.nodeName,3);
				return this.Parse(node.firstChild);
			}
			
			if (node.nodeName == "data") {
				DTrace("Parse(): >> Begin Array",3);
				Data = [];
				for (var i=0; i<node.childNodes.length;i++) {
					Data.push(this.Parse(node.childNodes[i]));
					DTrace("Parse(): adding data to array: "+Data[Data.length-1],3);
				}
				DTrace("Parse(): << End Array",3);
				return Data;
			}
			
			if (node.nodeName == "struct") {
				DTrace("Parse(): >> Begin Struct",3);
				Data = {};
				for (var i=0; i<node.childNodes.length;i++) {
					var Temp = this.Parse(node.childNodes[i]);
					Data[Temp.name]=Temp.value;
					DTrace("Parse(): Struct  item "+Temp.name + ":" + Temp.value,3);
				}
				DTrace("Parse(): << End Stuct",3);
				return Data;
			}
			
			// The member tag is *special*. The returned
			// value is *always* a hash (or in Flash-speak,
			// it is always an Object).
			if (node.nodeName == "member") {
				var Temp1;
				var Temp2;
				var Data = {};
				Temp1 = this.Parse(node.firstChild);
				Temp2 = this.Parse(node.lastChild);
				Data.name = Temp1;
				Data.value = Temp2;

				return Data;
			}
			if (node.nodeName == "name") {
				return this.Parse(node.firstChild);
			}
			//b&c 
			if (node.nodeName == "nil") {
				return null;
			}
			
			// These are the simple object data types.
			// we just want the values returned.
			if ( common.isSimpleType(node.nodeName) ) {
				return  node.firstChild.nodeValue;
			}
		}
		this.DTrace("Received an invalid Response.",1)
		return false;
	} 
	
	
	public function set Quiet(a:Boolean){
		if (a)
			this._TRACE_LEVEL=0
		else
			this._TRACE_LEVEL=3		
	}	
	
	
	/*///////////////////////////////////////////////////////////////////////
	DTrace()
	?: 	 traces to Output
	IN:  A message, level of verboseness (higher=more)
	OUT: Void
	///////////////////////////////////////////////////////////////////////*/
	private function DTrace(a,trace_level:Number):Void {
		if ( this._TRACE_LEVEL >= trace_level){
			trace(this._PRODUCT + " -> " + a);
		}
	}

}