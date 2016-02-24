# JSON Specifications
## Syntax for every possible game action

### TODO:

- How do clients work? Do we need client IDs, and send them with every call, or can we identify simple from the client? The chat example seemed to suggest the latter.
- In a similar vein, can a client object be associated with a game, or do we need to send a game_id with every action?

### General:

Every JSON object (from now on referred to as an "action") sent or received will have an `action` key, used to identify what action is being performed. Each action will also have a `user` key, with an id for the user performing the action.

Whenever a `Player` object is used, it should be a json object structured like so:

	{
		'id': String,
		'name': String,
		'team': Int (0 = good, 1 = bad)
	}

### Game creation and joining, and starting:

#### Creation:

Creating a game, the client will send a create action with their user-friendly name:

	/* TO SERVER */

	{
		'action': 'create'
		'name': String
	}
	
Upon creation of the game, the server should send the client a user_id for the game, and a game_id:

	/* TO CLIENT */

	{
		'action': 'create',
		'game_id': String,
		'player': Player
	}

If the server cannot create a game, game_id should be null.

#### Joining:

To join an existing game, the client will send:

	/* TO SERVER */

	{
		'action': 'join',
		'name': String,
		'game_id': String
	}
	
The server should reply with a success bool, and error_message if success is false, and a list of existing players if the success is true:

	/* TO CLIENT */

	{
		'action': 'join',
		'game_id': String
		'player': Player,
		'players': [Player, Player,...]
	}
	
Upon someone successfully joining, or a player leaving, the server should send an updated player list to *every* client in the game:

	/* TO CLIENT */

	{
		'action': 'update_players',
		'players': [Player, Player,...]
	}

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





























