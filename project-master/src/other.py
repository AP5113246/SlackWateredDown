from data import DATA 
import helper as hp
from user import user_profile
from error import AccessError, InputError

def clear():
    for list_data in DATA.values():
        # inbuilt function for clearing lists
        list_data.clear()
    
def users_all(token):
    if not hp.is_valid_token(token):
        raise AccessError('Token is invalid')   

    # this is more correct but no time to check it
    '''
    data_list = []
    for user in DATA['users']:
        user_info =
        {
            'u_id'      : user['u_id'],
            'name_first': user['name_first'],
            'name_last' : user['name_last'],
            'email': user['email'],
            'profile_img_url' : user['profile_img_url']
        }
        data_list.append(user_info)
    return {'users' : data_list}
    '''

    return {'users' : DATA['users']}

def admin_userpermission_change(token, u_id, permission_id):
    if not hp.is_valid_token(token):
        raise AccessError(description = "Invalid token")
    elif not hp.is_valid_uid(u_id):
        raise InputError(description = "Invalid u_id")
    elif not hp.is_valid_permission_id(permission_id):
        raise InputError(description = "Invalid permission_id")
    elif not hp.is_owner_permission(hp.get_uid(token)):
        raise AccessError(description = "User is not an owner")
    
    for user in DATA['users']:
        if user['u_id'] == u_id:
            user['permission_id'] = permission_id
            return {}

    raise InputError(description = "u_id not found")

def search(token, query_str):

    if not hp.is_valid_token(token):
        raise AccessError(description = "Invalid token")

    messages = []
    user = hp.get_user(hp.get_uid(token))
    
    for channel in user['channels']:
        if hp.user_in_channel(user['u_id'], channel):
            for message in hp.get_channel(channel)['messages']:
                if hp.is_valid_query(query_str) and message['message'].lower().find(query_str.lower()) > -1:
                    # Add is_this_user_reacted to the react dictionary
                    for react in message['reacts']:
                        # If their u_id is in the list of u_id's, then they have reacted
                        react['is_this_user_reacted'] = hp.get_uid(token) in react['u_ids']
                    messages.append(message)

    # code used here: https://www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-lambda-function/
    messages = sorted(messages, key = lambda i: i['message_id'], reverse=True)
    return {'messages': messages}
