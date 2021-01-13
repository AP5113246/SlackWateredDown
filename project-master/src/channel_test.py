import pytest

from error import InputError, AccessError
from data import DATA
import channel
from other import clear
from message import message_send
import auth
import channels
import helper as hp

#test channel details returns u_id, first name and last name
def test_channel_details_first_member():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    result = channel.channel_details(user1['token'], channel1['channel_id'])

    assert result['name'] == 'FIRST_CHANNEL'
    assert result['owner_members'][0]['name_first'] == 'John'
    assert result['all_members'][0]['u_id'] == user1['u_id']
    assert result['all_members'][0]['name_first'] == 'John'
    assert result['all_members'][0]['name_last'] == 'Smith'

#test channel details can store more than 1 member
def test_channel_details_second_member():
    clear()
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    auth.auth_logout(user2['token'])
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    channel.channel_invite(user1['token'], channel1['channel_id'], user2['u_id'])
    result = channel.channel_details(user1['token'], channel1['channel_id'])

    assert result['name'] == 'FIRST_CHANNEL'
    assert result['all_members'][1]['u_id'] == user2['u_id']
    assert result['all_members'][1]['name_first'] == 'Johny'
    assert result['all_members'][1]['name_last'] == 'Smithy'

#test channel_join adds user to 'all_members'
def test_channel_join_sucess():
    clear()
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    auth.auth_logout(user2['token'])
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_login('john.smith2@gmail.com', 'validP4ss2')
    channel.channel_join(user2['token'], channel1['channel_id'])
    result = channel.channel_details(user2['token'], channel1['channel_id'])
    
    assert result['name'] == 'FIRST_CHANNEL'
    # these tests are not blackbox
    assert result['all_members'][1]['u_id'] == user2['u_id']
    assert result['all_members'][1]['name_first'] == 'Johny'
    assert result['all_members'][1]['name_last'] == 'Smithy'
    assert len(result['all_members']) == 2

#test channel_messages returns messages, starting and ending
def test_channel_messages_single():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    message_send(user1['token'], channel1['channel_id'], 'Hello')
    mess = channel.channel_messages(user1['token'], channel1['channel_id'], 0)
    assert mess['messages'][0]['message'] == 'Hello'
    assert mess['start'] == 0
    assert mess['end'] == -1

def test_channel_messages_fail():
    clear()
    
    #Invalid token
     

#test channel_leave removes user from 'all_members'
def test_channel_leave_sucess():
    clear()
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    auth.auth_logout(user2['token'])
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_login('john.smith2@gmail.com', 'validP4ss2')
    channel.channel_join(user2['token'], channel1['channel_id'])
    result = channel.channel_details(user2['token'], channel1['channel_id'])

    assert len(result['all_members']) == 2
    channel.channel_leave(user2['token'], channel1['channel_id'])
    auth.auth_logout(user2['token'])
    user1 = auth.auth_login('john.smith@gmail.com', 'validP4ss')
    result = channel.channel_details(user1['token'], channel1['channel_id'])

    assert len(result['all_members']) == 1

#tests channel_addowner add extra owner
def test_channel_addowner_second_owner():
    clear()
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    auth.auth_logout(user2['token'])
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'SECOND_CHANNEL', True)
    channel.channel_addowner(user1['token'], channel1['channel_id'], user2['u_id'])
    result = channel.channel_details(user1['token'], channel1['channel_id'])
    assert result['owner_members'][1]['name_first'] == 'Johny'
    assert len(result['owner_members']) == 2

#test channel_removeowner removes user from 'owner_members'
def test_channel_removeowner_second_owner():
    clear()
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    auth.auth_logout(user2['token'])
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'SECOND_CHANNEL', True)
    channel.channel_addowner(user1['token'], channel1['channel_id'], user2['u_id'])
    channel.channel_removeowner(user1['token'], channel1['channel_id'], user2['u_id'])
    result = channel.channel_details(user1['token'], channel1['channel_id'])
    assert len(result['owner_members']) == 1

#test input error in channel_details, when channel_id is wrong
def test_channel_details_input_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_details(user1['token'], 22)

