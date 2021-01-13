from data  import DATA
from error import InputError, AccessError
from user import user_profile
import helper as hp

def channel_invite(token, channel_id, u_id):
    '''            
        AccessError if:
        - invalid token

        InputError if:
        - invalid channel
        - invalid u_id
        - returns without changing data
    '''

    if not hp.is_valid_token(token):
        raise AccessError(description = "Invalid token")
    elif not hp.is_valid_channel_id(channel_id):
        raise InputError(description = "Invalid channel_id")
    elif not hp.is_valid_uid(u_id):
        raise InputError(description = "Invalid u_id")
    elif not hp.user_in_channel(hp.get_uid(token), channel_id):
        raise AccessError(description = "Unauthorised invite")

    user_added = False

    if not hp.user_in_channel(u_id, channel_id):
        for channel in DATA['channels']:
            if channel['channel_id'] == channel_id:
                info = hp.get_user(u_id)
                # Ensure that information was collected
                if info == None or not hp.is_valid_uid(info['u_id']):
                    raise InputError(description = "u_id information not found")
                # Create a new_user dictionary
                new_user = {
                        'u_id': info['u_id'],
                        'name_first': info['name_first'],
                        'name_last': info['name_last'],
                        # 'user_email': info['email'],
                        'profile_img_url' : info['profile_img_url']
                }
                # Add this user to the list of users in the channels 'all_members' section
                channel['all_members'].append(new_user)
                user_added = True
                break
        # Add this channel to the users list of channels
        if user_added:
            for user in DATA['users']:
                if user['u_id'] == u_id:
                    user['channels'].append(channel_id)
                    return {}
    else:   # User is already in the channel
        raise AccessError(description = "User already in channel")

def channel_details(token, channel_id):
    '''
        AccessError if:
        - invalid token
        - 'token' user is not in channel
        InputError if:
        - invalid channel
        - returns without changing data
    '''
    
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_channel_id(channel_id):
        raise InputError(description='Channel id is invalid')
    elif not hp.user_in_channel(hp.get_uid(token), channel_id):
        raise AccessError(description='You must be a member of the channel to view its details')

    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            return {
                'name'          : channel['name'],
                'owner_members' : channel['owner_members'],
                'all_members'   : channel['all_members'],
            }
    raise InputError(description='Error has occurred in channel_details')

def channel_messages(token, channel_id, start):
    '''
        AccessError if:
        - invalid token
        - 'token' user is not in channel
        InputError if:
        - invalid channel
        - start is greater than total messages
    '''
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif  not hp.is_valid_channel_id(channel_id):
        raise InputError(description='Channel id is invalid')
    elif not hp.user_in_channel(hp.get_uid(token), channel_id):
        raise AccessError(description='User not in channel')

    chan_messages = hp.get_messages(channel_id)
    if start > len(chan_messages):
        raise InputError(description='Invalid start to messages')

    # If the start value is -ve, assume it's 0
    if start < 0:
        start = 0

    if len(chan_messages) < 50:
        end = len(chan_messages)
        end_return = -1
    else:
        end = 50
        end_return = start + 50
    
    # pagination
    end = start + 50
    if end > len(chan_messages):
        end = len(chan_messages)
        
    message_list = []
    # This assumes that messages are listed in order of when they are sent
    for message_num in range(start, end):
        # Generates 'is_this_user_reacted' and adds it to the dictionary 
        reacts = chan_messages[message_num]['reacts']
        for react in reacts:
            # If the user's u_id is in the list of u_id's, then they have reacted
            react['is_this_user_reacted'] = hp.get_uid(token) in react['u_ids']
        
        info = {
            'message_id'    : chan_messages[message_num]['message_id'], 
            'u_id'          : chan_messages[message_num]['u_id'],
            'message'       : chan_messages[message_num]['message'],
            'time_created'  : chan_messages[message_num]['time_created'],
            'reacts'        : reacts,
            'is_pinned'     : chan_messages[message_num]['is_pinned'],
        }
        message_list.append(info)

    # Sort the message_list
    message_list_sorted = sorted(message_list, key=lambda i: i['message_id'], reverse=True)
    
    return {
        'messages'  : message_list_sorted,
        'start'     : start,
        'end'       : end_return,
    }

def channel_leave(token, channel_id):
    '''
        AccessError if:
        - invalid token
        - 'token' user is not in channel
        InputError if:
        - invalid channel
        - returns without changing data
    '''
    #channel_id = int(channel_id)
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_channel_id(channel_id):
        raise InputError(description='Channel id is invalid')
    elif not hp.user_in_channel(hp.get_uid(token), channel_id):
        raise AccessError(description='User is not in channel')

    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            for owner in channel['owner_members']:
                if owner['u_id'] == hp.get_uid(token):
                    channel['owner_members'].remove(owner)
                    break
            for member in channel['all_members']:
                if member['u_id'] == hp.get_uid(token):
                    channel['all_members'].remove(member)
                    hp.get_user(hp.get_uid(token))['channels'].remove(channel_id)
                    return {}
                
    raise InputError(description = "Error leaving the channel")

