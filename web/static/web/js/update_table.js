
let ws = new WebSocket('ws:' + window.location.hostname + ':8000/round_results')

ws.onopen = () => {
    console.log("Socket connection opened")
  }

ws.onmessage = (event) =>{

  console.log(event.data)
  response = JSON.parse(event.data)
  response = JSON.parse(response["text"])

  // Check wheter the incoming message corresponds to
  // a new round message or a bet update
  
  if(response.hasOwnProperty("num_cards")){
    location.reload()
  }else{

    increment = parseInt(response["increment"])

    span = $("." + response["type"] + "[player=" + response["player"].split("-")[0] + "]")
    span.text(parseInt(span.text()) + increment)

    count = $("#" + response["type"] + "s-count")
    count.text(parseInt(count.text()) + increment)
    hands_count[response["type"]] += increment

    plus = $( ".fa-plus-square" + "[player=" + response["player"] + "]")
    minus = $( ".fa-minus-square" + "[player=" + response["player"] + "]")

    if(response["plus"] == "disabled")
      plus.addClass("disabled")
    else
      plus.removeClass("disabled") 

    if(response["minus"] == "disabled")
      minus.addClass("disabled")
    else
      minus.removeClass("disabled") 
  }
}



/* Insert new row in the table thorugh javascript
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