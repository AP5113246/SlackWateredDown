import pytest
from datetime import datetime

from standup import standup_start, standup_active, standup_send
from message_test import setup
from error import InputError, AccessError

RUNTIME = 3
INVALID_CHANNEL_ID = 100
TEST_MESSAGE = "Testing, 1, 2, 3"
INVALID_MESSAGE = TEST_MESSAGE * 1000

# starting a standup and testing that standup_active and standup_start have the same finish information
def test_standup_start():
    # setup for tests, see message_test for details
    info = setup()

    standup = standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)
    active_info = standup_active(info['user1']['token'], info['channel1']['channel_id'])
    assert active_info['is_active'] == True
    assert active_info['time_finish'] == standup['time_finish']

# testing that standup_active returns false when there is no active standup in a channel
def test_standup_inactive():
    # setup for tests, see message_test for details
    info = setup()

    active_info = standup_active(info['user1']['token'], info['channel1']['channel_id'])
    assert active_info['is_active'] == False

# although it's hard to be precise when testing the timer since running the program will take time
# I'm checking that it is greater than or equal to account for this
def test_standup_time():
    # setup for tests, see message_test for details
    info = setup()

    end_time = datetime.now().timestamp() + RUNTIME

    standup = standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)
    assert standup['time_finish'] >= end_time

# trying to start a standup with a standup already running in the channel
def test_standup_currently_running():
    # setup for tests, see message_test for details
    info = setup()

    standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)
    with pytest.raises(InputError):
        standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)

# starting a standup in a channel that doesn't exist
def test_standup_start_channel_doesnt_exist():
    info = setup()

    with pytest.raises(InputError):
        standup_start(info['user1']['token'], INVALID_CHANNEL_ID, RUNTIME)

# checking if a standup is active in a channel that doesn't exist
def test_standup_active_channel_doesnt_exist():
    info = setup()

    with pytest.raises(InputError):
        standup_active(info['user1']['token'], INVALID_CHANNEL_ID)

# sending a message to a standup in a channel that doesn't exist
def test_standup_send_channel_doesnt_exist():
    info = setup()

    with pytest.raises(InputError):
        standup_send(info['user1']['token'], INVALID_CHANNEL_ID, TEST_MESSAGE)

# sending a message to a standup in a channel that has no active standup
def test_standup_send_inactive():
    info = setup()

    with pytest.raises(InputError):
        standup_send(info['user1']['token'], info['channel1']['channel_id'], TEST_MESSAGE)

# sending a message which is too long
def test_standup_send_message_too_long():
    info = setup()

    standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)
    with pytest.raises(InputError):
        standup_send(info['user1']['token'], info['channel1']['channel_id'], INVALID_MESSAGE)
 
# sending a message to a startup in a channel the user is not a member of
def test_standup_send_user_not_member():
    info = setup()

    standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)
    with pytest.raises(AccessError): # user 2 is not a member of channel 1
        standup_send(info['user2']['token'], info['channel1']['channel_id'], TEST_MESSAGE)

# sending a message to a standup currently running and recieving no message
def test_standup_send_normal():
    info = setup()

    standup_start(info['user1']['token'], info['channel1']['channel_id'], RUNTIME)
    # assuming that if standup_send returns normally then everything worked properly
    assert standup_send(info['user1']['token'], info['channel1']['channel_id'], TEST_MESSAGE) == {}
    assert standup_send(info['user3']['token'], info['channel1']['channel_id'], TEST_MESSAGE) == {}