def channel_join(token, channel_id):
    '''
        AccessError if:
        - invalid token
        - not global user and private channel
        - returns without changing data
        InputError if:
        - invalid channel
    '''

    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_channel_id(channel_id):
        raise InputError(description='Channel id is invalid')
    elif hp.user_in_channel(hp.get_uid(token), channel_id):
        raise AccessError(description='User already in channel')
    elif hp.public_chan(channel_id) or hp.is_owner_permission(hp.get_uid(token)):
        for channel in DATA['channels']:
            if channel['channel_id'] == channel_id:
                user = hp.get_user(hp.get_uid(token))
                user_info = {
                    'u_id'      : user['u_id'],
                    'name_first': user['name_first'],
                    'name_last' : user['name_last'],
                    # 'user_email': user['email'],
                    'profile_img_url' : user['profile_img_url']
                }
                channel['all_members'].append(user_info)
                user['channels'].append(channel_id)
                return {}
    else:
        raise AccessError(description='Error has occurred in channel_join')

def channel_addowner(token, channel_id, u_id):
    '''
        AccessError if:
        - invalid token
        - user is already in channel
        - 'token' user is not an owner of the channel
        InputError if:
        - invalid channel
        - invalid u_id
        - returns without changing data
    '''

    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_channel_id(channel_id):
        raise InputError(description='Channel id is invalid')
    elif not hp.is_valid_uid(u_id):
        raise InputError(description='User id is invalid')
    elif hp.is_owner_permission(hp.get_uid(token)) and not hp.user_in_channel(hp.get_uid(token), channel_id):
        raise InputError(description='Global flockr owner is not a member of the channel.')
    elif not hp.is_owner(hp.get_uid(token), channel_id) and not hp.is_owner_permission(hp.get_uid(token)):
        raise AccessError(description='You are not an owner of the channel or a flockr owner')
    elif hp.is_owner(u_id, channel_id):
        raise InputError(description='That user is already an owner of this channel.')

    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            user = hp.get_user(u_id)
            user_info = {
                'u_id'      : user['u_id'],
                'name_first': user['name_first'],
                'name_last' : user['name_last'],
                # 'user_email': user['email'],
                'profile_img_url' : user['profile_img_url']
                
            }
            channel['owner_members'].append(user_info)
            # if using the command when the user is not a member of the channel,
            # add them into the channel
            if user_info not in channel['all_members']:
                channel['all_members'].append(user_info)
            return {}

    raise InputError(description='Error has occurred channel_addowner')
                
def channel_removeowner(token, channel_id, u_id):
    '''
        AccessError if:
        - invalid token
        - user is already in channel
        - 'token' user is not an owner of the channel or global user
        InputError if:
        - invalid channel
        - invalid u_id
        - returns without changing data
        - u_id user is not owner of channel
    '''
    #channel_id = int(channel_id)
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_channel_id(channel_id):
        raise InputError(description='Channel id is invalid')
    elif not hp.is_valid_uid(u_id):
        raise InputError(description='User id is invalid')
    elif hp.is_owner_permission(hp.get_uid(token)) and not hp.user_in_channel(hp.get_uid(token), channel_id):
        raise InputError(description='Global flockr owner is not a member of the channel.')
    elif not hp.is_owner(hp.get_uid(token), channel_id) and not hp.is_owner_permission(hp.get_uid(token)):
        raise AccessError(description='User is not an owner of the channel or flockr owner')
    elif not hp.is_owner(u_id, channel_id):
        raise InputError(description='That user is not an owner of this channel.')

    channel = hp.get_channel(channel_id)
    token_user = hp.get_user(hp.get_uid(token))
    # finds if 'token' user is a global user.
    token_is_global = hp.is_owner_permission(hp.get_uid(token))

    uid_is_owner = False # u_id user
    token_is_owner = False # token user

    for owner in channel['owner_members']:
        if owner['u_id'] == token_user['u_id']: 
            token_is_owner = True
        if owner['u_id'] == u_id:
            uid_is_owner = True
            del_owner = owner

    if not uid_is_owner:
        raise InputError(description='User with user id is not an owner of the channel')
    elif not token_is_owner and not token_is_global:
        raise AccessError(description='User with token is not an owner of the channel or global owner')
    elif token_is_owner or token_is_global and uid_is_owner:
        channel['owner_members'].remove(del_owner)
        return {}

    raise InputError(description='Error has occurred channel_owner')
