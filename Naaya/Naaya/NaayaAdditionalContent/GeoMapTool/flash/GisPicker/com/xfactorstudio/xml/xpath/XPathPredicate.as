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
import com.xfactorstudio.xml.xpath.XPathFunctions;
import com.xfactorstudio.xml.xpath.XPathPredicateLogical;
import com.xfactorstudio.xml.xpath.XPathPredicateOperator;
import com.xfactorstudio.xml.xpath.XPathPredicateOperatorName;

class com.xfactorstudio.xml.xpath.XPathPredicate{
	static var Logical = new XPathPredicateLogical();
	static var Operator = new XPathPredicateOperator();
	static var OperatorName = new XPathPredicateOperatorName();

	//TODO: WTF? Move the types to the types
	//object as I apperantly intended
	static var types = new Object();
	static var operatorType = 0;
	static var funcType = 1;
	static var queryType = 2;
	static var numberType = 3;
	static var stringType = 4;
	static var booleanType = 5;
	static var logicalType = 6;
	static var groupingType = 7;
	
	private function XPathPredicate(){
	}
	
	
	
	
	
	
	/**
		 evaluate
	
		 parses the predicate expression and returns the evaluated value
		 
		 @param (XMLNode)context the context node
		 @param (String)expr the XPath predicate expression
				that's the stuff in the []
		 @param (Array)nodeSet the nodeSet from the previous 
				selection, contains the context node
		 @param (Number)contextPosition the position of the 
				context node in the nodeSet NOTE: position is 
				not the same as array index, it is index+1
		 @return the evaluated value of the expression [Number | Boolean | NodeSet | String]
	**/
	static function evaluate(context:XMLNode, expr:String, nodeSet:Array, steps:Array):Array{
		//trace("PREDICATE ----------------");
		
		//for(var i=0;i<steps.length;i++){
			//trace(steps[i].type + " " + steps[i].value);
		//}
		
		var contextSize = nodeSet.length;
		var result;
		var args;
	
	
		for(var i=0;i<steps.length;i++){
			switch(steps[i].type){
				case XPathPredicate.funcType:
					//TODO see if you can make this line any freakin longer
					steps[i] = XPathFunctions[XPathFunctions.Names[XPathFunctions.Tokens[steps[i].value]]].call(XPathPredicate,XPathFunctions.parseArgs(steps[i].data,context),context,nodeSet);
					break;
				case XPathPredicate.queryType:
					steps[i] = XPath.selectNodes(context,steps[i].value);
					break;
				case XPathPredicate.stringType:
					steps[i] = steps[i].value;
					break;
				case XPathPredicate.numberType:
					steps[i] = Number(steps[i].value);
					break;
				case XPathPredicate.groupingType:
					var subSteps = XPathPredicate.parse(steps[i].value);
					steps[i] = XPathPredicate.evaluate(context, null, nodeSet, subSteps);
					break;				
			}
		}
		return XPathPredicate.solve(steps);
	}
	
