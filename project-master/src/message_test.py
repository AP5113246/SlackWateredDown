import pytest
import threading
import datetime
import time
from auth import auth_register
from message import (
    message_send,
    message_remove,
    message_edit,
    message_react,
    message_unreact,
    message_pin,
    message_unpin,
    message_sendlater,
)
from channels import channels_create
from channel import channel_invite, channel_leave
from other import clear
from error import InputError, AccessError
import helper as hp

# Simple setup
def setup():
    clear()
    # Creates three users
    user1 = auth_register("user1@gmail.com", "P455w04d!", "Rick", "Sanchez")
    user2 = auth_register("user2@gmail.com", "PassingCloud", "Morty", "Smith")
    user3 = auth_register("user3@gmail.com", "CerealB0x3s!", "Beth", "Smith")
    # Creates a channel where user1 is the owner
    channel1 = channels_create(user1['token'], "The Citadel", False)
    # Adds user3 as a member of the channel
    channel_invite(user1['token'], channel1['channel_id'], user3['u_id'])

    # User1 is the owner of a channel that User3 is a member of, and User2
    # is in no channels

    return {
        "user1": user1,
        "user2": user2,
        "user3": user3,
        "channel1": channel1,
    }

### message_send ###

# testing normal use case (no errors)
def test_message_send_valid():
    info = setup()
    message = "Hello World!"
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], message)
    assert len(m_id) == 1
    assert str(m_id['message_id']) # We can test this as is because as long as the 
                                   # message_id isn't empty, this is true

#  Test message less than 1000 characters
def test_message_send_over_1000():
    info = setup()
    message = "Hi" * 501
    with pytest.raises(InputError):
        assert message_send(info['user1']['token'], info['channel1']['channel_id'], message)

#  Invalid / Unauthorized token
def test_message_send_unauthorised():
    info = setup()
    message = "Captain Wuntch. Good to see you. But if you’re here, who’s guarding Hades?"
    with pytest.raises(AccessError):
        # Testing invalid token
        message_send("invalidtoken@hotmail.com", info['channel1']['channel_id'], message)
        # Testing unauthorized token
        message_send(info['user2']['token'], info['channel1']['channel_id'], message)
        # Testing invalid channel_id
        message_send(info['user1']['token'], -1287, message)

#  Sending data of different types (int, float, dict, list etc)
def test_message_send_invalid_types():
    info = setup()
    valid_message = "This is a message"
    # List of invalid token types, channel_id types and message types
    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]

    invalid_channel_types = [
        [0],
        1.03,
        "0",
        {"channel_id": 0},
    ]

    invalid_message_types = [
        ["Message here"],
        10,
        10.07,
        {"message": "This is my message"},
    ]

    for token in invalid_token_types:
        with pytest.raises(AccessError):
            message_send(token, info['channel1']['channel_id'], valid_message)
    for channel in invalid_channel_types:
        with pytest.raises(InputError):
            assert message_send(info['user1']['token'], channel, valid_message)
    for message in invalid_message_types:
        with pytest.raises(InputError):
            message_send(info['user1']['token'], info['channel1']['channel_id'], message)

#  Sending empty variables (token, channel id, message)
def test_message_send_empty():
    info = setup()
    with pytest.raises(AccessError):
        assert message_send(None, info['channel1']['channel_id'], "Message...")
    with pytest.raises(InputError):
        assert message_send(info['user1']['token'], None, "Message...")
    # Assumption: on a failed message_send, it returns a 'None' message_id unless an error is raised
    message = ""
    assert message_send(info['user1']['token'], info['channel1']['channel_id'], message)['message_id'] != None 

### message_remove ###

# Testing normal use case (no errors)
def test_message_remove_valid():
    info = setup()
    # Owner sends and removes his own message
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_remove(info['user1']['token'], m_id1['message_id']) == {}
    # Member sends and removes his own message
    m_id2 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_remove(info['user3']['token'], m_id2['message_id']) == {}
    # Member sends a message, and owner removes it
    m_id3 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_remove(info['user1']['token'], m_id3['message_id']) == {}

# Message_id doesn't exist - Fail (InputError)
def test_message_remove_invalid_id():
    info = setup()
    # message_id doesn't exist
    with pytest.raises(InputError):
        message_remove(info['user1']['token'], 100)

    # Create a message, remove it, then remove it again
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "First message")
    assert message_remove(info['user1']['token'], m_id['message_id']) == {}
    with pytest.raises(InputError):
        message_remove(info['user1']['token'], m_id['message_id'])

