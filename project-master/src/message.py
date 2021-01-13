import datetime
import threading
from data import DATA
from helper import (
    is_valid_token,
    is_valid_channel_id,
    user_in_channel,
    get_uid,
    get_message_info,
    is_owner,
    is_owner_permission,
    is_allowed_message_id,
    is_valid_react_id,
    get_channel
)
from error import InputError, AccessError
import helper as hp

def message_send(token, channel_id, message):
    '''
        AccessError if:
        - Invalid token
        - User not in channel
        InputError if:
        - Invalid channel id
        - Message is invalid or > 1000 chars long
        - Channel id is valid but message did not send
        - Channel id is valid but error still occurred
    '''
    if not is_valid_token(token):
        raise AccessError(description='Invalid token to message_send')
    elif not is_valid_channel_id(channel_id):
        raise InputError(description='Invalid channel_id to message_send')
    elif not user_in_channel(get_uid(token), channel_id):   
        raise AccessError(description='User not in channel')    
    elif not isinstance(message, str) or not len(message) <= 1000:
        raise InputError(description='Message is invalid')

    # Gets the current timestamp and truncates it to an integer (originally a float)
    time = int(datetime.datetime.now().timestamp())

    # creates a list of message_ids from messages sent
    messages = []
    for channel in DATA['channels']:
        messages.extend([message['message_id'] for message in channel['messages']])
    # if messages exist, find the max message id and add it
    # if no messages exist, set message_id to 0
    if messages:
        message_id = max(messages) + 1
    else:
        message_id = 0
 
    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            u_id = get_uid(token)
            # Checks to make sure that u_id and message_id aren't empty
            # if str(u_id) and str(message_id):
            message_info = {
                "message_id": message_id,
                "u_id": u_id,
                "message": message,
                "time_created": time,
                "channel_id": channel_id,
                "is_pinned" : False,
                "reacts" : [],
            }
            channel['messages'].append(message_info)
            # else: # Check these, they may be raising the wrong thing...
            #     if not str(message_id):
            #         raise InputError(description='Channel id is valid but message did not send')
            #     else:
            #         raise InputError(description='Channel id is valid but error still occurred')
            
    return {
        'message_id': message_id,
    }

def message_remove(token, message_id):
    '''
        AccessError if:
        - Message was not sent by 'token' user
        - 'token' user is not an owner of the channel or flockr
        - Invalid token
        InputError if:
        - Message does not exist
    '''
    message_info = get_message_info(message_id)
    if message_info == {}: # when message_info is an empty dict it means the message doesn't exist
        raise InputError(description='Message does not exist')
    channel_id = message_info['channel_id'] # extracting the channel id from the message id
    
    if not is_valid_token(token):
        raise AccessError(description='Invalid token')
    elif message_info['u_id'] != get_uid(token) and not is_owner(get_uid(token), channel_id) and not is_owner_permission(get_uid(token)):   
        raise AccessError(description='User does not have permission to remove this message')

    get_channel(channel_id)['messages'].remove(message_info)

    return {
    }

def message_edit(token, message_id, message):
    '''
        AccessError if:
        - Message was not sent by 'token' user
        - 'token' user is not an owner of the channel or flockr
        - Invalid token
        InputError if:
        - Message does not exist
        - New message is an invalid type or > 1000 chars long
    '''
    message_info = get_message_info(message_id)
    if message_info == {}: # when message_info is an empty dict it means the message doesn't exist
        raise InputError(description='Message does not exist')
    channel_id = message_info['channel_id'] # extracting the channel id from the message id

    if not is_valid_token(token):
        raise AccessError(description='Invalid token')
    elif message_info['u_id'] != get_uid(token) and not is_owner(get_uid(token), channel_id) and not is_owner_permission(get_uid(token)):   
      raise AccessError(description='User does not have permission to edit this message')
    elif not isinstance(message, str) or not len(message) <= 1000:
        raise InputError(description='New message is invalid')

    if message == "": # editing a message to an empty message deletes it
        return message_remove(token, message_id)

    channel = get_channel(channel_id)
    for curr_message in channel['messages']:
        if curr_message['message_id'] == message_id:
            curr_message['message'] = message

    return {}

#NOTE: message_pin and unpin can only be used by owners

