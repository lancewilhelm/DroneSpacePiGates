console.log('socket stuff is go!!!');

var lapTable = document.getElementById("lapTable");
var timingSocket = io('/timing').connect('http://' + document.domain + ':' + location.port);


timingSocket.on('connect', function() {
    timingSocket.emit('getLapList', {});
    console.log("websock connected");
});

timingSocket.on('pilot lap', function(data){
    console.log('pilot lap '+data);
    data = JSON.parse(data);
    var gate = data.gate;
    var message = data.message;
    addLapToTable(message[0],message[1],message[2]);
    blipAudio.play();
});

timingSocket.on('lap list', function(data){
    console.log(data);
    data = JSON.parse(data);
    var gate = data.gate;
    var message = data.message;
    refreshTable(message);
});

function addLapToTable(pilot, time, number){
  // Create an empty <tr> element and add it to the 1st position of the table:
  var row = lapTable.insertRow(-1);

  // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
  row.insertCell(0).innerHTML = pilot;
  row.insertCell(1).innerHTML = time;
  row.insertCell(2).innerHTML = number;
}

function clearLapTable(){
  while(lapTable.hasChildNodes())
  {
     lapTable.removeChild(lapTable.firstChild);
  }
  addLapToTable("Pilot","Time","Lap #");
}

function refreshTable(laps){
  clearLapTable()
  console.log(laps)
  for (i = 0; i < laps.length; i++){
      pilot = laps[i][0];
      time = laps[i][1];
      number = laps[i][2];
      console.log("adding laps to the table");
      addLapToTable(pilot,time,number);
  }
}

var d = new Date();
var audio = new Audio('static/sound/tone.mp3');
var blipAudio = new Audio('static/sound/blip.mp3');
var countdownTimer = 0;
var raceDuration = 120;

function resetCountdown(){
  clearInterval(countdownTimer);
  document.getElementById("timer").innerHTML = getMinutes(raceDuration*1000) + ":" + getSeconds(raceDuration*1000);
  console.log("resetting");
}

function stopCountdown() {
    clearInterval(countdownTimer);
}

function startCountdown(){
  clearInterval(countdownTimer);
  resetCountdown();
  d = new Date();
  d.setSeconds(new Date().getSeconds()+raceDuration+5);
  countdownTimer = setInterval(countdownMethod, 1000);
}

function getDays(ms) {
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

function getHours(ms) {
  return Math.floor((ms % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
}

function getMinutes(ms) {
  return Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
}

function getSeconds(ms) {
  return Math.floor((ms % (1000 * 60)) / 1000);
}

var countdownMethod = function() {

  // Get todays date and time
  var now = new Date().getTime();

  // Find the distance between now an the count down date
  var distance = d.getTime() - now;

  // Display the result in the element with id="demo"
  document.getElementById("timer").innerHTML = getMinutes(distance) + ":" + getSeconds(distance);
  // If the count down is finished, write some text
  if (distance < 0) {
    clearInterval(countdownTimer);
    document.getElementById("timer").innerHTML = "EXPIRED";
    audio.play();
  }
  if (distance <= (raceDuration+1)*1000) {
    if (distance >= raceDuration*1000) {
      audio.play();
    }
  }
}
resetCountdown();
