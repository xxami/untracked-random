
///////////////////////////////////////////////////////////////////////////////
// networked naughts and crosses :: server

var express = require('express');
var io = require('socket.io');
var path = require('path');
var app = express();
var server = require('http').createServer(app);
var io = io.listen(server);

app.use(express.static(path.join(__dirname, 'public')));
server.listen(27015);

///////////////////////////////////////////////////////////////////////////////
// global

// list of client data for clients who are waiting for games
// data is in the format of {'socket', 'private', 'private_id'}
// where socket is waiting clients socket, private is a boolean
// value where true means this is an invite only game (ie.
// waiting for an invited player), and private_id is used
// to idenfity valid invitees for private invitations
var open_games = [];
// list of currently playing games
// games are indexed by creators socket id (ie. socket.id)
// key data stored here is in the format {'p1', 'p2', 'game'}
// where p1 and p2 are the player sockets and game is a
// dictionary of gamedata (ie. get_new_gamedata())
// the index can be accessed from both player sockets due
// to the property socket.game_id being set to this value
// for all clients playing a game
var games = {};

///////////////////////////////////////////////////////////////////////////////
// misc

// check a given gameboard for wins, stalemates and return
// a status code indicator, also switch turns and set
// game state to ended if necessary
// returns -1 if game still in play
// returns 0 if game won by player 1
// returns 1 if game won by player 2
// returns 2 if game is a stalemate
function get_game_result(game, p) {
	var win_vals = [7, 56, 448, 73, 146, 292, 273, 84];
	var s = 0, t = 0;
	for (var i = 0; i < game['board'].length; i++) {
		var m = Math.pow(2, i);
		if (game['board'][i] == p) s += m;
		if (game['board'][i] != -1) t += m;
	}
	for (var i = 0; i < win_vals.length; i++) {
		if ((win_vals[i] & s) === win_vals[i]) {
			return (p == 0) ? 0 : 1;
		}
	}
	if (t == 511) {
		return 2;
	}
	return -1;
}

// return game data for a new board, neccessary?
function get_new_gamedata() {
	return {
		'turn' : 0,
		'board' : [-1, -1, -1, -1, -1, -1, -1, -1, -1],
		'ended' : false
	};
}

// returns new private id for invite only games generated at random
// private ids are 6 characters long, ie. 5FB90N
function gen_private_id() {
	// added two sets of numbers to decrease the chance
	// of only letters being generated as part of the id
	var c = "A0B1C2D3E4F5G6H7I8J9K0L1M2N3O4P5Q6R7S8T9U0VWXYZ";
	var result = '';
	for (var i = 0; i < 6; i++) {
		result += c.charAt(Math.floor(Math.random() * c.length));
	}
	return result;
}

// go through all games and clear up any mess
// caused by disconnecting players also
// let affected players know their opponent has
// disconnected if possible
function cleanup_games() {
	for (var game in games) {
		var d = games[game];
		var remove_game = false;
		if (d['p1'].disconnected) {
			remove_game = true;
			if (!d['p2'].disconnected) {
				d['p2'].emit('opponent_disconnect');
			}
		}
		else if (d['p2'].disconnected) {
			remove_game = true;
			if (!d['p1'].disconnected) {
				d['p1'].emit('opponent_disconnect');
			}
		}
		if (remove_game) {
			delete games[d['p1'].game_id];
		}
	}
}

///////////////////////////////////////////////////////////////////////////////
// networking

