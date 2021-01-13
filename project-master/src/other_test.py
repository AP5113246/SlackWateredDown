import pytest

from data import DATA
from auth import auth_register
from channels import channels_create
from channel import channel_invite
from message import message_send
from other import search, clear, admin_userpermission_change, users_all
from error import AccessError, InputError

import helper as hp

def test_users_all():
    # Set-up
    clear()
    user = auth_register('mscott@gmail.com', 'dundermifflin', 'Michael', 'Scott')
    # Invalid token
    inv_tokens = ["thisisnotatoken", 8, 982.23, [user['token']], {'token':user['token']}, None]

    for tok in inv_tokens:
        with pytest.raises(AccessError):
            users_all(tok)

    res = users_all(user['token'])
    assert len(res) == 1

#### Search tests ####

# Assumption: Case doesn't matter (i.e 'paper' will still return 'PaPeR')
def test_search_pass_single_channel():
    # Set-up
    clear()
    user = auth_register('mscott@gmail.com', 'dundermifflin', 'Michael', 'Scott')
    chan = channels_create(user['token'], 'Dunder', False)
    
    message_send(user['token'], chan['channel_id'], 'My name is Michael Scott') 
    m2 = message_send(user['token'], chan['channel_id'], 'I really enjoy paper')
    m3 = message_send(user['token'], chan['channel_id'], 'Paper is just the best')

    # Running the search
    result = search(user['token'], 'paper')

    # Ensuring the data layout is correct
    assert len(result) == 1 and 'messages' in result.keys()
    assert len(result['messages']) == 2
    assert len(result['messages'][0]) == 7
    assert 'message_id' and 'message' and 'time_created' and 'u_id' in result['messages'][0]
    print(result)
    # Ensuring that the returned data is correct
    assert result['messages'][1]['message_id'] == m2['message_id']
    assert result['messages'][0]['message_id'] == m3['message_id']

    assert result['messages'][1]['message'] == "I really enjoy paper"
    assert result['messages'][0]['message'] == "Paper is just the best"

    assert result['messages'][1]['time_created'] > 0
    assert result['messages'][0]['time_created'] > 0

    assert result['messages'][1]['u_id'] == user['u_id']
    assert result['messages'][0]['u_id'] == user['u_id']


def test_search_pass_multi_channel():
    # Set-up
    clear()
    user1 = auth_register('mscott@gmail.com', 'dundermifflin', 'Michaelo', 'Scottulos')
    user2 = auth_register('mscotty@gmail.com', 'dundermifflin', 'Michaeloe', 'Scotto')
    user3 = auth_register('mscottie@gmail.com', 'dundermifflin', 'Michaelus', 'Scott')
 
    chan1 = channels_create(user1['token'], 'Mifflin', False)
    chan2 = channels_create(user2['token'], 'MifflinSideChick', False)

    channel_invite(user1['token'], chan1['channel_id'], user2['u_id'])
    channel_invite(user1['token'], chan1['channel_id'], user3['u_id'])
    channel_invite(user2['token'], chan2['channel_id'], user1['u_id'])
    channel_invite(user2['token'], chan2['channel_id'], user3['u_id'])
 
    m1 = message_send(user1['token'], chan1['channel_id'], 'My name is Michaelo Scottulos') 
    m2 = message_send(user2['token'], chan1['channel_id'], 'Hey, my name is Michaeloe Scotto')
    message_send(user3['token'], chan1['channel_id'], 'No way, that similiar to my name')
    message_send(user1['token'], chan2['channel_id'], 'Sup ma dudes, I\'m a paper fanatic') 
    message_send(user2['token'], chan2['channel_id'], 'Yo dude, same here, I also like PAPER')
    m6 = message_send(user3['token'], chan2['channel_id'], 'Bruh same. Also, I\'m Michaelus Scott')

    # Running the search
    result = search(user2['token'], 'SCOTT')
    print(result)
    # Ensuring the returned data is correct (already checked layout in prev test)
    assert len(result['messages']) == 3
    assert result['messages'][2]['message_id'] == m1['message_id']
    assert result['messages'][2]['message'] == "My name is Michaelo Scottulos"
    assert result['messages'][2]['time_created'] > 0
    assert result['messages'][2]['u_id'] == user1['u_id']

    assert result['messages'][1]['message_id'] == m2['message_id']
    assert result['messages'][1]['message'] == "Hey, my name is Michaeloe Scotto"
    assert result['messages'][1]['time_created'] > 0
    assert result['messages'][1]['u_id'] == user2['u_id']

    assert result['messages'][0]['message_id'] == m6['message_id']
    assert result['messages'][0]['message'] == "Bruh same. Also, I'm Michaelus Scott"
    assert result['messages'][0]['time_created'] > 0
    assert result['messages'][0]['u_id'] == user3['u_id']