def message_pin(token, message_id):
    '''
        AccessError if:
        - Token is invalid
        - Token is not in owner members of a channel
        InputError if:
        - Message does not exist
        - Message is already pinned
    '''
    if not is_valid_token(token):
        raise AccessError(description='Invalid token to message_pin')

    message_info = get_message_info(message_id)
    if message_info == {}: # when message_info is an empty dict it means the message doesn't exist
        raise InputError(description='Message does not exist')

    if message_info['is_pinned'] == True:
        raise InputError(description='Message is already pinned')

    # only owners can pin and unpin messages
    if not is_owner(get_uid(token), message_info['channel_id']):
        raise AccessError(description='User is not an owner of the channel')
    
    channel = get_channel(message_info['channel_id'])
    for curr_message in channel['messages']:
        if curr_message['message_id'] == message_id:
            curr_message['is_pinned'] = True
    return {}

def message_unpin(token, message_id):
    '''
        AccessError if:
        - Token is invalid
        - Token is not in owner members of a channel
        InputError if:
        - Message does not exist
        - Message is already unpinned
    '''
    if not is_valid_token(token):
        raise AccessError(description='Invalid token to message_unpin')

    message_info = get_message_info(message_id)
    if message_info == {}: # when message_info is an empty dict it means the message doesn't exist
        raise InputError(description='Message does not exist')

    if message_info['is_pinned'] is False:
        raise InputError(description='Message is not pinned')

    # only owners can pin and unpin messages
    if not is_owner(get_uid(token), message_info['channel_id']):
        raise AccessError(description='User is not an owner of the channel')
    
    channel = get_channel(message_info['channel_id'])
    for curr_message in channel['messages']:
        if curr_message['message_id'] == message_id:
            curr_message['is_pinned'] = False
    return {}

# Assumptions: Users don't have to unreact before changing their react_id
def message_react(token, message_id, react_id):
    if not is_valid_token(token):
        raise AccessError(description = "Token not valid")
    elif not is_allowed_message_id(get_uid(token), message_id):
        raise InputError(description = "Message ID not valid")
    elif not is_valid_react_id(react_id):
        raise InputError(description = "React ID not valid")
   
    message_info = get_message_info(message_id)
    # Check if the user has already reacted
    # This assumes that this react structure has been added 
    for react in message_info['reacts']:
        if react['react_id'] == react_id:
            # If the given user has reacted
            if get_uid(token) in react['u_ids']:
                raise InputError(description = "User has already reacted with this react_id")
            else:
                react['u_ids'].append(get_uid(token))
                return {}
   
    # This is run if the react structure has not been added - the first time that this react
    # is done 
    react = {
        'react_id' : react_id,
        'u_ids' : [get_uid(token)],
    }
    message_info['reacts'].append(react)
    return {}

# Assumption: spec - "Message with ID message_id does not contain an active React with ID react_id"
#   means that the given user has not reacted to that message with the given react_id
def message_unreact(token, message_id, react_id):
    if not is_valid_token(token):
        raise AccessError(description = "Token not valid")
    elif not is_valid_react_id(react_id):
        raise InputError(description = "React ID not valid")
    elif not is_allowed_message_id(get_uid(token), message_id):
        raise InputError(description = "Message ID not valid")
 
    message_info = get_message_info(message_id)     
    for react in message_info['reacts']:
        if react['react_id'] == react_id:
            if not get_uid(token) in react['u_ids']:
                raise InputError(description = "User has not reacted")
            else:
                react['u_ids'].remove(get_uid(token))
                return {}

    # If this react_id is not in the 'reacts' list - i.e. this react has not been used by anyone yet
    raise InputError(description = "React with this react_id not active")     

def message_sendlater(token, channel_id, message, time_sent):
    curr_time = int(datetime.datetime.now().timestamp())
    if not is_valid_token(token):
        raise AccessError
    elif not is_valid_channel_id(channel_id):
        raise InputError
    elif not isinstance(message, str) or not len(message) < 1000:
        raise InputError
    elif not isinstance(time_sent, int) or time_sent < curr_time:
        raise InputError
    elif not user_in_channel(get_uid(token), channel_id):
        raise AccessError

    interval = time_sent - curr_time
    # Set the time for message_send function
    message = threading.Timer(interval, message_send, [token, channel_id, message])
    message.start()
    message.join()
   
    return {'message_id' : hp.get_last_message(channel_id)['message_id']} 