# Message_id exists, but the token that sent it isn't authorised
def test_message_remove_invalid_token():
    info = setup()
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "First message")
    with pytest.raises(AccessError):
        # User3 (member) attempts to remove user1's (owner) message
        message_remove(info['user3']['token'], m_id['message_id'])
        # User2 (not in channel) attempts to remove user1's message
        message_remove(info['user2']['token'], m_id['message_id'])
        # Invalid token attempts to remove the message from user1
        message_remove('invalid_tokennnnnn', m_id['message_id'])

# Empty token and message id causing errors
def test_message_remove_empty():
    info = setup()
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "First")
    # Empty token (invalid token)
    with pytest.raises(AccessError):
        message_remove('', m_id['message_id'])
    # Empty message_id (invalid message_id)
    with pytest.raises(InputError):
        message_remove(info['user1']['token'], '')

# Sending data of different types (int, float, dict, list etc)
def test_message_remove_invalid_types():
    info = setup()

    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]

    invalid_message_id_types = [
        ["1-13"],
        10,
        10.103,
        {"message_id": "1-0"},
    ]
    
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Message...")
    for token in invalid_token_types:
        with pytest.raises(AccessError): # Theoretically, the message shouldn't be deleted
            message_remove(token, m_id['message_id'])

    for message_id in invalid_message_id_types:
        with pytest.raises(InputError):
            message_remove(info['user1']['token'], message_id)

### message_edit ###

# Testing normal use case (no errors)
def test_message_edit_valid():
    info = setup()
    # Owner sends and edits his own message
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_edit(info['user1']['token'], m_id1['message_id'], 'Message is changed') == {}
    # Member sends and edits his own message
    m_id2 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_edit(info['user3']['token'], m_id2['message_id'], 'This has been editted') == {}
    # Member sends a message, and owner edits it
    m_id3 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_edit(info['user1']['token'], m_id3['message_id'], 'Hello!') == {}

# Testing invalid message_id
def test_message_edit_invalid_id():
    info = setup()
    # message_id doesn't exist
    with pytest.raises(InputError):
        message_edit(info['user1']['token'], 100, "change this message")

    # Create a message, remove it, then edit it
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "First message")
    assert message_remove(info['user1']['token'], m_id['message_id']) == {}
    with pytest.raises(InputError):
        message_edit(info['user1']['token'], m_id['message_id'], "no longer exists")

# Testing editing messages without the permission
def test_message_edit_invalid_token():
    info = setup()
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "First message")
    with pytest.raises(AccessError):
        # User3 (member) attempts to edit user1's (owner) message
        message_edit(info['user3']['token'], m_id['message_id'], "Change this message")
        # User2 (not in channel) attempts to edit user1's message
        message_edit(info['user2']['token'], m_id['message_id'], "Change this message")
        # Invalid token attempts to edit the message from user1
        message_edit('invalid_tokennnnnn', m_id['message_id'], "Change this message")

# Testing editing messages to be over the character limit
def test_message_edit_invalid_message():
    info = setup()
    # owner sends a message and edits it to be over 1000 characters
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Message here...")
    long_message = "A " + ("long " * 500) + "message"
    with pytest.raises(InputError):
        message_edit(info['user1']['token'], m_id1['message_id'], long_message)

# Testing that editing a message to be "" deletes the message
def test_message_edit_empty():
    info = setup()
    # Owner sends and removes his own message
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Original Message")
    assert message_edit(info['user1']['token'], m_id1['message_id'], '') == {}
    with pytest.raises(InputError): # testing that the message no longer exists
        message_edit(info['user1']['token'], m_id1['message_id'], 'editting it again')
    # Member sends and removes his own message
    m_id2 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_edit(info['user3']['token'], m_id2['message_id'], '') == {}
    with pytest.raises(InputError): # testing that the message no longer exists
        message_edit(info['user3']['token'], m_id2['message_id'], 'Edit #2')
    
    # Member sends a message, and owner removes it
    m_id3 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Message here...")
    assert message_edit(info['user1']['token'], m_id3['message_id'], "") == {}
    with pytest.raises(InputError): # testing that the message no longer exists
        message_edit(info['user1']['token'], m_id3['message_id'], "Hello!")