#test access error in channel_details, when user is not a member
def test_channel_details_access_error():
    clear()
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    auth.auth_logout(user2['token'])
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', False)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_login('john.smith2@gmail.com', 'validP4ss2')
    with pytest.raises(AccessError):
        channel.channel_details('token', channel1['channel_id'])
        channel.channel_details(user2['token'], channel1['channel_id'])

#test channel_messages with invalid channel id
def test_channel_messages_input_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    message_send(user1['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        channel.channel_messages(user1['token'], 22, 0)
    
#test channel_join with incorrect channel_id
def test_channel_join_input_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_join(user1['token'], 1)

#test access error when joining private channel
def test_channel_join_access_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', False)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    with pytest.raises(AccessError):
        # invalid token
        channel.channel_join('token', channel1['channel_id'])        
        channel.channel_join(user2['token'], channel1['channel_id'])

#test channel_leave with incorrect channel_id
def test_channel_leave_input_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    with pytest.raises(InputError):
        # invalid channel id
        channel.channel_leave(user1['token'], 1)
        # invalid token
        channel.channel_leave('token', 1)
#test access error when leaving private channel
def test_channel_leave_access_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', False)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    with pytest.raises(AccessError):
        channel.channel_leave('token', channel1['channel_id'])
        channel.channel_leave(user2['token'], channel1['channel_id'])

#### test channel_addowner ####
def test_channel_addowner_input_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    user2 = auth.auth_register('jsmith@gmail.com', 'validP4ss', 'John', 'Smith')
    # incorrect channel_id
    with pytest.raises(InputError):
        channel.channel_addowner(user1['token'], 22, user1['u_id'])
    # invalid u_id
    with pytest.raises(InputError):
        channel.channel_addowner(user1['token'], channel1['channel_id'], 'u_id')

    # add user2 as owner to the channel
    channel.channel_addowner(user1['token'], channel1['channel_id'], user2['u_id'])
    
    # user2 is already an owner
    with pytest.raises(InputError):
        channel.channel_addowner(user1['token'], channel1['channel_id'], user2['u_id'])

    # user1 is flockr owner but not in channel
    channel.channel_leave(user1['token'], channel1['channel_id'])

    user3 = auth.auth_register('jminh@gmail.com', 'validP4ss', 'John', 'Smith')
    channel.channel_invite(user2['token'], channel1['channel_id'], user3['u_id'])
    # user1 is flockr owner but not in channel
    with pytest.raises(InputError):
        channel.channel_addowner(user1['token'], channel1['channel_id'], user3['u_id'])

    # sucess for add owner
    channel.channel_join(user1['token'], channel1['channel_id'])
    assert channel.channel_addowner(user1['token'], channel1['channel_id'], user3['u_id']) == {}

#test channel_addowner error when adding owner as non member
def test_channel_addowner_access_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', False)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    with pytest.raises(AccessError):
        channel.channel_addowner('token', channel1['channel_id'], user1['u_id'])
        channel.channel_addowner(user2['token'], channel1['channel_id'], user1['u_id'])

#test channel_removeowner with incorrect channel_id
def test_channel_removeowner_input_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', True)
    user2 = auth.auth_register('jsmith@gmail.com', 'validP4ss', 'John', 'Smith')
    # incorrect channel_id
    with pytest.raises(InputError):
        channel.channel_removeowner(user1['token'], 22, user1['u_id'])
    # invalid u_id
    with pytest.raises(InputError):
        channel.channel_removeowner(user1['token'], channel1['channel_id'], 'u_id')

    # add user2 as member to the channel
    channel.channel_invite(user1['token'], channel1['channel_id'], user2['u_id'])
    # user2 is not an owner
    with pytest.raises(InputError):
        # user2 cannot be removed owner
        channel.channel_removeowner(user1['token'], channel1['channel_id'], user2['u_id'])
        # user1 cannot be removed owner        
        channel.channel_removeowner(user2['token'], channel1['channel_id'], user1['u_id'])


    # user2 is an owner
    channel.channel_addowner(user1['token'], channel1['channel_id'], user2['u_id'])
    # user1 is flockr owner but not in channel
    channel.channel_leave(user1['token'], channel1['channel_id'])

    # user1 is flockr owner but not in channel
    with pytest.raises(InputError):
        channel.channel_removeowner(user1['token'], channel1['channel_id'], user2['u_id'])

    # success when removing owner
    channel.channel_join(user1['token'], channel1['channel_id'])
    assert channel.channel_removeowner(user1['token'], channel1['channel_id'], user2['u_id']) == {}

#test remove owner failed when not a member
def test_channel_removeowner_access_error():
    clear()
    user1 = auth.auth_register('john.smith@gmail.com', 'validP4ss', 'John', 'Smith')
    channel1 = channels.channels_create(user1['token'], 'FIRST_CHANNEL', False)
    auth.auth_logout(user1['token'])
    user2 = auth.auth_register('john.smith2@gmail.com', 'validP4ss2', 'Johny', 'Smithy')
    with pytest.raises(AccessError):
        channel.channel_removeowner('token', channel1['channel_id'], user1['u_id'])
        channel.channel_removeowner(user2['token'], channel1['channel_id'], user1['u_id'])

#test channel_invite with valid input
def test_channel_invite_single():
    clear()
    # Make users
    user1 = auth.auth_register("testuser1@gmail.com", "password1", "Jake", "Peralta")
    user2 = auth.auth_register("testuser2@gmail.com", "password99", "Amy", "Santiago")
    # user1 creates a channel
    channel1 = channels.channels_create(user1['token'], "BestChannel", False)
    # Ensure that the channel has only one user
    assert len(DATA['channels'][0]['all_members']) == 1
    # user1 invites user2 to their channel
    assert channel.channel_invite(user1['token'], channel1['channel_id'], user2['u_id']) == {}
    # Assert that user1 channel has 2 members in 'all_members'
    result = channel.channel_details(user1['token'], channel1['channel_id'])
    assert len(result['all_members']) == 2
    # Ensure that user2 is in that channel
    assert hp.user_in_channel(user2['u_id'], channel1['channel_id'])

def test_channel_invite_multiple():
    # This tests is when two seperate users own their own channel, then are
    # invited to another channel
    # Set-Up
    clear()
    user1 = auth.auth_register("testuser1@gmail.com", "password1", "Jake", "Peralta")
    user2 = auth.auth_register("testuser2@gmail.com", "password99", "Amy", "Santiago")
    
    chan1 = channels.channels_create(user1['token'], "User1's Channel", False)
    chan2 = channels.channels_create(user2['token'], "User2's Channel", False)

    # Invite user1 to chan2 and user2 to chan1
    assert channel.channel_invite(user1['token'], chan1['channel_id'], user2['u_id']) == {}
    assert channel.channel_invite(user2['token'], chan2['channel_id'], user1['u_id']) == {}

    # Ensure that the data was changed
    assert hp.user_in_channel(user1['u_id'], chan1['channel_id'])
    assert hp.user_in_channel(user1['u_id'], chan2['channel_id'])
    assert hp.user_in_channel(user2['u_id'], chan1['channel_id'])
    assert hp.user_in_channel(user2['u_id'], chan2['channel_id'])

#test channel_invite with incorrect channel_id
def test_channel_invite_invalid_channel_id():
    clear()
    # Make the users
    user1 = auth.auth_register("boyledpotatoes@gmail.com", "password", "Charles", "Boyle")
    user2 = auth.auth_register("worse@gmail.com", "deathbyballet", "Rosa", "Diaz")
    with pytest.raises(InputError):
        # As user1, invite user 2 into a channel that doesn't exist
        channel.channel_invite(user1['token'], "notarealchannelid", user2['u_id'])

#test channel_invite with incorrect u_id
def test_channel_invite_invalid_uid():
    clear()
    # Make the users
    user1 = auth.auth_register("boyledpotatoes@gmail.com", "password", "Raymond", "Holt")
    # Make the channel
    channel1 = channels.channels_create(user1['token'], "BestChannel", False)
    with pytest.raises(InputError):
        # As user1, invite an invalid user to their channel
        channel.channel_invite(user1['token'], channel1['channel_id'], "invalid u_id")

#test channel_invite where owner invites themself into the channel
def test_channel_invite_already_in():
    # Test owner inviting themself
    clear()
    user1 = auth.auth_register("testmail@hotmail.com", "qwerty123", "Cheddar", "Dog")
    channel1 = channels.channels_create(user1['token'], "Precinct 99", False)
    with pytest.raises(AccessError):
        channel.channel_invite('token', channel1['channel_id'], user1['u_id'])
        channel.channel_invite(user1['token'], channel1['channel_id'], user1['u_id'])

    # Test owner inviting same person twice
    user2 = auth.auth_register("freemail@yahoo.com", "123pass", "Fried", "Egg")
    assert len(channel.channel_invite(user1['token'], channel1['channel_id'], user2['u_id'])) == 0
    with pytest.raises(AccessError):
        channel.channel_invite(user1['token'], channel1['channel_id'], user2['u_id'])

#test channel_invite where user invitee is not in the channel
def test_channel_invite_unauthorised_invite():
    clear()
    user1 = auth.auth_register("cerealbox@gmail.com", "qwerty123", "Test", "one")
    user2 = auth.auth_register("ricebubbles@hotmail.com", "qwerty123", "Testuser", "two")
    user3 = auth.auth_register("cornflakes@yahoo.com", "qwerty123", "teStUser3", "three")
    channel1 = channels.channels_create(user1['token'], "Breakfast Food", False)
    with pytest.raises(AccessError):
        channel.channel_invite(user2['token'], channel1['channel_id'], user3['u_id'])    

#test channel_invite for empty token, channel_id and u_id
def test_channel_invite_empty():
    # Test all variables as empty
    clear()
    user1 = auth.auth_register("testmail@yahoo.com", "football00", "Lionel", "Messi")
    user2 = auth.auth_register("testing@juliuscaesar.com", "Cereal!123", "Martin", "Luther")
    # user1 creates a channel, where there is only 1 member and 1 owner
    channel1 = channels.channels_create(user1['token'], 'Barcelona FC', False)

    # Empty token
    with pytest.raises(AccessError):
        channel.channel_invite('', channel1['channel_id'], user2['u_id'])
    # Ensure that user2 was not added to that channel
    result = channel.channel_details(user1['token'], channel1['channel_id'])
    assert len(result['all_members']) == 1

    # Empty channel_id
    with pytest.raises(InputError):
        channel.channel_invite(user1['token'], '', user2['u_id'])
    # Ensure user2 was not added to user1's channel
    result = channel.channel_details(user1['token'], channel1['channel_id'])
    assert len(result['all_members']) == 1

    # Empty u_id
    with pytest.raises(InputError):
        channel.channel_invite(user1['token'], channel1['channel_id'], '')
    # Ensure no users were added to user1's channel
    result = channel.channel_details(user1['token'], channel1['channel_id'])
    assert len(result['all_members']) == 1


def test_boost_coverage():
    clear()
    user1 = auth.auth_register("testmail@yahoo.com", "football00", "Lionel", "Messi")
    user2 = auth.auth_register("testing@juliuscaesar.com", "Cereal!123", "Martin", "Luther")
    # user1 creates a channel, where there is only 1 member and 1 owner
    channel1 = channels.channels_create(user1['token'], 'Barcelona FC', True)
    
    # testing channel details for a user not in the channel
    with pytest.raises(AccessError):
        channel.channel_details(user2['token'], channel1['channel_id'])

    # invalid token channel_messages
    with pytest.raises(AccessError):
        channel.channel_messages('token', channel1['channel_id'], 0)

    # user not in channel and calls channel_messages
    with pytest.raises(AccessError):
        channel.channel_messages(user2['token'], channel1['channel_id'], 0)

    # calling the start of channel_messages further than max messages
    with pytest.raises(InputError):
        channel.channel_messages(user1['token'], channel1['channel_id'], 10)

    # channel leave when user not in channel
    with pytest.raises(AccessError):
        channel.channel_leave(user2['token'], channel1['channel_id'])  

    # joining a channel when already a member
    with pytest.raises(AccessError):
        channel.channel_join(user1['token'], channel1['channel_id'])  
    
    channel.channel_join(user2['token'], channel1['channel_id'])  

    with pytest.raises(AccessError):
        channel.channel_addowner(user2['token'], channel1['channel_id'], user2['u_id'])