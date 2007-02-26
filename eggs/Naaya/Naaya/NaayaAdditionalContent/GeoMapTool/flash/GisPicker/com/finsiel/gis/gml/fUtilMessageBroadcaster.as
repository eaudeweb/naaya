/* Class: com.finsiel.gis.gml.fUtilMessageBroadcaster

Unique event diaptcher and broadcaster for gml entities

based on: http://www.gskinner.com/blog/archives/000023.html

we have to declare the dispatchEvent,
addEventListener and removeEventListener
methods that EventDispatcher sets up:

Parameters:

p_msgobj - {obj:object_wich_sent_the_message,typ:message_type}

   Returns:

Nothing	

Functions:

addEventListener - Macromedia Flash event listener
removeEventListener - Macromedia Flash event listener
dispatchEvent - Macromedia Flash event dispatcher
fUtilMessageBroadcaster - set instances up as dispatchers
sendMessage - sent the message (set up the event object and dispatch the event)

*/
//import mx.events.EventDispatc;
class com.finsiel.gis.gml.fUtilMessageBroadcaster {
	function dispatchEvent() {
	}
	function addEventListener() {
	}
	function removeEventListener() {
	}
	function fUtilMessageBroadcaster() {
		mx.events.EventDispatcher.initialize(this);
	}
	function sendMessage(p_msgobj:Object):Void {
		var eventObj:Object = {target:this, type:"message"};
		eventObj.msgobj = p_msgobj;
		dispatchEvent(eventObj);
	}
}
