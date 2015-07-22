/* Class: com.finsiel.gis.gml.fUtilTrim

   Remove blank spaces from a string start, end
  
   based on: Federico:: federico@infogravity.net

   Parameters:

      st - string to be trimmed

   Returns:

      Trimmed string

*/
class com.finsiel.gis.gml.fUtilTrim {
	/* Function: LTrim
	
	   Remove blank spaces from a string start
	
	   Parameters:
	
	      st - string to be trimmed
	
	   Returns:
	
	      Trimmed string
	
	*/
	public function LTrim(st) {
		var s = st.toString();
		var i = 0;
		while (s.charCodeAt(i) == 32 || s.charCodeAt(i) == 13 || s.charCodeAt(i) == 10 || s.charCodeAt(i) == 9) {
			i++;
		}
		return (st.substring(i, st.length));
	}
	/* Function: RTrim
	
	   Remove blank spaces from a string end
	
	   Parameters:
	
	      st - string to be trimmed
	
	   Returns:
	
	      Trimmed string
	
	*/
	public function RTrim(st) {
		var s = st.toString();
		var i = st.length-1;
		while (s.charCodeAt(i) == 32 || s.charCodeAt(i) == 13 || s.charCodeAt(i) == 10 || s.charCodeAt(i) == 9) {
			i--;
		}
		return (s.substring(0, i+1));
	}
	/* Function: LRtrim
	
	   Remove blank spaces both from a string and end
	
	   Parameters:
	
	      st - string to be trimmed
	
	   Returns:
	
	      Trimmed string
	
	*/
	public function LRtrim(s) {
		return RTrim(LTrim(s.toString()));
	}
}
