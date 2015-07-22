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
import com.xfactorstudio.xml.xpath.XPathStep;
import com.xfactorstudio.xml.xpath.XPathAxes;
import com.xfactorstudio.xml.xpath.XPathUtils;
import com.xfactorstudio.xml.xpath.XPathPredicate;
import com.xfactorstudio.xml.xpath.XPathAxisNames;

class com.xfactorstudio.xml.xpath.XPathParser{
	static var AxisNames:XPathAxisNames = new XPathAxisNames();
	static var AxisFunctions:Array = new Array("root","ancestor","ancestorOrSelf","attribute","child","descendant","descendantOrSelf","following","followingSibling","parent","preceding","precedingSibling","self","namespace");
	var stringQuery:String;
	
	function XPathParser(context,query){
		//this.stringQuery;
		parseQuery(context,query);
		
		//AxisNames["ancestor::"] = 1;
		//AxisNames["ancestor-or-self::"] = 2;
		//AxisNames["attribute::"] = 3;
		//AxisNames["@"] = 3;
		//AxisNames["child::"] = 4;
		//AxisNames["descendant::"] = 5;
		//AxisNames["descendant-or-self::"] = 6;
		//AxisNames["//"] = 6;
		//AxisNames["following::"] = 7;
		//AxisNames["following-sibling::"] = 8;
		//AxisNames["parent::"] = 9;
		//AxisNames[".."] = 9;
		//AxisNames["preceding::"] = 10;
		//AxisNames["preceding-sibling::"] = 11;
		//AxisNames["self::"] = 12;
		//AxisNames["."] = 12;
		//AxisNames["namespace::"] = 13;
		
	}
	
	
		

	
	
	
	static function parseQuery(context:XMLNode,query:String):Array{
		//var startTime = getTimer();
		var steps = new Array();
		var collChars = "";
		var c;
		//var currAxis = XPathParser.AxisNames["child::"];
		var currAxis = null;
		var currPredicate = null;
		
		//var start = getTimer();
		
		for(var i=0;i<query.length;i++){
			if(query.charCodeAt(i) < 33){
				continue;
			}
			c = query.charAt(i);	
			switch(c){
				case "/": //end of path step || root || descendant-or-self
					if(query.charAt(i+1) != "/" && query.charAt(i-1) != "/"){ //end of path step || root
						if(steps.length == 0 && currAxis == null){
							//steps.push({axis:0, text:"*", predicate:undefined});
							steps.push(new XPathStep(0, "*", null));
						}else{
							//steps.push({axis:currAxis, text:collChars, predicate:currPredicate});
							steps.push(new XPathStep(currAxis, collChars, currPredicate));
							//trace(">> " + collChars);
							currPredicate = null;
							currAxis = null;
							collChars = "";
						}
					}else{//descendant-or-self, weird case handled outside of axis change grabber below, should revisit this code
						/**
						if(i!=0){
							//steps.push({axis:currAxis, text:collChars, predicate:currPredicate});
							steps.push(new XPathStep(currAxis, collChars, currPredicate));
							currPredicate = null;
							//currAxis = XPathParser.AxisNames["child::"];
							currAxis = null;
							collChars = "";
						}
						**/
						steps.push(new XPathStep(XPathParser.AxisNames["descendant-or-self::"], "*", null));
						currPredicate = null;
						currAxis = null;
						collChars = "";
						i++;
						
					}
					break;				
				case "[": //beginning of a test
					if(currPredicate == null){										
						var innerNestCount = 0;
						var foundMatching = false;
						while(i<query.length && !foundMatching){
							if(query.charAt(i) == "["){
								innerNestCount++;
							}
							if(query.charAt(i) == "]"){
								innerNestCount--;
								if(innerNestCount == 0){
									foundMatching = true;
								}
							}
							currPredicate = (currPredicate==null)? query.charAt(i) : (currPredicate + query.charAt(i));
							i++;
						}
						i--;
						break;
					}else{ //this only allows one predicate
						return;
					}
				default:
					collChars = (collChars==null)? c : collChars+c;
					break;
			}
			
			//look for axis changes
			if(XPathParser.AxisNames[collChars] != null){
				if(query.charAt(i+1) != "."){ // make sure this is . and not the start of ..
					currAxis = XPathParser.AxisNames[collChars];
					collChars = "";
				}
			}
		}
		
			if(steps[steps.length-1].axis == 0){
				collChars = "*";
			}
			steps.push(new XPathStep(currAxis, collChars, currPredicate));
			//trace(new XPathStep(currAxis, collChars, currPredicate).toString());
	
		return XPathParser.processSteps(context,steps);
	}
	
	static function processSteps(context,steps:Array):Array{
		if(context instanceof XML)
			context = XPathAxes.root(context);
		if(context instanceof XMLNode)
			context = new Array(context);
		
		var axis,text,predicate;
		var results = new Array();
	
		for(var i=0;i<steps.length;i++){
			//trace(steps[i].toString());
			axis = steps[i].axis;
			text = steps[i].text;
			predicate = steps[i].predicate;
			
			if((axis == XPathParser.AxisNames["self::"]||axis == XPathParser.AxisNames["parent::"]||XPathParser.AxisNames["text()"]) && text.length==0){
				text = "*";
			}
			if(axis == null){
				axis = XPathParser.AxisNames["child::"]
			}

			context = XPathParser.processStep(XPathAxes[XPathParser.AxisFunctions[axis]],context,text);
			// run test for each step
			if(predicate != null){
				context = XPathParser.runTest(context,predicate);
			}
		}
		
		
		
		for(var j=0;j<context.length;j++){
			results.push(context[j]);
		}
		return results;
	}
	
	static function processStep(axisFunction,context,name):Array{
		var retVal = new Array();
		for(var i=0;i<context.length;i++){
			XPathUtils.appendArray(retVal,XPath.getNamedNodes(axisFunction.call(XPathParser,context[i]),name));
		}
		return retVal;
	}
	
	
	
	
	static function runTest(context:Array, test:String):Array{
		test = test.substr(1,test.length-2);
		var childIndex;
		var nodeArray = new Array();
		var steps = XPathPredicate.parse(test);
		
		for(var i=0;i<context.length;i++){
			//childIndex = XPathParser.getChildIndex(context[i]);
			//if(XPathPredicate.test(context[i],test,context,childIndex,XPathUtils.cloneArray(steps))){
			if(XPathPredicate.test(context[i],test,context,XPathUtils.cloneArray(steps))){
				nodeArray.push(context[i]);
			}
		}
		return nodeArray;
	}
	
	static function getChildIndex(kid:XMLNode):Number{
		var bros = kid.parentNode.childNodes;
		var sibCount = 0;
		
		for(var i=0;i<bros.length;i++){
			if(bros[i].nodeName == kid.nodeName){
				sibCount++;
			}
			if(bros[i] === kid){
				return sibCount;
			}
		}
		return 0;
	}
}

