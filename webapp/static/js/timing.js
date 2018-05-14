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
