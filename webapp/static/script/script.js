function setAllGateColors(color){
  origin = window.location.origin
  // gateColorURL = "{{ url_for('index') }}?color="+color
  // alert("sending POST call to "+gateColorUrl);
  var xhttp = new XMLHttpRequest();
  // event.preventDefault();
  //xhttp.open("POST", "{{ url_for('index')}}", true);
  xhttp.open("POST", "/api/gates/color", true);

  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("color="+color+"&gateID=all");
}

function sendElementCommand(command){
  origin = window.location.origin
  // gateColorURL = "{{ url_for('index') }}?color="+color
  // alert("sending POST call to "+gateColorUrl);
  var xhttp = new XMLHttpRequest();
  // event.preventDefault();
  xhttp.open("POST", "/api/gates/system", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("command="+command+"&gateID=all");
}

function getGateList(){
  origin = window.location.origin
  // gateColorURL = "{{ url_for('index') }}?color="+color
  // alert("sending POST call to "+gateColorUrl);
  var xhttp = new XMLHttpRequest();
  // event.preventDefault();
  xhttp.open("GET", "/api/server/gates", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("");
}

// Get the modal
var updateModal = document.getElementById('updateModal');
var powerModal = document.getElementById('powerModal');

// Get the button that opens the modal
var updateBtn = document.getElementById("updateBtn");
var powerBtn = document.getElementById("powerBtn");

// Get the <span> element that closes the modal
var updateSpan = document.getElementsByClassName("close")[0];
var powerSpan = document.getElementsByClassName("close")[1];

var updatenoBtn = document.getElementsByClassName("no")[0];
var powernoBtn = document.getElementsByClassName("no")[1];

// When the user clicks the button, open the modal
updateBtn.onclick = function() {
    updateModal.style.display = "block";
}
powerBtn.onclick = function() {
    powerModal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
updateSpan.onclick = function() {
    updateModal.style.display = "none";
}
powerSpan.onclick = function() {
    powerModal.style.display = "none";
}

updatenoBtn.onclick = function() {
    updateModal.style.display = "none";
}
powernoBtn.onclick = function() {
    powerModal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        updateModal.style.display = "none";
    }
    else if (event.target == modal) {
        powerModal.style.display = "none";
    }
}