// sockits!
io.sockets.on('connection', function(socket) {

	// preset game_id to avoid access errors
	socket.game_id = false;

	// set a value to the game board
	// sent when a player clicks and X or O
	// in a valid space on the board (on the client)
	socket.on('set_board', function(data) {
		if (!data) return;
		if (data['index'] === undefined) return;
		var n = data['index'];
		if (socket.game_id in games) {
			var game = games[socket.game_id];
			if (typeof n !== 'number' || n >= game['game']['board'].length)
				return;
			if (game['p1'].disconnected || game['p2'].disconnected) {
				socket.emit('opponent_disconnect');
				return;
			}
			if (game['game']['ended'] === true) return;
			var p = (socket.id == game['p1'].id) ? 0 : 1;
			if (game['game']['turn'] != p || game['game']['board'][n] != -1)
				return;
			// set a move on the board and see if the game is won/stalemate
			game['game']['board'][n] = p;
			var game_result = get_game_result(game['game'], p);
			game['game']['turn'] = ((game['game']['turn'] == 0) ? 1 : 0);
			if (game_result != -1) game['game']['ended'] = true;
			// update clients
			if (game['p1'].id == socket.id) {
				game['p2'].emit('game_update', {'result' : game_result,
				'turn' : game['game']['turn'], 'index' : n});
			}
			else {
				game['p1'].emit('game_update', {'result' : game_result,
				'turn' : game['game']['turn'], 'index' : n});
			}
		}
		else socket.emit('opponent_disconnect');
	});

	// find a new game
	// either put them in the wait list
	// or match them with someone already waiting
	socket.on('find_game', function(data) {
		// remove player from open games before letting them find a game
		// note: client shouldn't allow players to do this but just
		// incase they do, make sure it doesn't break anything
		for (var i = 0; i < open_games.length; i++) {
			var game = open_games[i];
			if (game['socket'].id == socket.id) {
				open_games.splice(i, 1);
			}
		}
		// remove player from games before letting them find a game
		// note: client shouldn't allow players to do this
		// but just incase they do, make sure it doesn't break anything
		if (socket.game_id in games) {
			var game = games[socket.game_id];
			if (socket.id == game['p1'].id) {
				if (!game['p2'].disconnected)
					game['p2'].emit('opponent_disconnect');
			}
			else {
				if (!game['p1'].disconnected)
					game['p1'].emit('opponent_disconnect');
			}
			delete games[game['p1'].game_id];
		}
		var found = false;
		// find a valid open game for the player to join first
		for (var i = 0; i < open_games.length; i++) {
			var game = open_games[i];
			if (!game['private']) {
				game['socket'].game_id = game['socket'].id;
				socket.game_id = game['socket'].id;
				games[game['socket'].game_id] = {'p1' : game['socket'],
					'p2' : socket, 'game' : get_new_gamedata()};
				open_games.splice(i, 1);
				socket.emit('start_game', {'player' : 1, 'turn' : 0});
				game['socket'].emit('start_game', {'player' : 0, 'turn' : 0});
				found = true;
				return;
			}
		}
		if (!found) {
			// no valid open games, create one and notify the
			// player to wait for other players
			open_games.push({'socket' : socket, 'private' : false,
				'private_id' : null});
			socket.emit('wait_for_player');
		}
	});

	// find a new game for invitation only games
	// if private_id data given attempt to join the player
	// to a private waiting invitation only game
	// otherwise create an open invitation only game
	// and return its private identifier (to 'wait_for_player')
	socket.on('find_game_private', function(data) {
		// remove player from open games before letting them find a game
		// note: client shouldn't allow players to do this but just
		// incase they do, make sure it doesn't break anything
		for (var i = 0; i < open_games.length; i++) {
			var game = open_games[i];
			if (game['socket'].id == socket.id) {
				open_games.splice(i, 1);
			}
		}
		// remove player from games before letting them find a game
		// note: client shouldn't allow players to do this
		// but just incase they do, make sure it doesn't break anything
		if (socket.game_id in games) {
			var game = games[socket.game_id];
			if (socket.id == game['p1'].id) {
				if (!game['p2'].disconnected)
					game['p2'].emit('opponent_disconnect');
			}
			else {
				if (!game['p1'].disconnected)
					game['p1'].emit('opponent_disconnect');
			}
			delete games[game['p1'].game_id];
		}
		if (!data) {
			var done = false;
			while (!done) {
				var matched = false;
				var id = gen_private_id();
				open_games.forEach(function(game) {
					if (game['private_id'] == id) matched = true;
				});
				if (!matched) {
					done = true;
					open_games.push({'socket' : socket, 'private' : true,
						'private_id' : id});
					socket.emit('wait_for_player', {'private_id' : id});
				}
			}
		}
		else {
			if (data['private_id'] !== undefined) {
				var found = false;
				for (var i = 0; i < open_games.length; i++) {
					var game = open_games[i];
					if (game['private_id'] == data['private_id']) {
						found = true;
						game['socket'].game_id = game['socket'].id;
						socket.game_id = game['socket'].id;
						games[game['socket'].game_id] = {'p1' : game['socket'],
							'p2' : socket, 'game' : get_new_gamedata()};
						open_games.splice(i, 1);
						socket.emit('start_game', {'player' : 1, 'turn' : 0});
						game['socket'].emit('start_game', {'player' : 0,
							'turn' : 0});
						break;
					}
				}
				if (!found) {
					socket.emit('invalid_private_id');
				}
			}
			else socket.emit('invalid_private_id');
		}
	});

	// replay game
	socket.on('replay_game', function(data) {
		if (socket.game_id in games) {
			var game = games[socket.game_id];
			if (game['p1'].disconnected || game['p2'].disconnected) {
				socket.emit('opponent_disconnect');
				delete games[game['p1'].game_id];
			}
			else {
				if (!game['game']['ended']) return;
				game['game'] = get_new_gamedata();
				game['p1'].emit('start_game', {'player' : 0, 'turn' : 0});
				game['p2'].emit('start_game', {'player' : 1, 'turn' : 0});
			}
		}
	});

	// remove player from any game they may be in
	// make sure to notify other affected players that
	// their oppenent has left the game
	socket.on('leave_game', function(data) {
		for (var i = 0; i < open_games.length; i++) {
			var game = open_games[i];
			if (game['socket'].id == socket.id) {
				open_games.splice(i, 1);
			}
		}
		if (socket.game_id in games) {
			var game = games[socket.game_id];
			if (socket.id == game['p1'].id) {
				if (!game['p2'].disconnected)
					game['p2'].emit('opponent_disconnect');
			}
			else {
				if (!game['p1'].disconnected)
					game['p1'].emit('opponent_disconnect');
			}
			delete games[game['p1'].game_id];
		}
	})

	// disconnection clean up
	// remove player from any open game or game
	// they are in (see cleanup_games() for more)
	socket.on('disconnect', function(data) {
		var i = 0;
		socket.disconnected = true;
		open_games.forEach(function(game) {
			if (game['socket'].id == socket.id) {
				open_games.splice(i, 1);
			}
			i++;
		});
		if (socket.game_id in games)
			cleanup_games();
	});

});