#### message_react ####
def test_message_react_pass():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")
    
    # First react
    assert message_react(info['user3']['token'], message_id['message_id'], 1) == {} # Thumbs up
    # Ensure that the message has that react saved
    reacts = hp.get_message_info(message_id['message_id'])['reacts']
    assert info['user3']['u_id'] in reacts[0]['u_ids'] 
    assert reacts[0]['react_id'] == 1

    # Second react
    assert message_react(info['user1']['token'], message_id['message_id'], 1) == {} # Thumbs up
    # Ensure that the user was added to the u_ids that reacted
    reacts = hp.get_message_info(message_id['message_id'])['reacts']
    assert info['user1']['u_id'] in reacts[0]['u_ids']
    assert len(reacts[0]['u_ids']) == 2

def test_message_react_already_reacted():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")
   
    # First react 
    assert message_react(info['user3']['token'], message_id['message_id'], 1) == {} # Thumbs up
    # Ensure that the message has that react saved
    reacts = hp.get_message_info(message_id['message_id'])['reacts']
    assert info['user3']['u_id'] in reacts[0]['u_ids'] 
    assert reacts[0]['react_id'] == 1

    # Second react
    with pytest.raises(InputError):
        message_react(info['user3']['token'], message_id['message_id'], 1) # Thumbs up
    
    # Reacting to their own message twice
    message_id2 = message_send(info['user3']['token'], info['channel1']['channel_id'], "Hello!")
    # First time
    assert message_react(info['user3']['token'], message_id2['message_id'], 1) == {} # Thumbs up
    # Second time
    with pytest.raises(InputError):
        message_react(info['user3']['token'], message_id2['message_id'], 1) # Thumbs up
    
def test_message_react_invalid_variables():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")
       
    # Invalid react_id
    invalid_react_ids = [
        0,
        2,
        -1,
        ["1"],
        1.07,
        {'react_id' : 1},
        None,
    ]
    for react in invalid_react_ids:
        with pytest.raises(InputError):
            message_react(info['user3']['token'], message_id['message_id'], react)
        
    # Invalid message_id
    invalid_message_ids = [
        -1,
        ["0"],
        1.034,
        None,
    ]
    for inv_message_id in invalid_message_ids:
        with pytest.raises(InputError):
            message_react(info['user3']['token'], inv_message_id, 1)
        
def test_message_react_unauthorised():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")

    # User 2 is not in the channel, therefore they cannot react
    with pytest.raises(InputError):
        message_react(info['user2']['token'], message_id['message_id'], 1)

    # User 3 leaves the channel, then tries to like the message
    channel_leave(info['user3']['token'], info['channel1']['channel_id'])
    with pytest.raises(InputError):
        message_react(info['user3']['token'], message_id['message_id'], 1)

#### message_unreact ####
def test_message_unreact_pass():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")
    message_react(info['user1']['token'], message_id['message_id'], 1)
    # Ensure the react was successful
    m_info = hp.get_message_info(message_id['message_id'])
    assert len(m_info['reacts'][0]['u_ids']) == 1
   
    # Unreact
    assert message_unreact(info['user1']['token'], message_id['message_id'], 1) == {}
    m_info = hp.get_message_info(message_id['message_id'])
    # Ensure unreact was successful
    assert len(m_info['reacts'][0]['u_ids']) == 0

