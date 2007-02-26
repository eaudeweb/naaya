/**
	Copyright (c) 2002 Neeld Tanksley.  All rights reserved.
	
	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are met:
	
	1. Redistributions of source code must retain the above copyright notice,
	this list of conditions and the following disclaimer.
	
	2. Redistributions in binary form must reproduce the above copyright notice,
	this list of conditions and the following disclaimer in the documentation
	and/or other materials provided with the distribution.
	
	3. The end-user documentation included with the redistribution, if any, must
	include the following acknowledgment:
	
	"This product includes software developed by Neeld Tanksley
	(http://xfactorstudio.com)."
	
	Alternately, this acknowledgment may appear in the software itself, if and
	wherever such third-party acknowledgments normally appear.
	
	4. The name Neeld Tanksley must not be used to endorse or promote products 
	derived from this software without prior written permission. For written 
	permission, please contact neeld@xfactorstudio.com.
	
	THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
	INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
	FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL NEELD TANKSLEY
	BE LIABLE FOR ANY DIRECT, INDIRECT,	INCIDENTAL, SPECIAL, EXEMPLARY, OR 
	CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
	GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
	HOWEVER CAUSED AND ON ANY THEORY OF	LIABILITY, WHETHER IN CONTRACT, STRICT 
	LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
	OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
**/

import com.xfactorstudio.xml.xpath.XPath;
import com.xfactorstudio.xml.xpath.XPathParser;
import com.xfactorstudio.xml.xpath.XPathAxes;
import com.xfactorstudio.xml.xpath.XPathFunctionNames;

class com.xfactorstudio.xml.xpath.XPathFunctions{
	//TODO: Why the heck am I looking up the 
	//value from the array and not just getting the string
	//function name directly?? Was I thinking speed? is there a difference?
	static var Tokens = new XPathFunctionNames();
	static var Names = [
		"null",
		"last",
		"position",
		"count",
		"id",
		"name",
		"string",
		"concat",
		"startsWith",
		"contains",
		"substringBefore",
		"substringAfter",
		"substring",
		"stringLength",
		"normalizeSpace",
		"translate",
		"boolean",
		"Not",
		"True",
		"False",
		"lang",
		"number",
		"sum",
		"floor",
		"ceiling",
		"normalizeSpace",
		"round",
		"localName",
		"namespaceURI"
		]
	
	private function XPathFunctions(){
	
	}

	
	
	
	
	
	///////////////////////////////////////////////
	//
	//     XPath functions
	//
	//     XPath supports a limited number of functions
	//     These are the equivilent functions in AS
	//
	//     Because these functions are called automatically by the 
	//     expression parser, each function is passed the same four 
	//     arguments. args is an array containg the user supplied 
	//     arguments, context is the current context XMLNode, nodeSet 
	//     is the current nodeSet that contains the contextNode, 
	//     
	//
	//////////////////////////////////////////////
	static function parseArgs(args:Array,context:XMLNode,nodeSet:Array){
		
		var argArray = new Array();
		var collChars = "";
		var c,j;
		for(var i=0;i<args.length;i++){
			c = args.charAt(i);
			switch(c){
				case "'":
				case "\"":
					i++; //kill quote
					j=i;
					while(args.charAt(j) != '"' && args.charAt(j) != "'" && j<args.length){
						j++;
					}
					collChars = args.substr(i,j-i);
					argArray.push(collChars);
					collChars = "";
					i=j;
					break;
				case ",":
					if(collChars != ""){
						if(isNaN(collChars)){
							argArray.push(XPath.selectNodes(context,collChars));
						}else{
							argArray.push(collChars);
						}
						
					}
					collChars = "";
					break;
				case " ":
					break;
				default:
					collChars += c;
					break;
			}
		}
		
		if(collChars != ""){
			if(isNaN(collChars)){
				argArray.push(XPath.selectNodes(context,collChars));
			}else{
				argArray.push(collChars);
			}
		}
	
		return argArray;
	}
	
	//////////////////////
	// Node Set Functions
	//////////////////////
	static function last(args:Array,context:XMLNode,nodeSet:Array){
		return Number(nodeSet.length);
	}
	static function position(args:Array,context:XMLNode,nodeSet:Array){
		return XPathParser.getChildIndex(context);
	}
	static function count(args:Array,context:XMLNode,nodeSet:Array){
		return args[0].length;
	}
	static function id(args:Array,context:XMLNode,nodeSet:Array){
		//not implemented
	}
	static function name(args:Array,context:XMLNode,nodeSet:Array){
		var targetNode = (args.length == 0)? context : args[0][0];
		return targetNode.nodeName;
	}
	static function localName(args:Array,context:XMLNode,nodeSet:Array){
		var targetNode = (args.length == 0)? context : args[0][0];
		return targetNode.nodeName.split(":")[1];
	}
	static function namespaceURI(args:Array,context:XMLNode,nodeSet:Array){
		var targetNode = (args.length == 0)? context : args[0][0];
		var prefix = targetNode.nodeName.split(":")[0];
		var inScopeNS = XPathAxes.namespace(targetNode);
		for(var i=0;i<inScopeNS.length;i++){
			if(XPathFunctions.localName([[inScopeNS[i]]]) == prefix){
				return inScopeNS[i].nodeValue;
			}
		}
		
	}
	//////////////////////
	// String Functions
	//////////////////////
	static function toString(args){
		if(args instanceof Array){
			args = XPathAxes.stringValue(args[0]).join("");
		}
		return String(args);
	}
	static function string(args:Array,context:XMLNode,nodeSet:Array){
		return XPathFunctions.toString(args[0]);
	}
	
