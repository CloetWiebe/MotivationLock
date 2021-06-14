'use strict';
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const route= `${window.location.hostname}:5000/shutdown`

let htmlGewensteCalorieen, htmlGeslacht, htmlLeeftijd, htmlGewicht;
//#region ***  DOM references                           ***********
//#endregion

//#region ***  Callback-Visualisation - show___         ***********
const showGegevens = function () {
  let params = new URLSearchParams(window.location.search);
  htmlGewensteCalorieen = params.get('gewensteCalorieen');
  htmlGeslacht = params.get('geslacht');
  htmlLeeftijd = params.get('leeftijd');
  htmlGewicht = params.get('gewicht');
  socket.emit("F2B_start", {gewenstecal: htmlGewensteCalorieen, geslacht: htmlGeslacht, leeftijd: htmlLeeftijd, gewicht: htmlGewicht})
  alert("Data verstuurd, wacht een minuut op onze berekeningen");
};
//#endregion

//#region ***  Callback-No Visualisation - callback___  ***********
//#endregion

//#region ***  Data Access - get___                     ***********
//#endregion

//#region ***  Event Listeners - listenTo___            ***********
const listenToSocket = function(){
  console.log("Litsening to Socket")

  // -----------------------------------------Calorieen-------------------------------------------------
  socket.on("B2F_cal", function(jsonObject){
    // console.log("Data van cal", jsonObject)
    let verbrandecal= jsonObject.verbrandecal
    // console.log("verbrand deze minuut", verbrandecal)
    let totverbrand=jsonObject.totverbrand
    // console.log("Tot verbrand:", totverbrand)
    let goalcal=jsonObject.goalcal
    // console.log("Gewenstecal:", goalcal)
    let Htmlcal =` <div class="u-max-width-sm">
                        <h1>Calorieën afgelopen minuut</h1>
    <p>Je doel was <strong>${goalcal}</strong> calorieën te verbanden</p>
    <p>Afgelopen minuut heb je <strong>${verbrandecal.toFixed(2)}</strong> calorieën verbrand</p>
    <p>Je hebt al <strong>${totverbrand.toFixed(2)}</strong> calorieën verbrand</p>
    <p>Je hebt al <strong>${((totverbrand/goalcal)*100).toFixed(2)}%</strong> precent van je doel gedaan</p>
    <div>`
    document.querySelector('.js-calorieen').innerHTML = Htmlcal
  })

  // ----------------------------------------bpm-------------------------------------------------------
  socket.on('B2F_bpm', function(jsonObject){
    // console.log("Data van hart", jsonObject)
    let bpm = jsonObject.bpm
    // console.log("bmp: ", bpm)
    let Htmlhartslag=`                  <div class="u-max-width-sm">
    <h1>Hartslag de afgelopen minuut</h1>
    <p>Je hartslag gemiddelde harslag afgelopen minuut was <strong>${bpm} bpm</strong></p>
  </div>`
  document.querySelector('.js-hartslag').innerHTML=Htmlhartslag
  })

  // ---------------------------------------temp
  socket.on('B2F_temp', function(jsonObject){
    // console.log("Data van temp", jsonObject)
    let temp = jsonObject.temp
    // console.log("temp: ", temp)
    let HtmlTemp=`                  <div class="u-max-width-sm">
    <h1>Temperatuur afgelopen minuut</h1>
    <p>Je gemiddelde temperatuurn afgelopen minuut was <strong>${temp} graden celcius</strong></p>
  </div>`
  document.querySelector('.js-temp').innerHTML= HtmlTemp
  })

  socket.on('B2F_moved', function(jsonObject){
    // console.log("Data van moved", jsonObject)
    let moved = jsonObject.moved
    // console.log("moved: ", moved)
    if (moved == 1){
      let Htmlmoved = `                  <div class="u-max-width-sm">
      <h1>Beweeg je nog?</h1>
      <p>Je beweegt nog volgens de sensor</p>
    </div>`
    document.querySelector('.js-moved').innerHTML= Htmlmoved
    }
    else if(moved == 0){
      let Htmlmoved = `                  <div class="u-max-width-sm">
      <h1>Beweeg je nog?</h1>
      <p>Je beweegt niet meer volgens de sensor</p>
    </div>`
    document.querySelector('.js-moved').innerHTML= Htmlmoved
    }
  })

  socket.on('B2F_totcalday', function(jsonObject){
    console.log("Data calperday: ", jsonObject)
    let Htmltable = `                    
    <tr>
    <th><strong>Totaal aantal calories verbrand</strong></th>
    <th><strong>Datum</strong></th>
    <th><strong>Dag</strong></th>
    </tr>`
    for (let dag of jsonObject.meetingen ){
        Htmltable +=`                    
        <tr>
        <td>${dag.Totaal}</td>
        <td>${dag.Datum}</td>
        <td>${dag.Dag}</td>
      </tr>`
      }
      document.querySelector('.js-table').innerHTML=Htmltable
  })
}

const listenToReset = function(){
  console.log("Listening to reset click")
  const button = document.querySelector('.js-reset')
  button.addEventListener('click', function(){
    console.log("Reset Button Clicked")
    socket.emit('F2B_reset', {reset: "ja"})
  })
}

const litsenToPage = function(){
  console.log("reset")
  socket.emit('F2B_reset', {reset: "ja"})
}
//#endregion

//#region ***  Init / DOMContentLoaded                  ***********
const init = function () {
  console.log('DOM is geladen');
  if (document.querySelector('.c-form-item')) {
    console.log('Form pagina');
    litsenToPage()
  }
  if (document.querySelector('.js-calorieen')) {
    console.log('Stats pagina');
    showGegevens();
    listenToSocket();
    listenToReset();
  }
};

document.addEventListener('DOMContentLoaded', init);
//#endregion