def test_message_unreact_already_unreacted():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")
    message_react(info['user1']['token'], message_id['message_id'], 1)
    # Ensure the react was successful
    m_info = hp.get_message_info(message_id['message_id'])
    assert len(m_info['reacts'][0]['u_ids']) == 1

    # Unreact
    assert message_unreact(info['user1']['token'], message_id['message_id'], 1) == {}
    m_info = hp.get_message_info(message_id['message_id'])
    # Ensure unreact was successful
    assert len(m_info['reacts'][0]['u_ids']) == 0
    
    # Second unreact
    with pytest.raises(InputError):
        message_unreact(info['user1']['token'], message_id['message_id'], 1)

    # Other user (React then unreact twice) - Not message sender   
    message_react(info['user3']['token'], message_id['message_id'], 1)
    message_unreact(info['user3']['token'], message_id['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(info['user3']['token'], message_id['message_id'], 1)

def test_message_unreact_invalid_variables():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")
       
    # Invalid react_id
    invalid_react_ids = [
        0,
        2,
        -1,
        ["1"],
        1.07,
        {'react_id' : 1},
        None,
    ]
    for react in invalid_react_ids:
        with pytest.raises(InputError):
            message_unreact(info['user3']['token'], message_id['message_id'], react)
        
    # Invalid message_id
    invalid_message_ids = [
        -1,
        ["0"],
        1.034,
        None,
    ]
    for inv_message_id in invalid_message_ids:
        with pytest.raises(InputError):
            message_unreact(info['user3']['token'], inv_message_id, 1)
        
def test_message_unreact_unauthorised():
    info = setup()
    message_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Hello!")

    # User 2 is not in the channel, therefore they cannot unreact
    with pytest.raises(InputError):
        message_unreact(info['user2']['token'], message_id['message_id'], 1)

    # User 3 reacts, leaves the channel, then tries to unreact to the message
    message_react(info['user3']['token'], message_id['message_id'], 1)
    channel_leave(info['user3']['token'], info['channel1']['channel_id'])
    with pytest.raises(InputError):
        message_unreact(info['user3']['token'], message_id['message_id'], 1)

#### message_pin ####
def test_message_pin_pass():
    info = setup()
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Original Message")
    res = message_pin(info['user1']['token'], m_id1['message_id'])
    assert res == {}

def test_message_pin_error():
    info = setup()
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Original Message")
    m_id2 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Second message")
    message_pin(info['user1']['token'], m_id1['message_id'])

    with pytest.raises(InputError):
        # message id is incorrect
        message_pin(info['user1']['token'], "message_id")
    with pytest.raises(InputError):        
        # message is already pinned
        message_pin(info['user1']['token'], m_id1['message_id'])
        
    with pytest.raises(AccessError):
        # token is not a valid token
        message_pin("token", m_id2['message_id'])  
    with pytest.raises(AccessError):
        # token is not an owner of the channel
        message_pin(info['user2']['token'], m_id2['message_id'])  
    with pytest.raises(AccessError):
        # token is not a member of the channel
        message_pin(info['user3']['token'], m_id2['message_id'])        

def test_message_pin_invalid_types():
    info = setup()

    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]

    invalid_message_id_types = [
        ["1-13"],
        10,
        10.103,
        {"message_id": "1-0"},
    ]
    
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Message...")
    for token in invalid_token_types:
        with pytest.raises(AccessError): # Theoretically, the message shouldn't be deleted
            message_pin(token, m_id['message_id'])

    for message_id in invalid_message_id_types:
        with pytest.raises(InputError):
            message_pin(info['user1']['token'], message_id)

def test_message_unpin_pass():
    info = setup()
    m_id1 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Original Message")
    message_pin(info['user1']['token'], m_id1['message_id'])
    res = message_unpin(info['user1']['token'], m_id1['message_id'])
    assert res == {}

def test_message_unpin_error():
    info = setup()
    message_send(info['user1']['token'], info['channel1']['channel_id'], "First message")
    m_id2 = message_send(info['user1']['token'], info['channel1']['channel_id'], "Second message")
    message_pin(info['user1']['token'], m_id2['message_id'])

    with pytest.raises(AccessError):
        # token is not a valid token
        message_unpin("token", m_id2['message_id'])  

    with pytest.raises(AccessError):
        # token is not an owner of the channel
        message_unpin(info['user2']['token'], m_id2['message_id'])  
        
    with pytest.raises(AccessError):
        # token is not a member of the channel
        message_unpin(info['user3']['token'], m_id2['message_id'])        

    message_unpin(info['user1']['token'], m_id2['message_id'])

    with pytest.raises(InputError):
        # message id is incorrect
        message_unpin(info['user1']['token'], "message_id")
    with pytest.raises(InputError):
        # message is not pinned
        message_unpin(info['user1']['token'], m_id2['message_id'])
        
def test_message_unpin_invalid_types():
    info = setup()

    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]

    invalid_message_id_types = [
        ["1-13"],
        10,
        10.103,
        {"message_id": "1-0"},
    ]
    
    m_id = message_send(info['user1']['token'], info['channel1']['channel_id'], "Message...")
    message_pin(info['user1']['token'], m_id['message_id'])
    for token in invalid_token_types:
        with pytest.raises(AccessError): # Theoretically, the message shouldn't be deleted
            message_unpin(token, m_id['message_id'])

    for message_id in invalid_message_id_types:
        with pytest.raises(InputError):
            message_unpin(info['user1']['token'], message_id)


