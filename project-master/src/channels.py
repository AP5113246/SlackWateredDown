from data import DATA
from error import InputError

# TODO: check for invalid token
# in each channel
def channels_list(token):
    for users in DATA['users']:
        if users['token'] == token:
            my_channels = users['channels']

    channel_info = list(filter(lambda channel: channel['channel_id'] in my_channels, DATA['channels']))
    return {
        'channels' : channel_info,
    }

def channels_listall(token):
    return {
        'channels': DATA['channels'],
    }

def channels_create(token, name, is_public):

    if len(name) > 20:
        raise InputError('Channel name is too long')
    
    max_id = -1
    for channel in DATA['channels']:
        if channel['channel_id'] > max_id:
            max_id = channel['channel_id']
    
    new_id = max_id + 1
    for user in DATA['users']:
        if user['token'] == token:
            u_id    = user['u_id']
            u_fname = user['name_first']
            u_lname = user['name_last']
            #u_email = user['email']
            u_prof_url = user['profile_img_url']
            user['channels'].append(new_id)

    new_channel = {
        'channel_id': new_id,
        'name'      : name,
        'is_public' : is_public,
        'owner_members': [
                    {
                        'u_id'      : u_id,
                        'name_first': u_fname,
                        'name_last' : u_lname,
                        #'user_email': u_email,
                        'profile_img_url' : u_prof_url
                    }
                ],
        'all_members': [
                    {
                        'u_id'      : u_id,
                        'name_first': u_fname,
                        'name_last' : u_lname,
                        #'user_email': u_email,
                        'profile_img_url' : u_prof_url
                    }
                ],
        'messages': [],
    }

    DATA['channels'].append(new_channel)

    return {
        'channel_id': new_id,
    }

