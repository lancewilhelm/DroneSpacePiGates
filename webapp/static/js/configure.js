
function sendSerialCommand(command){
  origin = window.location.origin
  // gateColorURL = "{{ url_for('index') }}?color="+color
  // alert("sending POST call to "+gateColorUrl);
  var xhttp = new XMLHttpRequest();

  // event.preventDefault();
  xhttp.open("POST", "/api/server/sensors/timing/command", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("command="+command);
}

function execute(){
  var command = -1;
  var commandValue = document.getElementById('commandValue').value;

  //figure out which command we'd like to run
  var enterBubbleElement = document.getElementById('enterBubble');
  var exitBubbleElement = document.getElementById('exitBubble');
  var rssiMultiplierElement = document.getElementById('rssiMultiplier');
  var channelElement = document.getElementById('channel');
  var bandElement = document.getElementById('band');
  var testProgramElement = document.getElementById('testProgram');
  if(enterBubbleElement.checked){
    command = 11;
  }
  if(exitBubbleElement.checked){
    command = 12;
  }
  if(rssiMultiplierElement.checked){
    command = 13;
  }
  if(channelElement.checked){
    command = 14;
  }
  if(testProgramElement.checked){
    command = 15;
  }
  if(bandElement.checked){
    command = 16;
  }

  //deal with value
  if(commandValue===""){
    commandValue = 0;
  }

  //figure out which module we are talking to
  var moduleId;
  for (moduleId = 0; moduleId <= 7; moduleId++) {
    var moduleElement = document.getElementById('module'+moduleId);
    console.log('module'+moduleId);
    if(moduleElement.checked){
      sendSerialCommand("96");
      sendSerialCommand(command);
      sendSerialCommand(moduleId);
      sendSerialCommand(commandValue);
    }
  }
}
