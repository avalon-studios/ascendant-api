# Socket.IO Specifications
## Syntax for every possible game action

### General:

Many events communicate data back to the client using an ack. I'll try to explain each event as clearly as possible. Keep in mind however, that to ack, one must ack from the @socketio.on() event function, so it may be difficult to separate the game logic as much as we'd like to. 

Whenever a `Player` object is used, it should be a dict structured like so:

	{'id': String, 'name': String, 'team': Int}

### Game creation and joining, and starting:

#### Creation:

Creating a game, the client will send a create event with their user-friendly name:

	@socketio.on('create')
	def on_create(data):
	
`data` will be a dictionary containing:

	{'name': String}
	
The server should then ack (by using a return at the end of `on_create`) a game dictionary containing:

	/* TO CLIENT */

	{'game_id': String, 'player': Player}

If the server cannot create a game, game_id should be null.

#### Joining:

To join an existing game, the client will call:

	@socketio.on('join')
	def on_join(data):

`data` will be a dictionary containing:

	{'name': String, 'game_id': String}
	
then server should ack (return):

	{'game_id': String, 'player': Player, 'players': [Player, Player...]}

	
Upon someone successfully joining, or a player leaving, the server should send an `update_players` event *every* client in the game room:

    socketio.emit('update_players', [Player, Player...], json=True, room=self.game_id)
      
#### Leaving:

To leave a game, we call:

	@socketio.on('leave')
	def on_join(data):
	
`data` will be a dictionary containing:

	{'player_id': String, 'game_id': String}
	
Then make sure you `update_players`! I don't think we should ack this — discuss?

#### Starting the game:

Only the person who created the game has the ability to start it:

	@socketio.on('start')
	def on_start(data):

where `data` is a dict:

	{'game_id': String}

Upon receiving `start`, the server should check that there are enough players (though there should be, if start was sent. Double check of course). If there aren't enough players, ack an error. `error_message` should be a user readable description of what's wrong. If the start is successful, ack a success with no error message. 

	//ack:
	return {'success': Bool, 'error_message': String}
	
After a successful start, emit an `assign_roles` event to the clients.

	socketio.emit('assign_roles' {player: Player, players: [Player, Player...], json=True, room=game_id}

Now the server should wait for a `ready` event from each client:

	@socketio.on('ready')
	def on_ready(data):
	
`data` will be a dict with a `game_id` and `player_id` and this should mark the player as ready, and ack with a success and error message if something went wrong:

	// ack
	return {'success': Bool, 'error_message': String}

### Gameplay Actions

#### Leader Selection

Once the game has begun, the server needs to begin selecting leaders. The action should be sent to every client in the room so it can say "Player.name is selecting a mission team" and the client with the matching ID will begin the selection process:
	
	socketio.emit('propose_mission', {'leader': Player}, json=True, room=game_id)

#### Proposing a mission team

When a leader has selected the players, they will send them to the server like so:
	
	@socketio.on('propose_mission')
	def on_propose_mission(data):
	
where `data` is:

	{'game_id': String, 'player_ids': [String, String...]}
	
This should check for the proper number of players and ack a success: 

	// ack
	return {'success': Bool, 'error_message': String}

After a mission has been proposed, the player list gets sent to every client so they can vote:

	socketio.emit('do_proposal_vote', {'players': [Player, Player...]}, json=True, room=game_id)


#### Mission playout

Then the server waits for a vote from every client, which comes in like so:

	@socketio.on('proposal_vote')
	def on_proposal_vote(data):
	
where `data` is a dictionary with a 'vote' key and player:
 
	{'game_id': String, 'player_id': String, 'vote': Bool}

After all votes have been received, emit the result. `number_failed` is the number of proposals that have been denied so far (0 if pass == true). `players` is the players in the mission *if it passed*. That way they can start voting right away. 

	socketio.emit('proposal_vote_result', {'pass': Bool, 'number_failed': Int, players: [Player, Player...]}, json=True, room=game_id)

If the vote passed, the server sent the players participating, and those players send the server their vote:

	@socketio.on('mission_vote')
	def on_mission_vote(data):
	
where `data` is a dict: 

	{'vote': Bool, 'game_id': String}

Ack when you receive the vote:
	
	// ack
	return {'success': Bool, 'error_message': String}
	
The server then tells each client the results:

	socketio.emit('mission_vote_result', {'pass': Bool, 'mission_number': Int}, json=True, room=game_id)


Then the server picks the next leader and the cycle starts again.

### Ending:

This needs discussion.





