	/**
		 parse
	
		takes an expression and returns an array of the parsed steps
	**/
	static function parse(expr:String):Array{
		var result;
		var args;
		var collChars = "";
		var steps = new Array();
		var c,j,i;
		//trace(expr);
		
		for(var i=0;i<expr.length;i++){
			c = expr.charAt(i);
		
			//consume whitespace
			while(c == " " && i < expr.length){			
				i++;
				c = expr.charAt(i);
				//trace("leaving with " + c);
			}
			
			//trace(">>"+c);
			switch(c){
				//case " ":
				//	break;
				//catch string litterals
				case "'":
				case "\"": 
					i++; //kill qoute
					j=i;
					while(expr.charAt(j) != '"' && expr.charAt(j) != "'" && j<expr.length){
						j++;
					}
					collChars = expr.substr(i,j-i);
					i=j;
					steps.push({type:XPathPredicate.stringType, value:collChars , data:undefined});
					break;
				//catch operators
				case "(": //grouping
					i++; //kill (
					j=i;
					var innerNestCount = 1;
					var foundMatching = false;
					while(j<expr.length && !foundMatching){
						if(expr.charAt(j) == "("){
							innerNestCount++;
						}
						if(expr.charAt(j) == ")"){
							innerNestCount--;
							if(innerNestCount == 0){
								foundMatching = true;
								break;
							}
						}
						
						j++;
					}
	
					collChars = expr.substr(i,j-i);
					i=j;
					steps.push({type:XPathPredicate.groupingType, value:collChars , data:undefined});
					break;
				case "+":
				case "-":
				case "*":
				case "=":
					//trace("= " + c);
					steps.push({type:XPathPredicate.operatorType, value:c , data:undefined});
					break;
				case "!":
				case "<":
				case ">":
					if(expr.charAt(i+1) == "="){
						steps.push({type:XPathPredicate.operatorType, value:c+"=" , data:undefined});
						i++;
					}else{
						steps.push({type:XPathPredicate.operatorType, value:c, data:undefined});
					}
					break;
				default:
					//trace("default "+  c);
					//catch numbers
					if(!isNaN(c)){ //handle numbers
						j=i;
						while(!isNaN(expr.charAt(j)) && j<expr.length){
							j++;
						}
						steps.push({type:XPathPredicate.numberType, value:expr.substr(i,j-i) , data:undefined});
						j--;
						i=j;
					//catch xpaths and functions
					}else{ 
						collChars = "";
						j=i;
						
						while(expr.charAt(j) != " " && j<expr.length &&
								(XPathPredicate.Operator[expr.charAt(j)] == null || expr.charAt(j) == "-")&&
								XPathFunctions.Tokens[collChars] == null && 
								XPathPredicate.Logical[collChars] == null &&
								XPathPredicate.OperatorName[collChars] == null){
								
								if(expr.charAt(j) == "["){ //we are now sure this is an XPath
									var innerNestCount = 1;
									var foundMatching = false;
									while(j<expr.length && !foundMatching){
										if(expr.charAt(j) == "["){
											innerNestCount++;
										}
										if(expr.charAt(j) == "]"){
											innerNestCount--;
											if(innerNestCount == 0){
												foundMatching = true;
											}
										}
										
										collChars += expr.charAt(j);
										j++;
									}
									i=j;
	
								} else{
									//trace("collChars = " + collChars);
									collChars += expr.charAt(j);
									j++;
								}
							
						}
						j--;
						i=j;
						//trace(collChars);
						if(XPathFunctions.Tokens[collChars] != null){
							//collect args
							var args = "";
							while(i<expr.length && expr.charAt(i) != ")"){
								i++;
								args += expr.charAt(i);
							}
							args = args.substr(0,args.length-1);
							steps.push({type:XPathPredicate.funcType , value:collChars , data:args});
						}else if(XPathPredicate.Logical[collChars] != null){
							steps.push({type:XPathPredicate.operatorType , value:collChars , data:args});
						}else if(XPathPredicate.OperatorName[collChars] != null){ // mod & div
							steps.push({type:XPathPredicate.operatorType, value:collChars, data:undefined});
						}else{					
							steps.push({type:XPathPredicate.queryType, value:collChars , data:undefined});
						}
							
					}
					break;
			}
			
		}
		//leave for debugging
		//trace("[");
		//for(var i=0;i<steps.length;i++){
		//	trace("step =  " + steps[i].value);
		//}
	
		return steps;
	}
	
	/**
		 test
	
		 takes the evaluated value of a predicate expression
		 returned from evaluate and returns a boolean based 
		 on its value. 
		 true = node included, false = node not included
		 
		@param (XMLNode)context the context node
		@param (String)expr the XPath predicate expression
			that's the stuff in the []
		@param (Array)nodeSet the nodeSet from the previous 
			selection, contains the context node
		@param (Number)contextPosition the position of the 
			context node in the nodeSet NOTE: position is 
			not the same as array index, it is index+1
		@return the evaluated value of the expression as a boolean
	**/
	static function test(context:XMLNode, expr:String, nodeSet:Array, steps:Array):Boolean{
		
		// already evaluates to a number no point running it throught
		// the evaluate process just return the bollena val now
		if(!isNaN(expr)){
			return (expr == XPathParser.getChildIndex(context))? true : false;
		}
		
		//var steps = XPathPredicate.parse(context, expr, nodeSet, contextPosition);
		var result = XPathPredicate.evaluate(context, expr, nodeSet,steps);	
		//evaluate any numerical result to boolean
		if(typeof(result) == "number"){
			return (result == XPathParser.getChildIndex(context))? true : false;
		}
		
		return XPathFunctions.toBoolean(result);
	}
	
	static function solve(steps:Array):Array{
		XPathPredicate.solveMultiplicativeExpressions(steps);
		XPathPredicate.solveAdditiveExpressions(steps);
		XPathPredicate.solveRelationalExpressions(steps);
		XPathPredicate.solveEqualityExpressions(steps);
		XPathPredicate.solveLogicalAndExpressions(steps);
		XPathPredicate.solveLogicalOrExpressions(steps);
		// by the time the steps get here, there should only be one element,
		// the value of the expression, so we just return [0]. This feels weak, should test
		return steps[0];
	}
	
	static function solveMultiplicativeExpressions(steps:Array){
		for(var i=0;i<steps.length;i++){
			switch(steps[i].value){
				case "*":
					steps.splice(i-1,3,Number(steps[i-1]) * Number(steps[i+1]));
					i=i-2;
					break;
				case "mod":
					steps.splice(i-1,3,Number(steps[i-1]) % Number(steps[i+1]));
					i=i-2;
					break;
				case "div":
					steps.splice(i-1,3,Number(steps[i-1]) / Number(steps[i+1]));
					i=i-2;
					break;
			}
		}
	}
	
