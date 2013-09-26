$(document).ready(function(){
	try {
		var host = "ws://" + window.location.hostname + ":8090";
		console.log("Host:", host);
		
		var s = new WebSocket(host);
		
		s.onopen = function (e) {
			console.log("Socket opened.");
		};
		
		s.onclose = function (e) {
			console.log("Socket closed.");
		};
		
		s.onmessage = function (e) {
			console.log("Socket message:", e.data);
			$("#jarvis-text").text(e.data).hide().fadeIn(500);
		};
		
		s.onerror = function (e) {
			console.log("Socket error:", e);
		};
		
	} catch (ex) {
		console.log("Socket exception:", ex);
	}
});