
///////////////////////////////////////////////////////////////////////////////
// networked naughts and crosses :: client

///////////////////////////////////////////////////////////////////////////////
// global

var socket = io.connect('http://lw2.co.uk:27015');

var P1 = 0;
var P2 = 1;
var BLANK = -1;

var turn = null;
var player = null;

var ended = false;

// board data
// 0 = 'x', 1 = 'o', -1 = empty (see also: constants)
var board = [
	BLANK, BLANK, BLANK, BLANK, BLANK, BLANK, BLANK, BLANK, BLANK
];

// board ids used to display game state
var board_ids = [
	"t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9"
];

///////////////////////////////////////////////////////////////////////////////
// client display

// display game ui
function display_game() {
	for (var i = 1; i < (board_ids.length + 1); i++){
		document.getElementById('b'+i).style.opacity = 1;
		document.getElementById('h'+i).style.opacity = 1;
		document.getElementById('h'+i).className="hide";
		document.getElementById('t'+i).style.opacity = 1;
		document.getElementById('b'+i).style.pointerEvents = "all";
		document.getElementById('h'+i).style.pointerEvents = "all";
		document.getElementById('t'+i).style.pointerEvents = "all";
	}
	document.getElementById('findgame').className = "button_hide";
	document.getElementById('invitebtn').className = "button_hide";
	document.getElementById('invite').className = "button_hide";
	document.getElementById('leave').style.pointerEvents = "all";
	document.getElementById('leave').style.opacity = 1;
	document.getElementById('message').style.opacity=1;
}

// display invite url
function display_invite_url(url) {
	document.getElementById('invite').value = url;
	document.getElementById('invite').className = "option invite code";
	document.getElementById('invitebtn').value = "waiting for friend";
	document.getElementById('findgame').className = "button_hide";
}

// display the given status text
function display_text(s) {
	console.log(s);
	document.getElementById('message').style.opacity=0;
	document.getElementById('message').style.marginTop="-8em";
	setTimeout(function(){
		document.getElementById('message').innerHTML=s;
		document.getElementById('message').style.opacity=1;
		document.getElementById('message').style.marginTop="-11em";},600)
}

// display for when the game finishes (ie. offer replay)
function display_replay() {
	document.getElementById('replay').style.pointerEvents = "all";
	document.getElementById('replay').style.opacity = 1;
}

// display find game ui
function display_find_game() {
	for (var i = 1; i < (board_ids.length + 1); i++){
		document.getElementById('b'+i).style.opacity = 0;
		document.getElementById('h'+i).style.opacity = 0;
		document.getElementById('t'+i).style.opacity = 0;
		document.getElementById('b'+i).style.pointerEvents = "none";
		document.getElementById('h'+i).style.pointerEvents = "none";
		document.getElementById('t'+i).style.pointerEvents = "none";
	}
	document.getElementById('leave').style.pointerEvents = "none";
	document.getElementById('leave').style.opacity = 0;
	document.getElementById('findgame').className = "option";
	document.getElementById('invitebtn').className = "option invite";
	document.getElementById('invite').className = "option invite";
	document.getElementById('message').style.opacity=0;
	document.getElementById('findgame').value = "find game";
	document.getElementById('replay').style.pointerEvents = "none";
	document.getElementById('replay').style.opacity = 0;
}

// display win of given win data
function strike_win(arr) {
	for (var i = 0; i < arr.length; i++) {
		var e = document.getElementById(arr[i]);
		e.className += (turn == P1) ? ' winx' : ' wino';
	}
	ended = true;
	if (turn == player) display_text('u won');
	else display_text('ur opponent won');
	display_replay();
	board_disable();
}

// display stalemate
function strike_stalemate() {
	for (var i = 0; i < board.length; i++) {
		document.getElementById('h' + (i + 1)).className += " cat";
	}
	ended = true;
	display_text('game ended in a draw')
	display_replay();
	board_disable();
}

// display individual tile data by given tile index
// n index, p player
function strike_tile(n, p) {
	var e = document.getElementById("b" + board_ids[n][1]);
	e.className = ((p == P1) ? 'tilex' : 'tileo');
	if (turn != P1) {
		if (player == P1) display_text('ur turn');
		else display_text('ur opponents turn')
	}
	else {
		if (player == P1) display_text('ur opponents turn');
		else display_text('ur turn');
	}
}

// enable board
function board_enable() {
	for (var i = 0; i < board_ids.length; i++) {
		if (board[i] === BLANK) {
			var e = document.getElementById(board_ids[i]);
			if (turn == P2) e.className = "o"
			else e.className = "x";
		}
	}
}