def test_coverage_boost():
    clear()
    user1 = auth_register("user1@gmail.com", "P455w04d!", "Rick", "Sanchez")
    user2 = auth_register("user2@gmail.com", "PassingCloud", "Morty", "Smith")
    user3 = auth_register("user3@gmail.com", "CerealB0x3s!", "Beth", "Smith")
    # Creates a channel where user1 is the owner
    channel1 = channels_create(user1['token'], "The Citadel", False)
    # Adds user3 as a member of the channel
    channel_invite(user1['token'], channel1['channel_id'], user3['u_id'])
    # User1 is the owner of a channel that User3 is a member of, and User2
    # is in no channels

    # send a message when not in channel
    with pytest.raises(AccessError):
        message_send(user2['token'], channel1['channel_id'], 'testmessage')
    
    mid1 = message_send(user1['token'], channel1['channel_id'], 'testmessage')
    with pytest.raises(AccessError):
        # invalid token
        message_remove('token', mid1['message_id'])

    with pytest.raises(AccessError):
        # invalid token
        message_edit('token', mid1['message_id'], "hello")

    with pytest.raises(AccessError):
        # invalid token
        message_react('token', mid1['message_id'], 1)
        
    with pytest.raises(AccessError):
        # invalid token
        message_unreact('token', mid1['message_id'], 1)

#### message_sendlater ####
def test_message_sendlater_pass():
    info = setup()
    curr_time = int(datetime.datetime.now().timestamp())
    time_sent = curr_time + 1    

    m1 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "Hello", time_sent)
    # Ensure that the return variable are correct
    assert len(m1) == 1
    assert 'message_id' in m1.keys()
    # Ensure that the time is correct
    assert hp.get_message_info(m1['message_id'])['time_created'] == time_sent

    # Send multiple messages
    curr_time = int(datetime.datetime.now().timestamp())
    time_sent = curr_time + 1
    m1 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "m1", time_sent)
    m2 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "m2", time_sent)
    m3 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "m3", time_sent)
    m4 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "m4", time_sent)
    m5 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "m5", time_sent)
    m6 = message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "m6", time_sent)

    assert m6['message_id'] > m5['message_id'] and hp.get_message_info(m6['message_id'])['message'] == "m6"
    assert m5['message_id'] > m4['message_id'] and hp.get_message_info(m5['message_id'])['message'] == "m5"
    assert m4['message_id'] > m3['message_id'] and hp.get_message_info(m4['message_id'])['message'] == "m4"
    assert m3['message_id'] > m2['message_id'] and hp.get_message_info(m3['message_id'])['message'] == "m3"
    assert m2['message_id'] > m1['message_id'] and hp.get_message_info(m2['message_id'])['message'] == "m2"

def test_message_sendlater_invalid():
    info = setup()
    curr_time = int(datetime.datetime.now().timestamp())

    # Invalid times
    invalid_time_sent = [
        "right now",
        str(curr_time + 1),
        curr_time - 3,
        [curr_time],
        None,
    ]
    for time_sent in invalid_time_sent:
        with pytest.raises(InputError):
            message_sendlater(info['user1']['token'], info['channel1']['channel_id'], "Hello!", time_sent)

    # Invalid message
    invalid_message_types = [
        ["Message here"],
        10,
        10.07,
        {"message": "This is my message"},
        None,
    ]
    for message in invalid_message_types:
        with pytest.raises(InputError):
            message_sendlater(info['user1']['token'], info['channel1']['channel_id'], message, curr_time + 1)
             
    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]
    for token in invalid_token_types:
        with pytest.raises(AccessError):
            message_sendlater(token, info['channel1']['channel_id'], "Hi", curr_time + 2)

    invalid_channel_types = [
        [0],
        1.03,
        "0",
        {"channel_id": 0},
    ]
    for channel in invalid_channel_types:
        with pytest.raises(InputError):
            message_sendlater(info['user1']['token'], channel, "Hi", curr_time + 1)

