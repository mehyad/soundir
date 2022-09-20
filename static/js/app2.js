//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; //stream from getUserMedia()
var recorder; //WebAudioRecorder object
var input; //MediaStreamAudioSourceNode  we'll be recording
var encodingType; //holds selected encoding for resulting audio (file)
var encodeAfterRecord = true; // when to encode

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record
var $timeDisplay = $('#time-display');
var $recording = $('#recording');
// var encodingTypeSelect = document.getElementById("encodingTypeSelect");
var recordButton = document.getElementById("record");
var stopButton = document.getElementById("stop");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

function startRecording() {
  console.log("startRecording() called");

  /*
		Simple constraints object, for more advanced features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/

  var constraints = { audio: true, video: false };

  /*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

  navigator.mediaDevices
    .getUserMedia(constraints)
    .then(function (stream) {
      // __log(
      //   "getUserMedia() success, stream created, initializing WebAudioRecorder..."
      // );

      /*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device

		*/
      audioContext = new AudioContext();

      //update the format
      // document.getElementById("formats").innerHTML =
      //   "Format: 2 channel " +
      //   encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value +
        // " @ " +
        // audioContext.sampleRate / 1000 +
        // "kHz";

      //assign to gumStream for later use
      gumStream = stream;

      /* use the stream */
      input = audioContext.createMediaStreamSource(stream);

      //stop the input from playing back through the speakers
      // input.connect(audioContext.destination)

      //get the encoding
      encodingType = 'wav';
        // encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value;

      //disable the encoding selector
      // encodingTypeSelect.disabled = true;

      recorder = new RecordRTC.StereoAudioRecorder()//input, {
        //workerDir: "static/js/", // must end with slash
        //encoding: encodingType,
        // numChannels: 2, //2 is the default, mp3 encoding supports only 2
        /*
        onEncoderLoading: function (recorder, encoding) {
          // show "loading encoder..." display
          __log("Loading " + encoding + " encoder...");
        },
        onEncoderLoaded: function (recorder, encoding) {
          // hide "loading encoder..." display
          __log(encoding + " encoder loaded");
        },*/
     // });

      recorder.onComplete = function (recorder, blob) {
        //__log("Encoding complete");
        createDownloadLink(blob, recorder.encoding);
        // encodingTypeSelect.disabled = false;
      };

      recorder.setOptions({
        timeLimit: 120,
        encodeAfterRecord: encodeAfterRecord,
        ogg: { quality: 0.5 },
        mp3: { bitRate: 160 },
      });
      var minSecStr = function(n) {
        return (n < 10 ? "0" : "") + n;
      };
      
      var updateDateTime = function() {
        var sec;
        sec = recorder.recordingTime() | 0;
        $timeDisplay.html("" + (minSecStr(sec / 60 | 0)) + ":" + (minSecStr(sec % 60)));
      };

      //start the recording process
      recorder.record();
      window.setInterval(updateDateTime, 200);
      //__log("Recording started");
    })
    .catch(function (err) {
      //enable the record button if getUSerMedia() fails
      recordButton.disabled = false;
      stopButton.disabled = true;
    });
  // $recording.removeClass('hidden');
  $recording.toggleClass("text-danger");
  $recording.toggleClass("text-muted");
  $recording.html('<strong>RECORDING</strong>');

  //disable the record button
  recordButton.disabled = true;
  recordButton.classList.toggle("hidden");
  stopButton.classList.toggle("hidden")
  // stopButton.classList.toggle("btn-default")
  // stopButton.classList.toggle("btn-danger")
  stopButton.disabled = false;
}

function stopRecording() {
  $recording.html('<strong>STOPPED</strong>');
  $recording.toggleClass("text-danger");
  $recording.toggleClass("text-muted");
  console.log("stopRecording() called");

  //stop microphone access
  gumStream.getAudioTracks()[0].stop();

  //disable the stop button
  stopButton.disabled = true;
  recordButton.disabled = false;
  recordButton.classList.toggle("hidden");
  stopButton.classList.toggle("hidden")

  //tell the recorder to finish the recording (stop recording + encode the recorded audio)
  recorder.stop();

  //__log("Recording stopped");
}

function createDownloadLink(blob, encoding) {
  var url = URL.createObjectURL(blob);
  var au = document.createElement("audio");
  var li = document.createElement("li");
  var link = document.createElement("a");
  var filename = new Date().toISOString();
  //add controls to the <audio> element
  au.controls = true;
  au.src = url;

  //link the a element to the blob
  link.href = url;
  link.download = filename + "." + encoding;
  link.innerHTML = link.download;

  //add the new audio and a elements to the li element
  li.appendChild(au);
  // li.appendChild(document.createTextNode(filename + "." + encoding));
  // li.appendChild(link);
  //upload link
  // var upload = document.createElement("a");
  // upload.href = "";
  // upload.innerHTML = "Upload";
  var upload = document.createElement("button");
  upload.innerHTML = "Upload";
  upload.classList.add("btn");
  upload.classList.add("btn-primary");

  upload.addEventListener("click", function (event) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function (e) {
      if (this.readyState === 4) {
        console.log("Server returned: ", e.target.responseText);
      }
    };
    var fd = new FormData();
    fd.append("audio_data", blob, filename);
    xhr.open("POST", "/record", true);
    xhr.send(fd);
    window.location.href = "/direction";
  });
  li.appendChild(document.createTextNode(" ")); //add a space in between
  li.appendChild(upload); //add the upload link to li

  //add the li element to the ordered list
  recordingsList.appendChild(li);
}

//helper function
function __log(e, data) {
  log.innerHTML += "\n" + e + " " + (data || "");
}
