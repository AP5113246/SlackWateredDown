#### auth_* functions ####
Assumed:
	- The token of a registered user is created from an encryption their email. 
	- The u_id is the users element in the Users dictionary (under DATA)
	- When a user registers and it is valid, they are automatically logged in.
	- The first valid registered user is a global owner.
    - When a user registers, they are given a unique handle.
	- This handle is created from the concatenation of the first letter of first name and last name with numbers added at the name.
	- If handle exceeds 20 characters, the last name is cutoff by the length of the number.
	- Login function cannot be called twice on the same user as the front-end display will prevent them from doing so.
	- Logged out users can not access other functions within Flockr

#### channels_* functions ####
Assumed:
	- Creating a valid channel sets you as a member and the owner of that channel.
	- Registering a user validated their token, and thus you don't need to log them in to use that token
	- The public or private data for channels is held in the category 'is_public'
	- Indexing channel id's from 0

#### channel_* functions ####
Assumes:
	- If a test passes all error checks and fails the success check, raises Input Error with description "does not return data"
    - channels created will have 'name' as a string only i.e. "test_channel"
    - channel id must be unique
    - if a member is an owner and also a member of a channel, that person will be shown as an owner on the frontend
    - add_owner can only be used on members of channel, as frontend will prevent them from doing so.
    - remove_owner can only be used on owners of channel, as frontend will prevent them from doing so. 
	- A member cannot use 'channel_join' on a channel he is already in
	- in the reacts dictionary, 'is_this_user_reacted' will be generated when calling the function "channel_messages"

#### user* functions ####
Assumes:
	- user_setname allows multiple users to have the same name
	- user_setemail will raise InputError if user sets email to same email
	- user_sethandle will raise InputError if user sets handle to same handle
	- If a user sets their handle to a handle that can be created, the other
	 user will generate another unique handle
	- Handles created can have numbers at the end only
	- Coordiantes passed in upload photo will only be an integer greater than 0.

#### message_* functions ####
Assumes:
	- The creator of a channel can edit any user's message, likewise with global users
	- Messages can't be edited to be over the 1000 character limit
	- On a failed message send, it returns a 'None' message_id unless an error is raised
	- Message ID's are independent of the channel.
	- Two messages from seperate channels cannot have the same message_id
	  since message remove doesn't check channel_id, just message id
	- Message edit and remove raises an input error if the message doesn't exist.
	- Editing a message to '', removes the message
    - Message send will create an empty reacts list and set is_pinned to False.
    - Message react will create dictionary keys in 'reacts' for 'react_id' and 'u_ids' but not 'is_this_user_reacted', for a new react_id
    - If a user reacts to a message and leaves the channel, the reaction will still remain.

#### standup_ functions ####
Assumes:
	- The 1000 character limit considers the entirety of the standup since it is sent in one message after the timer
	- The Name of each user in the standup message includes their entire first and last name, concatenated together with the casing maintained e.g TestUser: message
	- The functions don't need to check the validity of the tokens
	- The data for the standups is held in it's own section of data.py and not under the current channel data and a new entry is made each time a standup is started and deleted when it ends

#### Extra ####
Assumes:
    - Helper function have been used in channel.py and message.py to reduce
    excess code.
    - In other.py, an InputError will occur if admin_permission is used but u_id is not found in data.
    - In other.py, search will return message sorted by reverse order. e.g. message id 7, 6, 5, 4, 3, 1.
