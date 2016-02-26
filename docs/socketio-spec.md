# JSON Specifications
## Syntax for every possible game action

### General:

Many events communicate data back to the client using an ack. I'll try to explain each event as clearly as possible. Keep in mind however, that to ack, one must ack from the @socketio.on() event function, so it may be difficult to separate the game logic as much as we'd like to. 

Whenever a `Player` object is used, it should be a dict structured like so:

	{'id': String, 'name': String, 'team': Int}

### Game creation and joining, and starting:

#### Creation:

Creating a game, the client will send a create event with their user-friendly name:

	// event
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

	{'game_id': String, 'player': Player}

	
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

	/* TO SERVER */

	{
		'action': 'start',
		'game_id': String
	}

Upon receiving `start`, the server should check that there are enough players. If not, or if we eventually have other errors, it should tell the client:

	/* TO CLIENT */

	{
		'action': 'start_error',
		'error_message': String
	}
	
If, however, there are enough players, the server should assign players to teams (assassins/knights), and send the following to every client:

	/* TO CLIENT */

	{
		'action': 'assign_roles',
		'player': Player,
		'players': [Player, Player,...] // Need to update players once teams have been set
	}

### Gameplay Actions

#### Leader Selection

Once the game has begun, the server needs to begin selecting leaders. The action should be sent to every client so it can say "Player is selecting a mission team" and the client with the match ID will begin the selection process:
	
	/* TO CLIENT */

	{
		'action': 'propose_mission',
		'leader': String 				// user_id of the leader
	}

#### Proposing a mission team

When a leader has selected the players, they will send them to the server like so:

	/* TO SERVER */
	
	{
		'action': 'propose_mission',
		'player_ids': 					 // OPEN TO DISCUSSION — but I think we only need to send IDs
			[
				String,
				String,
				String
			]
	}

After a mission has been proposed, the player list gets sent to every client so they can vote:

	/* TO CLIENT */
	
	{
		'action': 'do_proposal_vote',
		'player_ids':
			[
				String,
				String,
				String
			]
	}
	
#### Mission playout

Then the server waits for a vote from every client, which comes in like so:

	/* TO SERVER */
	
	{
		'action': 'proposal_vote',
		'vote': Bool (true = accept, false = deny) 
	}

The server tells the clients whether or not the vote passed, so it can update the UI
	
	/* TO CLIENT */
	
	{
		'action': 'proposal_vote_result',
		'pass': Bool,
		'number_failed': Int, 			// So the client can update UI on number of unapproved missions. 0 if passed.
		'players': 						// Optional, null if pass == false
			[
				String, 
				String, 
				String
			]
	}

If the vote passed, the server sent the players participating, and those players send the server their vote:

	/ * TO SERVER */
	
	{
		'action': 'mission_vote',
		'vote': Bool
	}
	
The server then tells each client the results:

	/* TO CLIENT */
	
	{
		'action': 'mission_vote_result',
		'pass': Bool
	}

Then the server picks the next leader and the cycle starts again.

### Ending:

This needs discussion.





























