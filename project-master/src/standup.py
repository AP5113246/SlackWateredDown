from datetime import datetime
import threading

from data import DATA
from error import InputError, AccessError
from helper import is_valid_channel_id, user_in_channel, is_owner_permission, get_uid, get_user, get_standup
from message import message_send

def standup_start(token, channel_id, length):

    if not is_valid_channel_id(channel_id):
        raise InputError(description='Invalid channel_id')
    elif standup_active(token, channel_id)['is_active'] == True:
        raise InputError(description='Standup currently running')

    time_finish = datetime.now().timestamp() + length
    threading.Timer(length, standup_finish, [channel_id]).start() # starting the timer for the standup

    new_standup = {
        'channel_id': channel_id,
        'author_token': token,
        'time_finish': time_finish,
        'message': "",
    }
    DATA['standups'].append(new_standup)

    return {
        'time_finish': time_finish,
    }

def standup_finish(channel_id):

    standup = get_standup(channel_id)
    if standup != None: # if standup exists
        message_send(standup['author_token'], standup['channel_id'], standup['message'])
        DATA['standups'].remove(standup)

def standup_active(token, channel_id):

    if not is_valid_channel_id(channel_id):
        raise InputError(description='Invalid channel_id')

    standup = get_standup(channel_id)
    if standup != None:
        return {
            'is_active': True,
            'time_finish': standup['time_finish'],
        }
    
    # no standup has been found in the standup dictionary in DATA
    return {
        'is_active': False,
        'time_finish': None,
    }

def standup_send(token, channel_id, message):
    
    if not is_valid_channel_id(channel_id):
        raise InputError(description='Invalid channel_id')
    elif standup_active(token, channel_id)['is_active'] == False:
        raise InputError(description='Standup not currently running')
    elif not user_in_channel(get_uid(token), channel_id):
        raise AccessError(description='User not in channel')

    user = get_user(get_uid(token))
    standup = get_standup(channel_id)
    new_message = standup['message'] + f"{user['name_first']}{user['name_last']}: {message}\n"

    if len(new_message) > 1000:
        raise InputError(description='Standup exceeded 1000 characters')
    else:
        standup['message'] = new_message

    return {}