	static function solveAdditiveExpressions(steps:Array){
		for(var i=0;i<steps.length;i++){
			switch(steps[i].value){
				case "+":
					steps.splice(i-1,3,Number(steps[i-1]) + Number(steps[i+1]));
					i=i-2;
					break;
				case "-":
					steps.splice(i-1,3,Number(steps[i-1]) - Number(steps[i+1]));
					i=i-2;
					break;
			}
		}
	}
	
	static function solveLogicalAndExpressions(steps:Array){
		
		for(var i=0;i<steps.length;i++){
			if(steps[i].value == "and"){
				var result = (XPathPredicate.isTrue(steps[i-1]) && XPathPredicate.isTrue(steps[i+1]))? true : false;
					steps.splice(i-1,3,result);
					i=i-2;
			}
		}
	}
	
	static function solveLogicalOrExpressions(steps:Array){
		for(var i=0;i<steps.length;i++){
			if(steps[i].value == "or"){
				var result = (XPathPredicate.isTrue(steps[i-1]) || XPathPredicate.isTrue(steps[i+1]))? true : false;
					steps.splice(i-1,3,result);
					i=i-2;
			}
		}
	}
	
	static function solveRelationalExpressions(steps:Array){
		for(var i=0;i<steps.length;i++){
			switch(steps[i].value){
				case ">":
					steps.splice(i-1,3,XPathPredicate.isGreaterThan(steps[i-1],steps[i+1]));
					i=i-2;
					break;
				case "<":
					steps.splice(i-1,3,XPathPredicate.isLessThan(steps[i-1],steps[i+1]));
					i=i-2;
					break;
				case ">=":
					steps.splice(i-1,3,XPathPredicate.isGreaterThanOrEqualTo(steps[i-1],steps[i+1]));
					i=i-2;
					break;
				case "<=":
					steps.splice(i-1,3,XPathPredicate.isLessThanOrEqualTo(steps[i-1],steps[i+1]));
					i=i-2;
					break;
			}
		}
	}
	
	static function solveEqualityExpressions(steps:Array){
		for(var i=0;i<steps.length;i++){
			switch(steps[i].value){
				case "=":
					steps.splice(i-1,3,XPathPredicate.isEqualTo(steps[i-1],steps[i+1]));
					i=i-2;
					break;
				case "!=":
					steps.splice(i-1,3,XPathPredicate.isNotEqualTo(steps[i-1],steps[i+1]));
					i=i-2;
					break;
			}
		}
	}
	
	/**
		Equality Expressions
	**/
	static function isEqualTo(val1, val2):Boolean{
		var values = XPathPredicate.convertForComparison(val1, val2);
		return (values.val1 == values.val2);
	}
	static function isNotEqualTo(val1, val2):Boolean{
		var values = XPathPredicate.convertForComparison(val1, val2);
		return (values.val1 != values.val2);
	}
	/**
		Relational Expressions
	**/
	static function isGreaterThan(val1, val2):Boolean{
		var values = XPathPredicate.convertForComparison(val1, val2);
		return (values.val1 > values.val2);
	}
	
	static function isLessThan(val1, val2):Boolean{
		var values = XPathPredicate.convertForComparison(val1, val2);
		return (values.val1 < values.val2);
	}
	
	static function isGreaterThanOrEqualTo(val1, val2):Boolean{
		var values = XPathPredicate.convertForComparison(val1, val2);
		return (values.val1 >= values.val2);
	}
	static function isLessThanOrEqualTo(val1, val2):Boolean{
		var values = XPathPredicate.convertForComparison(val1, val2);
		return (values.val1 <= values.val2);
	}
	
	static function convertForComparison(val1,val2):Object{
		var tv1,tv2;
		tv1 = typeof(val1)
		tv2 = typeof(val2)
		if(tv1 == "boolean" || tv2 == "boolean"){
			val1 = XPathFunctions.toBoolean(val1);
			val2 = XPathFunctions.toBoolean(val2);
			return {val1:val1,val2:val2};
		}
		
		if(tv1 == "number" || tv2 == "number"){
			val1 = XPathFunctions.toNumber(val1);
			val2 = XPathFunctions.toNumber(val2);
			return {val1:val1,val2:val2};
		}
		
		if(tv1 == "string"|| tv2 == "string"){
			val1 = XPathFunctions.toString(val1);
			val2 = XPathFunctions.toString(val2);
			return {val1:val1,val2:val2};
		}
		
		return {val1:val1,val2:val2};
	}
	
	static function isTrue(test):Boolean{
		return XPathFunctions.toBoolean(test);
		
	}

}