	static function concat(args:Array,context:XMLNode,nodeSet:Array){
		for(var i=0;i<args.length;i++){
			args[i] = XPathFunctions.toString(args[i]);
		}
		return args.join("");
	}
	static function startsWith(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toString(args[0]);
		args[1] = XPathFunctions.toString(args[1]);
		//trace(args[0]);
		//trace(args[1]);
		return (args[0].substr(0,args[1].length) == args[1])? true : false;
	}
	static function contains(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toString(args[0]);
		args[1] = XPathFunctions.toString(args[1]);
		return (args[0].indexOf(args[1]) != -1)? true : false;
	}
	static function substringBefore(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toString(args[0]);
		args[1] = XPathFunctions.toString(args[1]);
		return args[0].substr(0,args[0].indexOf(args[1]));
	}
	static function substringAfter(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toString(args[0]);
		args[1] = XPathFunctions.toString(args[1]);
		return args[0].substr(args[0].indexOf(args[1])+args[1].length,args[0].length);
	}
	static function substring(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toString(args[0]);
		args[1] = XPathFunctions.toString(args[1]);
		return args[0].substr(args[1]-1,Math.min(args[2],args[0].length));
	}
	static function stringLength(args:Array,context:XMLNode,nodeSet:Array){
		args = XPathFunctions.toString(args[0]);
		return (args != null)? args.length : XPathAxes.stringValue(context).length;
	}
	static function normalizeSpace(args:Array,context:XMLNode,nodeSet:Array){
		args = XPathFunctions.toString(args[0]);
		var i,s
		for(i=0;i<args.length;i++){
			if(args.charCodeAt(i) < 33){
				s=i;
				while(args.charCodeAt(s) < 33){
					s++;
				}
				if(s > i+1){
					args = args.split(args.substr(i,s-i)).join(" ");
				}
			}
		}
		//leading
		i=0;
		while(args.charCodeAt(i) < 33){
			i++;
		}
		args = args.substr(i,args.length);
		//trailing
		i=args.length-1;
		while(args.charCodeAt(i) < 33){
			i--;
		}
		args = args.substr(0,i+1);
		return args;
	}
	static function translate(context,nodeSet,args){
		//not implemented
	}
	//}
		
		
		
	//////////////////////
	// Number Functions
	//////////////////////
	static function toNumber(args:Array){
		//return XPathFunctions.number([args]);
		if(args instanceof Array){
			args = XPathFunctions.toString(args);
		}
		switch(typeof(args)){
			case "string":
				return Number(args);
			case "boolean":
				return (args)? 1 : 0;
			default:
				return args;
		}
		/**
		if(typeof(args) == "string"){
			return Number(args);
		}
		if(typeof(args) == "boolean"){
			return (args)? 1 : 0;
		}
		
		return args;
		**/
	}
	static function number(args:Array,context:XMLNode,nodeSet:Array){
		return XPathFunctions.toNumber(args[0]);
	}
	static function sum(args:Array,context:XMLNode,nodeSet:Array){
		//args = args[0];
		var total = 0;
		for(var i=0;i<args[0].length;i++){
			total += Number(XPathAxes.stringValue(args[0][i])[0]);
		}
		return total;
	}
	static function floor(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toNumber(args[0]);
		return Math.floor(Number(args[0]));
	}
	static function ceiling(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toNumber(args[0]);
		return Math.ceil(Number(args[0]));
	}
	static function round(args:Array,context:XMLNode,nodeSet:Array){
		args[0] = XPathFunctions.toNumber(args[0]);
		return Math.round(Number(args[0]));
	}
	
	
	//////////////////////
	// Boolean Functions
	//////////////////////
	static function toBoolean(args){
		return XPathFunctions.boolean([args]);
	}
	
	static function boolean(args:Array,context:XMLNode,nodeSet:Array){
		args = args[0];	
		if(args instanceof Array){
			return (args.length > 0)? true : false;
		}
		switch(typeof(args)){
			case "number":
				return (args != 0)? true : false;
			case "string":
				return (args.length > 0)? true : false;
			default:
				return args;
		}
		/**
		if(typeof(args) == "number"){
			return (args != 0)? true : false;
		}
		if(typeof(args) == "string"){
			return (args.length > 0)? true : false;
		}
		return args;
		**/
	}
	static function Not(args:Array,context:XMLNode,nodeSet:Array){
		args = args[0];
		if(args == "false" || args == false){
			return true;
		}else{
			return false;
		}
	}
	static function True(args:Array,context:XMLNode,nodeSet:Array){
		return true;
	}
	static function False(args:Array,context:XMLNode,nodeSet:Array){
		return false;
	}
	static function lang(args:Array,context:XMLNode,nodeSet:Array){
		//not implemented
	}
}
