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
			$("#jarvis-text").text(e.data);
		};
		
		s.onerror = function (e) {
			console.log("Socket error:", e);
		};
		
	} catch (ex) {
		console.log("Socket exception:", ex);
	}

	// Chrome Speech To Text
	var final_transcript = '';
	var recognizing = false;
	var ignore_onend;
	var start_timestamp;
	if (('webkitSpeechRecognition' in window)) {
	  var recognition = new webkitSpeechRecognition();
	  
	  //Experiment with this value
	  recognition.continuous = true;
	  
	  recognition.interimResults = true;
	  recognition.lang = 'en-US';
	  recognition.start();

	  recognition.onstart = function() {
	    recognizing = true;
	    showInfo('info_speak_now');
	  };

	  recognition.onerror = function(event) {
	    if (event.error == 'no-speech') {
	      ignore_onend = true;
	    }
	    if (event.error == 'audio-capture') {
	      ignore_onend = true;
	    }
	    if (event.error == 'not-allowed') {
	      if (event.timeStamp - start_timestamp < 100) {
	        //Show an error
	      } else {
	        //Show an error
	      }
	      ignore_onend = true;
	    }
	  };

	  recognition.onend = function() {
	    recognizing = false;
	    if (ignore_onend) {
	      return;
	    }
	    if (!final_transcript) {
	      return;
	    }
	    showInfo('');
	    if (window.getSelection) {
	    }
	  };

	  recognition.onresult = function(event) {
	    var interim_transcript = '';
	    for (var i = event.resultIndex; i < event.results.length; ++i) {
	      if (event.results[i].isFinal) {
	        final_transcript += event.results[i][0].transcript;
	      } else {
	        interim_transcript += event.results[i][0].transcript;
	      }
	    }
	    $("#chrome-text").text(final_transcript);
	  };
	}
});