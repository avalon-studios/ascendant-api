# JSON Specifications
## Syntax for every possible game action

### General:

Every JSON object (from now on referred to as an "action") sent or received will have an `action` key, used to identify what action is being performed. Each action will also have a `user` key, with an id for the user performing the action.

### Game creation and joining, and similar:

#### Creation:

Creating a game, the client will send a create action with their user-friendly name:

	{
		'action': 'create'
		'name': String
	}
	
Upon creation of the game, the server should send the client a user_id for the game, and a game_id:

	{
		'action': 'create',
		'user_id': String,
		'game_id': String
	}

If the server cannot create a game, game_id should be null.

#### Joining:

To join an existing game, the client will send:

	{
		'action': 'join',
		'name': String,
		'game_id': String
	}
	
The server should reply with a success bool, and error_message if success is false, and a list of existing players if the success is true:

	{
		'action': 'join',
		'success': Bool,
		'error_message': String,
		'players':
			[{
				'user_id': String,
				'name': String
			},
			{
				'user_id': String,
				'name': String
			}]
	}
	
Upon someone successfully joining, or a player leaving, the server should send an updated player list to *every* client in the game:

	{
		'action': 'update_players',
		'players':
			[{
				'user_id': String,
				'name': String
			},
			{
				'user_id': String,
				'name': String
			}]
	}

#### Starting the game:

Only the person who created the game has the ability to start it:

	{
		'action': 'start',
		'game_id': String,
	}





























