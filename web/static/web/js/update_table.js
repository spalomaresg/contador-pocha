
let ws = new WebSocket('ws:' + window.location.hostname + ':8000/round_results')

//window.addEventListener("focus", () => ws = new WebSocket('ws:' + window.location.hostname + ':8000/round_results')
//);

function visibility_change(){
  console.log("Change of visibility")
  switch(document.visibilityState) {
    case "hidden":
      console.log("hidden");
      break;
    case "visible":
      console.log("visible")
      break;
  }
}

//document.addEventListener("visibilitychange",visibility_change(),false)

ws.onopen = () => {
  console.log("Socket connection opened")
}

ws.onclose = () =>{
  console.log("Socket connection closed")
}

ws.onmessage = (event) =>{

  console.log(event.data)
  response = JSON.parse(event.data)
  response = JSON.parse(response["text"])

  // Check wether the incoming message corresponds to
  // a new round message or a bet update
  
  if(response.hasOwnProperty("num_cards")){
    location.reload()
  }else{

    increment = parseInt(response["increment"])
    if(increment == 1) elem = $("." + response["type"] + ".fa-plus-square" + "[player=" + response["player"] + "]")
    else elem = $("." + response["type"] + ".fa-minus-square" + "[player=" + response["player"] + "]")
    player = response["player"]
    elem.trigger('click', true);
  }
}


/*
  This function is aimed to serve as a non-reloading
  solution to update the table información whenever
  a new message come from the weboscket.
  This is a much cleaner design much but requires some
  logic (reordering of columns to match descending order, 
  color map...) which is currently on the server side 
  of the application.
*/

/* 
  Insert new row in the table thorugh javascript
  This is a cleaner method than refreshing the page
  but it would require additional code to reorder
  the columns according to each player points.
    
    JSON structure

    {
      num_cards:
      total_bets ?
      bets: [{
        player:
        bet:
        won:
        hand:
        points ?
      }]
    }

*/

function add_row(){

  var row_div = document.createElement("div")
  row_div.setAttribute("num_cards",new_round["num_cards"])
  row_div.setAttribute("class","row flex-row")

  var first_col_1 = document.createElement("div")
  first_col_1.setAttribute("class","col flex-cell")
  first_col_1.innerHTML = new_round["num_cards"]
  var first_col_2 = document.createElement("span")
  first_col_2.setAttribute("class","bet-details")

  
  row_div.appendChild(first_col_1)
  first_col_1.appendChild(first_col_2)

  total_bets = 0
  for(const player of new_round["bets"]) {

    total_bets += player["bet"]

    player_div = document.createElement("div")
    player_div.setAttribute("bet",player["bet"])
    player_div.setAttribute("won", player["won"])
    player_div.setAttribute("class","col flex-cell")

    player_points = document.createElement("span")
    player_points.setAttribute("class","score win-0") 
    player_points.innerHTML = 15
    player_div.appendChild(player_points)

    player_bets = document.createElement("span")
    player_bets.setAttribute("class","bet-details")
    player_bets.innerHTML = player["bet"] + "/" + player["won"]
    player_div.appendChild(player_bets)

    if(player["hand"] == "hand"){
      img = document.createElement("i")
      img.setAttribute("class","fas fa-hand-paper")
      player_div.appendChild(img)
    }else if (player["hand"] == ["dessert"]){
      img = document.createElement("img")
      img.setAttribute("class","dessert")
      img.setAttribute("src", "/static/web/img/cards.png")
      player_div.appendChild(img)
    }

    row_div.appendChild(player_div)

    first_col_2.innerHTML = "/ " + total_bets

    table = document.getElementsByClassName("tbody")[0]
    table.appendChild(row_div)

  }
}