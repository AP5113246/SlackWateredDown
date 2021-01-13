import pytest
from channels import channels_list, channels_listall, channels_create
from channel import channel_join
from auth import auth_login, auth_register
from error import InputError
from other import clear
from data import DATA

def test_channels_list_empty(): # listing when there are no channels
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channels = channels_list(user_token)['channels']
    assert len(channels) == 0

def test_channels_list_single_channel(): # listing only 1 channel
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_id = channels_create(user_token, 'test channel', True)['channel_id']

    channels = channels_list(user_token)['channels']
    assert len(channels) == 1
    for channel in channels:
        assert channel['channel_id'] == channel_id

def test_channels_list_multiple_channels(): # listing multiple channels
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_ids = []
    channel_ids.append(channels_create(user_token, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 2', True)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 3', True)['channel_id'])

    channels = channels_list(user_token)['channels']
    assert len(channels) == 3
    for channel in channels:
        assert channel['channel_id'] in channel_ids

def test_channels_list_filter_channels(): # testing filering out channels that the user is not a member off
    clear()
    user1 = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token1 = user1['token']
    user2 = auth_register('z5309113@gmail.com', 'qwert123', 'Aaron', 'Shek')
    user_token2 = user2['token']

    channel1 = channels_create(user_token1, 'test channel 1', True)['channel_id']
    channel2 = channels_create(user_token2, 'test channel 2', True)['channel_id']
    channel3 = channels_create(user_token2, 'test channel 3', True)['channel_id']
    channels = channels_list(user_token1)['channels']
    assert len(channels) == 1
    for channel in channels:
        assert channel['channel_id'] == channel1
    
    channels = channels_list(user_token2)['channels']   
    print(channels)
    assert len(channels) == 2
    for channel in channels:
        assert channel['channel_id'] == channel2 or channel3

def test_channels_list_not_owner(): # testing listing channels when the user is not the owner 
    clear()
    user1 = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token1 = user1['token']
    user2 = auth_register('z5309113@gmail.com', 'qwert123', 'Aaron', 'Shek')
    user_token2 = user2['token']

    channel_ids = []
    channel_ids.append(channels_create(user_token1, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token1, 'test channel 2', True)['channel_id'])
    channel_ids.append(channels_create(user_token1, 'test channel 3', True)['channel_id'])

    for channel in channel_ids:
        channel_join(user_token2, channel)

    channels = channels_list(user_token2)['channels']
    assert len(channels) == 3
    for channel in channels:
        assert channel['channel_id'] in channel_ids

def test_channels_list_public_and_private(): # testing that the is_public data does not affect listing
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_ids = []
    channel_ids.append(channels_create(user_token, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 2', False)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 3', True)['channel_id'])

    channels = channels_list(user_token)['channels']
    assert len(channels) == 3
    for channel in channels:
        assert channel['channel_id'] in channel_ids

def test_channels_listall_empty(): # listing all channels when there is none
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    all_channels = channels_listall(user_token)['channels']
    assert len(all_channels) == 0

def test_channels_listall_single_channel(): # listing a single channel
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_id = channels_create(user_token, 'test channel', True)['channel_id']

    all_channels = channels_listall(user_token)['channels']
    assert len(all_channels) == 1
    for channel in all_channels:
        assert channel['channel_id'] == channel_id

def test_channels_listall_multiple_channels(): # listing multiple channels
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_ids = []
    channel_ids.append(channels_create(user_token, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 2', True)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 3', True)['channel_id'])

    all_channels = channels_listall(user_token)['channels']
    assert len(all_channels) == 3
    for channel in all_channels:
        assert channel['channel_id'] in channel_ids

def test_channels_listall_multiple_owners(): # listing when channels are all owned by users
    clear()
    user1 = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token1 = user1['token']
    user2 = auth_register('z5309113@gmail.com', 'qwert123', 'Aaron', 'Shek')
    user_token2 = user2['token']

    channel_ids = []
    channel_ids.append(channels_create(user_token1, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token1, 'test channel 2', True)['channel_id'])
    channel_ids.append(channels_create(user_token2, 'test channel 3', True)['channel_id'])

    all_channels = channels_listall(user_token1)['channels']
    assert len(all_channels) == 3
    for channel in all_channels:
        assert channel['channel_id'] in channel_ids

def test_channels_listall_multiple_users(): # listing when there are channels which users are a part of, but don't own
    clear()
    user1 = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token1 = user1['token']
    user2 = auth_register('z5309113@gmail.com', 'qwert123', 'Aaron', 'Shek')
    user_token2 = user2['token']

    channel_ids = []
    channel_ids.append(channels_create(user_token1, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token1, 'test channel 2', True)['channel_id'])
    channel_ids.append(channels_create(user_token1, 'test channel 3', True)['channel_id'])

    for channel in channel_ids:
        channel_join(user_token2, channel)
    
    all_channels = channels_listall(user_token1)['channels']
    assert len(all_channels) == 3
    for channel in all_channels:
        assert channel['channel_id'] in channel_ids

def test_channels_listall_public_and_private(): # testing is_public data doesn't affect listing
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_ids = []
    channel_ids.append(channels_create(user_token, 'test channel 1', True)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 2', False)['channel_id'])
    channel_ids.append(channels_create(user_token, 'test channel 3', True)['channel_id'])

    all_channels = channels_listall(user_token)['channels']
    assert len(all_channels) == 3
    for channel in all_channels:
        assert channel['channel_id'] in channel_ids

# tests for channels_create -> creates a channel and sets the current user as a member

def test_channels_create_simple(): # simple creation of a channel
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channels = channels_list(user_token)['channels']

    assert len(channels) == 0
    channel_id = channels_create(user_token, 'test channel', True)['channel_id']

    channels = channels_list(user_token)['channels']
    assert len(channels) == 1
    for channel in channels:
        assert channel['channel_id'] == channel_id

def test_channels_create_length_edgecase(): # channel with name of 20 characters
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_id = channels_create(user_token, 'this is 20characters', True)['channel_id']

    channels = channels_list(user_token)['channels']
    assert len(channels) == 1
    for channel in channels:
        assert channel['channel_id'] == channel_id

def test_channels_create_name_too_long(): # channel name over 20 chars
    clear()
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    with pytest.raises(InputError):
        assert channels_create(user_token, 'more than 20 characters', True)

def test_channels_create_public_and_private():
    clear()
    # checking that is_public data is registered correctly
    user = auth_register('z5317148@gmail.com', 'password', 'Will', 'Dahl')
    user_token = user['token']
    channel_id1 = channels_create(user_token, 'test channel 1', True)['channel_id']
    channel_id2 = channels_create(user_token, 'test channel 2', False)['channel_id']

    all_channels = channels_list(user_token)['channels']
    assert len(all_channels) == 2
    for channel in all_channels:
        if channel['channel_id'] is channel_id1:
            assert channel['is_public'] == True
        elif channel['channel_id'] is channel_id2:
            assert channel['is_public'] == False