// disable board
function board_disable() {
	for (var i = 0; i < board_ids.length; i++) {
		var e = document.getElementById(board_ids[i]);
		e.className = "disabled";
	}
}

// clear/reset all board tiles
function clear_board_tiles() {
	for (var i = 0; i < board_ids.length; i++) {
		var e = document.getElementById("b" + board_ids[i][1]);
		e.className = 'tile';
	}
}

///////////////////////////////////////////////////////////////////////////////
// client

// update game board visuals
// n index, p player
function update_board(n, p) {
	strike_tile(n, p);
	var s = 0, t = 0;
	var dbg_s = '', dbg_t = '';
	for (var i = 0; i < board.length; i++) {
		var m = Math.pow(2, i);
		if (board[i] == p) s += m;
		if (board[i] != -1) t += m;
	}
	if ((s & 7) === 7) 
			strike_win(['h1', 'h2', 'h3']);
	else if ((s & 56) === 56)
			strike_win(['h4', 'h5', 'h6']);
	else if ((s & 448) === 448)
			strike_win(['h7', 'h8', 'h9']);
	else if ((s & 73) === 73)
			strike_win(['h1', 'h4', 'h7']);
	else if ((s & 146) === 146)
			strike_win(['h2', 'h5', 'h8']);
	else if ((s & 292) === 292)
			strike_win(['h3', 'h6', 'h9']);
	else if ((s & 273) === 273)
			strike_win(['h1', 'h5', 'h9']);
	else if ((s & 84) === 84)
			strike_win(['h3', 'h5', 'h7']);
	else if (t == 511)
		strike_stalemate();
}

// process tile input
// n index, p player, r game result
function process_tile_input(n, p, r) {
	if (p == player && player != turn) return;
	if (board[n] == BLANK) {
		board[n] = p;
		update_board(n, p);
		if (r != -1) return;
		turn = (turn == P1) ? P2 : P1;
		if (player == turn)
			board_enable();
		else {
			board_disable();
			socket.emit('set_board', {'index' : n});
		}
	}
}

// clear board (visuals and data)
function board_clear() {
	board = [
		BLANK, BLANK, BLANK, BLANK, BLANK, BLANK, BLANK, BLANK, BLANK
	];
	clear_board_tiles();
}

// client setup
board_clear();
board_disable();

///////////////////////////////////////////////////////////////////////////////
// client input

// user clicks on the board
function board_click(n) {
	if (ended) return;
	process_tile_input(n - 1, player, -1);
}

// user clicks on the invite a friend button
function invite_friend() {
	socket.emit('find_game_private');
}

// user clicks on the find game button
function find_game() {
	socket.emit('find_game');
	document.getElementById('findgame').value = "finding game";
	document.getElementById('invitebtn').className = "button_hide";
	document.getElementById('invite').className = "button_hide";
}

// user clicks on the leave game button
function leave_game() {
	socket.emit('leave_game');
	display_find_game();
}

// user clicks on the replay button
function replay() {
	socket.emit('replay_game');
}

///////////////////////////////////////////////////////////////////////////////
// networking

// detect/join private game on load
if (location.hash.length == 7) {
	socket.emit('find_game_private',
		{'private_id' : location.hash.substring(1)});
}

// when an update from the opponent arrives:
// add their data to the board
socket.on('game_update', function(data) {
	if (data) {
		var r = data['result'];
		var index = data['index'];
		process_tile_input(index, ((player == 0) ? 1 : 0), r);
		turn = data['turn'];
	}
});

// game start network event
// called when players a matched agains each other
// and when a game is restarted
socket.on('start_game', function(data) {
	if (data) {
		ended = false;
		if (data['player'] == P1) player = P1;
		else player = P2;
		if (data['turn'] == P1) turn = P1;
		else turn = P2;
		board_clear();
		if (player == turn) board_enable();
		else board_disable();
	}
	if (turn == P1) {
		if (player == P1) display_text('ur turn');
		else display_text('ur opponents turn')
	}
	else {
		if (player == P1) display_text('ur opponents turn');
		else display_text('ur turn');
	}
	display_game();
});

// wait for player event
// server couldn't find any available players
// if private game, let the player know the invite url
// so they can invite their friends
socket.on('wait_for_player', function(data) {
	if (data) {
		if ('private_id' in data) {
			var id = data['private_id'];
			var domain = location.protocol + '//' + location.hostname +
				(location.port ? ':' + location.port : '');
			display_invite_url(domain + '/#' + id);
		}
	}
});

// game ended because of connection issues
socket.on('opponent_disconnect', function(data) {
	display_find_game();
});

// game ended because of connection issues
socket.on('invalid_private_id', function(data) {
	display_find_game();
});