def test_search_invalid_arg():
    # Set-up
    clear()
    user = auth_register('mscott@gmail.com', 'dundermifflin', 'Michael', 'Scott')
    chan = channels_create(user['token'], 'Dunder Mifflin Chat', False)
    
    message_send(user['token'], chan['channel_id'], 'My name is Michael Scott') 
    message_send(user['token'], chan['channel_id'], 'I really enjoy paper')
    message_send(user['token'], chan['channel_id'], 'Paper is just the best')

    # Invalid token
    inv_tokens = ["thisisnotatoken", 8, 982.23, [user['token']], {'token':user['token']}, None]

    for tok in inv_tokens:
        with pytest.raises(AccessError):
            search(tok, "paper")

    # Invalid query string
    inv_queries = ["zebra", "papercompany", 783, 76.23, ["paper"], {'paper': 'scott'}, None]

    for query in inv_queries:
        assert len(search(user['token'], query)['messages']) == 0

def test_search_empty_arg():
    # Set-up
    clear()
    user = auth_register('mscott@gmail.com', 'dundermifflin', 'Michael', 'Scott')
    chan = channels_create(user['token'], 'Dunder Mifflin Chat', False)
    
    message_send(user['token'], chan['channel_id'], 'My name is Michael Scott') 
    message_send(user['token'], chan['channel_id'], 'I really enjoy paper')
    message_send(user['token'], chan['channel_id'], 'Paper is just the best')

    # Empty token
    with pytest.raises(AccessError):
        search("", "paper")

    # Empty query string
    assert len(search(user['token'], "")['messages']) == 0

#### User permission change ####
def test_admin_userpermission_change_pass():
    # Set-Up
    clear()
    user1 = auth_register("google@gmail.com", "SearchMe", "Google", "Incorporated")
    user2 = auth_register("hotmail@gmail.com", "IDontHaveUsers", "Hotmail", "Incorporated")

    # Ensure their initial permission id's are correct
    assert DATA['users'][1]['permission_id'] == 2
    assert DATA['users'][0]['permission_id'] == 1
    
    # Ensure that the return result from the function is correct
    assert admin_userpermission_change(user1['token'], user2['u_id'], 1) == {}
    
    # Ensure that the data was changed
    assert DATA['users'][1]['permission_id'] == 1

def test_admin_userpermission_change_fail():
    # Set-Up
    clear()
    user1 = auth_register("google@gmail.com", "SearchMe", "Google", "Incorporated")
    user2 = auth_register("hotmail@gmail.com", "IDontHaveUsers", "Hotmail", "Incorporated")
    user3 = auth_register("yahoo@gmail.com", "ISuckBad", "Yahoo", "Incorporated")

    # Invalid permissions (user is not authorised)
    with pytest.raises(AccessError):
        admin_userpermission_change(user2['token'], user3['u_id'], 1)

    # Invalid u_id
    inv_uid = [-1, "1", [1], 1.05, {'u_id': 1}]
    for uid in inv_uid:
        with pytest.raises(InputError):
            admin_userpermission_change(user1['token'], uid, 1)

    # Invalid permission_id (permission_id not a valid value)
    inv_permission = [3, 0, 1.59, "1", [1], {'permission_id':1}]
    for permission in inv_permission:
        with pytest.raises(InputError):
            admin_userpermission_change(user1['token'], user2['u_id'], permission)

    # Invalid token
    inv_token = ["token", 1, 1.5, [user1['token']], {'token': user1['token']}]
    for token in inv_token:
        with pytest.raises(AccessError):
            admin_userpermission_change(token, user2['u_id'], 1)
    
    # Empty variables
    with pytest.raises(AccessError):
        # token
        admin_userpermission_change("", user2['u_id'], 1)
    with pytest.raises(InputError):
        # u_id
        admin_userpermission_change(user1['token'], int, 1)
    with pytest.raises(InputError):
        # permission_id
        admin_userpermission_change(user1['token'], user2['u_id'], int)
 
