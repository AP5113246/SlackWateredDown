''' Below are the tests for server.py
    Our test are done using a url pytest fixture'''
from time import sleep,time
import json 
import re
from subprocess import Popen, PIPE
import signal
import pytest
import requests
from echo_http_test import url

ACCESS_ERROR = 403
INPUT_ERROR = 400
SUCCESS = 200 



'''
Tests for Iteration 3 
'''

def test_message_sendlater(url):
    # Register user
    user_info = {'email':'joerogan@gmail.com', 'password':'ElkMeAT', 'name_first':'Joe', 'name_last':'Rogan'}
    user_request = requests.post(url+'/auth/register', json=(user_info))
    user = user_request.json()
    # Creates a channel where user1 is the owner
    channel_info = {'token':user['token'],'name':"The JRE Podcast",'is_public':True}
    channel_request = requests.post(url+'/channels/create',json=(channel_info))
    channel = channel_request.json()

    message_info = {'token':user['token'],'channel_id':channel['channel_id'],'message':'Hello World! I like elk meat :)','time_sent':time()+2}
    message_sendlater = requests.post(url+'/message/sendlater', json=(message_info))
    assert message_sendlater.status_code == 200
 
   
   
def test_message_reactions(url):
    '''
    Tests will see if a user and an invitee can react and unreact messages in a channel
    '''

    # Register user
    user_info = {'email':'joerogan@gmail.com', 'password':'ElkMeAT', 'name_first':'Joe', 'name_last':'Rogan'}
    user_request = requests.post(url+'/auth/register', json=(user_info))
    user = user_request.json()
    assert user_request.status_code == 200
    # Creates a channel where user1 is the owner
    channel_info = {'token':user['token'],'name':"The JRE Podcast",'is_public':True}
    channel_request = requests.post(url+'/channels/create',json=(channel_info))
    channel = channel_request.json()
    assert channel_request.status_code == 200

    message = "Hello World! I like Elk meat!"
    message_info = {'token':user['token'],'channel_id':channel['channel_id'],'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    message_payload = message_request.json()
    
    assert message_request.status_code == 200
    
    invitee_info = {'email':'conormcgregor@gmail.com', 'password':'IloveMMA', 'name_first':'Conor', 'name_last':'Mcgregor'}
    invitee_reg = requests.post(url+'/auth/register', json = invitee_info)
    invitee = invitee_reg.json()
    assert invitee_reg.status_code == 200
    
    invite_info = {'token':user['token'],'channel_id':channel['channel_id'],'u_id':invitee['u_id']}
    invite_connor = requests.post(url+'/channel/invite', json=(invite_info))
    assert invite_connor.status_code == 200

    user_react_info = {'token':user['token'],'message_id': message_payload['message_id'],'react_id': 1}
    send_react = requests.post(url+'/message/react', json=(user_react_info))
    assert send_react.status_code == 200
    
    invitee_react_info = {'token':invitee['token'],'message_id': message_payload['message_id'],'react_id': 1}
    send_react = requests.post(url+'/message/react', json=(invitee_react_info))
    assert send_react.status_code == 200
    
    ''' --NOTE: 0 is an invalid react_id
    invitee_unreact_info = {'token':invitee['token'],'message_id': message_payload['message_id'],'react_id': 0}
    send_react = requests.post(url+'/message/unreact', json=(invitee_unreact_info))
    assert send_react.status_code == 200
    
    user_unreact_info = {'token':user['token'],'message_id': message_payload['message_id'],'react_id': 0}
    send_unreact = requests.post(url+'/message/unreact', json=(user_unreact_info))
    assert send_unreact.status_code == 200
    '''
    
def test_message_pins(url):
    '''
    Tests if owner can pin and unpin messages succesfully and invitee can't pin message
    '''
    # Register user
    user_info = {'email':'joerogan@gmail.com', 'password':'ElkMeAT', 'name_first':'Joe', 'name_last':'Rogan'}
    user_request = requests.post(url+'/auth/register', json=(user_info))
    user = user_request.json()
    assert user_request.status_code == 200
    # Creates a channel where user1 is the owner
    channel_info = {'token':user['token'],'name':"The JRE Podcast",'is_public':True}
    channel_request = requests.post(url+'/channels/create',json=(channel_info))
    channel = channel_request.json()
    assert channel_request.status_code == 200

    message = "Hello World! I like Elk meat!"
    message_info = {'token':user['token'],'channel_id':channel['channel_id'],'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    message_payload = message_request.json()
    
    assert message_request.status_code == 200
    
    invitee_info = {'email':'conormcgregor@gmail.com', 'password':'IloveMMA', 'name_first':'Conor', 'name_last':'Mcgregor'}
    invitee_reg = requests.post(url+'/auth/register', json = invitee_info)
    invitee = invitee_reg.json()
    assert invitee_reg.status_code == 200
    
    invite_info = {'token':user['token'],'channel_id':channel['channel_id'],'u_id':invitee['u_id']}
    invite_connor = requests.post(url+'/channel/invite', json=(invite_info))
    assert invite_connor.status_code == 200
    #Should be 200 codes
    user_pin_info = {'token':user['token'], 'message_id': message_payload['message_id']}
    pin_message = requests.post(url+'/message/pin', json = (user_pin_info))
    assert pin_message.status_code == 200
    
    user_unpin_info = {'token':user['token'], 'message_id': message_payload['message_id']}
    unpin_message = requests.post(url+'/message/unpin', json = (user_unpin_info))
    unpin_message.status_code == 200

    #Should be access error because invitee is not an owner of channel
    user_pin_info = {'token':invitee['token'], 'message_id': message_payload['message_id']}
    pin_message = requests.post(url+'/message/pin', json = (user_pin_info))
    assert pin_message.status_code == 403


def test_auth_pass_request_reset(url):


    # Register user
    user_info = {'email':'joerogan@gmail.com', 'password':'ElkMeAT', 'name_first':'Joe', 'name_last':'Rogan'}
    user_request = requests.post(url+'/auth/register', json=(user_info))
    assert user_request.status_code == 200
    request_info = {'email':'joerogan@gmail.com'}
    request_reset = requests.post(url+'/auth/passwordreset/request', json=(request_info))
    assert request_reset.status_code == 200
    
    # testing an invalid reset code
    reset_info = {'reset_code':'thisisasecretcode','new_password':'jrepodcastftjamie'}
    reset_pass = requests.post(url+'/auth/passwordreset/reset', json=(reset_info))
    assert reset_pass.status_code == 400

def test_standup_run(url):
    # Register user
    user_info = {'email':'joerogan@gmail.com', 'password':'ElkMeAT', 'name_first':'Joe', 'name_last':'Rogan'}
    user_request = requests.post(url+'/auth/register', json=(user_info))
    user = user_request.json()
    assert user_request.status_code == 200
    # Creates a channel where user1 is the owner
    channel_info = {'token':user['token'],'name':"The JRE Podcast",'is_public':True}
    channel_request = requests.post(url+'/channels/create',json=(channel_info))
    channel = channel_request.json()
    assert channel_request.status_code == 200
    
    invitee_info = {'email':'conormcgregor@gmail.com', 'password':'IloveMMA', 'name_first':'Conor', 'name_last':'Mcgregor'}
    invitee_reg = requests.post(url+'/auth/register', json = invitee_info)
    invitee = invitee_reg.json()
    assert invitee_reg.status_code == 200
    
    invite_info = {'token':user['token'],'channel_id':channel['channel_id'],'u_id':invitee['u_id']}
    invite_connor = requests.post(url+'/channel/invite', json=(invite_info))
    assert invite_connor.status_code == 200
    
    start_standup_info = {'token':user['token'],'channel_id':channel['channel_id'],'length': 45}
    start_standup = requests.post(url+'/standup/start', json=(start_standup_info))
    assert start_standup.status_code == 200
   
    #The standup/active and standup/send functions should work for both users of the channel 
    standup_active_info = {'token':user['token'],'channel_id':channel['channel_id']}
    check_active_owner = requests.get(url+'/standup/active', params = (standup_active_info))
    assert check_active_owner.status_code == 200 

    standup_active_info = {'token':invitee['token'],'channel_id':channel['channel_id']}
    check_active_member = requests.get(url+'/standup/active', params = (standup_active_info))
    assert check_active_member.status_code == 200     
    
    standup_send_info = {'token':user['token'],'channel_id':channel['channel_id'],'message':'Hey Conor welcome to the podcast'}
    send_standup_owner = requests.post(url+'/standup/send', json = (standup_send_info))
    assert send_standup_owner.status_code == 200
    
    standup_send_info = {'token':invitee['token'],'channel_id':channel['channel_id'],'message':'Hey Joe, glad to be here :)'}
    send_standup_invitee = requests.post(url+'/standup/send', json=standup_send_info)
    assert send_standup_invitee.status_code == 200
    
def test_user_profile_photo(url):
    # Register user
    user_info = {'email':'joerogan@gmail.com', 'password':'ElkMeAT', 'name_first':'Joe', 'name_last':'Rogan'}
    user_request = requests.post(url+'/auth/register', json=user_info)
    user = user_request.json()
    assert user_request.status_code == 200
    image_url = 'https://pbs.twimg.com/media/EmG9CpFXIAEs0SG?format=jpg&name=large'
    photo_upload_info = {'token':user['token'],'img_url': image_url,'x_start':0,'y_start':0,'x_end':450,'y_end':361}
    upload_photo = requests.post(url+'/user/profile/uploadphoto',json=photo_upload_info)
    assert upload_photo.status_code == 200
    
    
   
   

'''
Tests for Auth Functions
'''
def test_auth_register(url):
    '''Checks to see if user is registered'''
    register_user = {'email':'valid@gmail.com', 'password':'validP4ss', 'name_first':'Jake', 'name_last':'Peralta'}
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 200

def test_auth_invalid(url):
    # invalid email
    register_user = {'email':"failedemail.com", 'password':'validP4ss', 'name_first':'Jake', 'name_last':'Peralta'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 400
    # empty password
    register_user = {'email':"failedemail.com", 'password':'', 'name_first':'Jake', 'name_last':'Peralta'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 400
    # empty first name
    register_user = {'email':"failedemail.com", 'password':'validP4ss', 'name_first':'', 'name_last':'Peralta'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 400
    # empty last name
    register_user = {'email':"failedemail.com", 'password':'validP4ss', 'name_first':'Jake', 'name_last':''} 
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 400
    # name too long
    name = "ThisIsAVeryLongNameForSomeoneThatIsMoreThan50Characters"
    # name_first > 50 chars
    register_user = {'email':"validemail@gmail.org.au", 'password':'validP4ss', 'name_first':name, 'name_last':'Place'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 400
    # name_last > 50 chars
    register_user = {'email':"validemail@gmail.org.au", 'password':'validP4ss', 'name_first':'Martin', 'name_last':name} 
    register = requests.post(url+'/auth/register', json=(register_user))
    assert register.status_code == 400

    email_inputs = [76, 10.03, ["list@gmail.com"], {"thisisvalid@gmail.com": 'email'}]
    passw_inputs = [19, 12.1332, ["PasswordValid"], {"ValidPa45": 'Password'}]
    name_inputs = [11, 9.11, ["Eleven"], {'name_first': 'eleven'}]
    
    for in_type in email_inputs:
        register_user = {'email':in_type, 'password':'validP4ss', 'name_first':'Jake', 'name_last':'Peralta'} 
        register = requests.post(url+'/auth/register', json=(register_user))
        assert register.status_code == 400
    
    for in_type in passw_inputs:
        register_user = {'email':'validemail@gmail.com', 'password':in_type, 'name_first':'Jake', 'name_last':'Peralta'} 
        register = requests.post(url+'/auth/register', json=(register_user))
        assert register.status_code == 400

    for in_type in name_inputs:
        register_user = {'email':'validemail@gmail.com', 'password':'validpass', 'name_first':in_type, 'name_last':'Peralta'} 
        register = requests.post(url+'/auth/register', json=(register_user))
        assert register.status_code == 400

    for in_type in name_inputs:
        register_user = {'email':'validemail@gmail.com', 'password':'correctpas123', 'name_first':'Jake', 'name_last':in_type} 
        register = requests.post(url+'/auth/register', json=(register_user))
        assert register.status_code == 400

def test_auth_logout_login(url):
    '''Checks to see if user can be logged out and logged in after registering'''
    register_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'}
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload = register.json()
    assert register.status_code == 200
    #Assert it has worked and proceed to logout user
    logout_user = {'token':payload['token']}
    logout_request = requests.post(url+'/auth/logout', json=(logout_user))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] is True
    assert (logout_request).status_code == 200
    #Assert logout works and proceed to login user
    login_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters'}
    login_request = requests.post(url+'/auth/login', json=(login_user))
    assert login_request.status_code == 200
    
def test_auth_login_invalid(url):
    # invalid email
    login_user = {'email':'ianjacobsgmail.com', 'password':'Il0vetrimesters'}
    login_request = requests.post(url+'/auth/login', json=(login_user))
    assert login_request.status_code == 400
    # email not registered
    login_user = {'email':'mailmailmail@gmail.com', 'password':'Il0vetrimesters'}
    login_request = requests.post(url+'/auth/login', json=(login_user))
    assert login_request.status_code == 400

    
    register_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    requests.post(url+'/auth/register', json=(register_user))
    # email is incorrect for valid user
    login_1 = {'email':'email@gmail.com', 'password':'Il0vetrimesters'}
    login_request = requests.post(url+'/auth/login', json=(login_1))
    assert login_request.status_code == 400
    # password is incorrect for valid user
    login_2 = {'email':'ianjacobs@gmail.com', 'password':'Ihatesemesters'}
    login_request = requests.post(url+'/auth/login', json=(login_2))
    assert login_request.status_code == 400
    # empty password
    login_3 = {'email':'ianjacobs@gmail.com', 'password':''}
    login_request = requests.post(url+'/auth/login', json=(login_3))
    assert login_request.status_code == 400
    # email empty
    login_4 = {'email':'', 'password':'Ihatesemesters'}
    login_request = requests.post(url+'/auth/login', json=(login_4))
    assert login_request.status_code == 400
    login_5 = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters '}
    login_request = requests.post(url+'/auth/login', json=(login_5))
    assert login_request.status_code == 400

def test_login_multiple(url):
    log = {'email':'mail@mail.com', 'password': 'passmwd'}
    register_user = {'email':log['email'], 'password':log['password'], 'name_first':'Ian', 'name_last':'Jacobs'} # pylint: disable=C0301
    requests.post(url+'/auth/register', json=(register_user))
    requests.post(url+'/auth/login', json=(log))
    requests.post(url+'/auth/login', json=(log))
    requests.post(url+'/auth/login', json=(log))
    res = requests.post(url+'/auth/login', json=(log))
    assert res.status_code == 200

def test_auth_logout_empty(url):
    logout_request = requests.post(url+'/auth/logout', json=({'token':'mymail@gmail.com'}))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] == False
    assert (logout_request).status_code == 200

    logout_request = requests.post(url+'/auth/logout', json=({'token':''}))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] == False
    assert (logout_request).status_code == 200

def test_auth_logout_multiple(url): 
    register_user = {'email':'potato@gmail.com', 'password':'sammosaas', 'name_first':'John', 'name_last':'Jacobs'} 
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload = register.json()
    logout_user = {'token':payload['token']}
    logout_request = requests.post(url+'/auth/logout', json=(logout_user))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] == True
    assert (logout_request).status_code == 200
    logout_request = requests.post(url+'/auth/logout', json=(logout_user))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] == False
    assert (logout_request).status_code == 200
    logout_request = requests.post(url+'/auth/logout', json=(logout_user))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] == False
    assert (logout_request).status_code == 200

    requests.post(url+'/auth/login', json=({'email':'potato@gmail.com', 'password':'sammosaas'}))
    logout_request = requests.post(url+'/auth/logout', json=(logout_user))
    logout_payload = logout_request.json()
    assert logout_payload['is_success'] == True
    assert (logout_request).status_code == 200
    
def test_channels_create_public(url): 
    
    '''Test for channel_create'''
    register_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'}
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload = register.json()
    assert register.status_code == 200
    
    #Create new channel
    new_channel_details = {'token':payload['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    assert create_channel.status_code == 200

def test_channels_create_private(url): 
    
    '''Test for channel_create'''
    register_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload = register.json()
    assert register.status_code == 200
    
    #Create new channel
    new_channel_details = {'token':payload['token'], 'name':'Secret_Channel', 'is_public':False}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    assert create_channel.status_code == 200
    
    
def test_channels_list(url):
   
    '''Test for channel_create'''
    register_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'}
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload = register.json()
    assert register.status_code == 200
    #Create new channel
    new_channel_details = {'token':payload['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    assert create_channel.status_code == 200
    #List all the channels related to user/token
    list_request = payload['token']
    get_list = requests.get(url+'/channels/list',params={'token':list_request})
    assert get_list.status_code == 200

def test_channels_listall_onechannel(url):
    
    register_user = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} # pylint: disable=C0301
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload = register.json()
    assert register.status_code == 200
     #Create new channel
    new_channel_details = {'token':payload['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    assert create_channel.status_code == 200
 
    get_listall = requests.get(url+'/channels/listall',params={'token':payload['token']})
    assert get_listall.status_code == 200
    
'''
Tests for Channel Functions
'''
def test_channel_details(url):
    #Register User
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user = register.json()
    assert register.status_code == 200
    #Create channel
    new_channel_details = {'token':payload_user['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200 
    #Get details
    details_payload = {'token':payload_user['token'], 'channel_id':payload_channel['channel_id']}
    get_details = requests.get(url+'/channel/details',params=details_payload)
    assert get_details.status_code == 200
    

def test_channel_invite_leave(url):
     #Register owner
    register_owner = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    register = requests.post(url+'/auth/register', json=(register_owner))
    payload_owner = register.json()
    assert register.status_code == 200
 
     #Create new channel
    new_channel_details = {'token':payload_owner['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200  
    #Register Second user
    register_invitee = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_invitee))
    payload_invitee = register.json()
    assert register.status_code == 200
    
    invite_info = {'token':payload_owner['token'], 'channel_id':payload_channel['channel_id'], 'u_id':payload_invitee['u_id']}
    invite_user = requests.post(url+'/channel/invite', json=(invite_info))
    assert invite_user.status_code == 200
    
    #Pass the invitee's token to check if they can get details of the channel as previous asser isn't enough
    details_payload = {'token':payload_invitee['token'], 'channel_id':payload_channel['channel_id']}
    get_details = requests.get(url+'/channel/details',params=details_payload)
    assert get_details.status_code == 200
    #Get invitee to leave
    leave_info = {'token':payload_invitee['token'],'channel_id':payload_channel['channel_id']}
    leave_channel = requests.post(url+'/channel/leave',json = (leave_info))
    assert leave_channel.status_code == 200
    #Make sure invitee can't access channel details i.e a 400 error should be sent
    details_payload = {'token':payload_invitee['token'], 'channel_id':payload_channel['channel_id']}
    get_details = requests.get(url+'/channel/details',params=details_payload)
    assert get_details.status_code == 403
 
   
def test_channel_addowner_removeowner(url):
    #Register owner always has global permission
    register_owner = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    register = requests.post(url+'/auth/register', json=(register_owner))
    payload_owner = register.json()
    assert register.status_code == 200

    #Create new channel
    new_channel_details = {'token':payload_owner['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200  
    
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_addowner = register.json()
    assert register.status_code == 200
    
    add_owner_info = {'token':payload_owner['token'],'channel_id':payload_channel['channel_id'],'u_id':payload_addowner['u_id']}
    owner_add = requests.post(url+'channel/addowner', json=(add_owner_info))
    assert owner_add.status_code == 200
    
    remove_owner_info = {'token':payload_owner['token'],'channel_id':payload_channel['channel_id'],'u_id':payload_addowner['u_id']}
    owner_remove = requests.post(url+'channel/removeowner', json =(remove_owner_info))
    assert owner_remove.status_code == 200

'''
Tests for Users Functions
'''
def test_users_all(url):
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    #Send request to register user
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user_one = register.json()
    assert register.status_code == 200       
    get_all_users = requests.get(url+'/users/all',params={'token':payload_user_one['token']})
    assert get_all_users.status_code == 200
    
    register_user = {'email':'bobmarley@gmail.com', 'password':'Rastaking', 'name_first':'Bob', 'name_last':'Marley'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user_two = register.json()
    assert register.status_code == 200
    get_all_users = requests.get(url+'/users/all',params={'token':payload_user_two['token']})
    assert get_all_users.status_code == 200

def test_user_profile(url):
    register_user = {'email':'bobmarley@gmail.com', 'password':'Rastaking', 'name_first':'Bob', 'name_last':'Marley'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    user = register.json()
    info_request ={'token':user['token'],'u_id':user['u_id']} 
    profile_request = requests.get(url+'/user/profile',params=(info_request))
    assert profile_request.status_code == 200


def test_user_profile_set_functions(url):

    register_user = {'email':'bobmarley@gmail.com', 'password':'Rastaking', 'name_first':'Bob', 'name_last':'Marley'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    user_payload = register.json()
    
    name_change_info = {'token':user_payload['token'],'name_first':'Damian','name_last':'Marley'}
    change_name = requests.put(url+'/user/profile/setname', json=(name_change_info))
    assert change_name.status_code == 200
    
    email_change_info = {'token':user_payload['token'],'email':'damianmarley@gmail.com'}
    change_email = requests.put(url+'/user/profile/setemail',json=(email_change_info))
    assert change_email.status_code == 200
    
    handle_change_info = {'token':user_payload['token'],'handle_str':'Marley_Jr'}
    set_handle = requests.put(url+'/user/profile/sethandle',json=(handle_change_info))
    assert set_handle.status_code == 200
    
'''
Tests for Messages
'''
# testing normal use case (no errors)
def test_message_send_valid(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message = "Hello World!"
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 200

#  Test message less than 1000 characters
def test_message_send_over_1000(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message = "Hi" * 501
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 400

#  Invalid / Unauthorized token
def test_message_send_unauthorised(url):
    # Register users
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user2_info = {'email':'user2@gmail.com', 'password':'PassingCloud', 'name_first':'Morty', 'name_last':'Smith'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    user2_request = requests.post(url+'/auth/register', json=(user2_info))
    user2 = user2_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message = "Captain Wuntch. Good to see you. But if you’re here, who’s guarding Hades?"
    # Testing invalid token
    message_info = {'token':"invalidtoken@hotmail.com",'channel_id':channel1['channel_id'],'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 403

    # Testing unauthorized token
    message_info = {'token':user2['token'],'channel_id':channel1['channel_id'],'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 403

    # Testing invalid channel_id
    message_info = {'token':user1['token'],'channel_id':-1287,'message':message}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 400

#  Sending something data of different types (int, float, dict, list etc)
def test_message_send_invalid_types(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    
    valid_message = "This is a message"
    # Tuple of invalid token types, channel_id types and message types
    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]

    invalid_channel_types = [
        [0, 1],
        {"channel_id": 0},
    ]

    invalid_message_types = [
        ["Message here"],
        10,
        10.07,
        {"message": "This is my message"},
    ]

    for token in invalid_token_types:
        message_info = {'token':token,'channel_id':channel1['channel_id'],'message':valid_message}
        message_request = requests.post(url+'/message/send', json=(message_info))
        assert message_request.status_code == 403
    for channel in invalid_channel_types:
        message_info = {'token':user1['token'],'channel_id':channel,'message':valid_message}
        message_request = requests.post(url+'/message/send', json=(message_info))
        assert message_request.status_code == 400
    for message in invalid_message_types:
        message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':message}
        message_request = requests.post(url+'/message/send', json=(message_info))
        assert message_request.status_code == 400

#  Sending empty variables (token, channel id, message)
def test_message_send_empty(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    # empty token
    message_info = {'token':None,'channel_id':channel1['channel_id'],'message':"Message..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 403
    # empty channel_id
    message_info = {'token':user1['token'],'channel_id':None,'message':"Message..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 400
    # empty message
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':None}
    message_request = requests.post(url+'/message/send', json=(message_info))
    assert message_request.status_code == 400

### message_remove ###

# Testing normal use case (no errors)
def test_message_remove_valid(url):
    # Register users
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user3_info = {'email':'user3@gmail.com', 'password':'CerealB0x3s!', 'name_first':'Beth', 'name_last':'Smith'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    user3_request = requests.post(url+'/auth/register', json=(user3_info))
    user3 = user3_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    # Adds user3 as a member of the channel
    invite_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'u_id':user3['u_id']}
    requests.post(url+'/channel/invite',json=(invite_info))

    # Owner sends and removes his own message
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    remove_info = {'token':user1['token'],'message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 200

    # Member sends and removes his own message
    message_info = {'token':user3['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    remove_info = {'token':user3['token'],'message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 200

    # Member sends a message, and owner removes it
    message_info = {'token':user3['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    remove_info = {'token':user1['token'],'message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 200

# Message_id doesn't exist - Fail (InputError)
def test_message_remove_invalid_id(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    # message_id doesn't exist
    remove_info = {'token':user1['token'],'message_id':"100"}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 400

    # Create a message, remove it, then remove it again
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    remove_info = {'token':user1['token'],'message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 400

# Message_id exists, but the token that sent it isn't authorised
def test_message_remove_invalid_token(url):
    # Creates three users
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user2_info = {'email':'user2@gmail.com', 'password':'PassingCloud', 'name_first':'Morty', 'name_last':'Smith'}
    user3_info = {'email':'user3@gmail.com', 'password':'CerealB0x3s!', 'name_first':'Beth', 'name_last':'Smith'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    user2_request = requests.post(url+'/auth/register', json=(user2_info))
    user2 = user2_request.json()
    user3_request = requests.post(url+'/auth/register', json=(user3_info))
    user3 = user3_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    # Adds user3 as a member of the channel
    invite_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'u_id':user3['u_id']}
    requests.post(url+'/channel/invite',json=(invite_info))

    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()

    # User3 (member) attempts to remove user1's (owner) message
    remove_info = {'token':user3['token'],'message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 403

    # User2 (not in channel) attempts to remove user1's message
    remove_info = {'token':user2['token'],'message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 403
    
    # Invalid token attempts to remove the message from user1
    remove_info = {'token':'invalid_tokennnnnn','message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 403

# Empty token and message id causing errors
def test_message_remove_empty(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    # Empty token (invalid token)
    remove_info = {'token':'','message_id':payload['message_id']}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 403
    # Empty message_id (invalid message_id)
    remove_info = {'token':user1['token'],'message_id':''}
    remove_request = requests.delete(url+'/message/remove', json=(remove_info))
    assert remove_request.status_code == 400

# Sending something data of different types (int, float, dict, list etc)
def test_message_remove_invalid_types(url):
    # Register user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    invalid_token_types = [
        ["user1@gmail.com"],
        77,
        13.3478,
        {"token": "user1@gmail.com"},
    ]

    invalid_message_id_types = [
        ["1-13"],
        {"message_id": "1-0"},
    ]
    
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    for token in invalid_token_types:
        remove_info = {'token':token,'message_id':payload['message_id']}
        remove_request = requests.delete(url+'/message/remove', json=(remove_info))
        assert remove_request.status_code == 403

    for message_id in invalid_message_id_types:
        remove_info = {'token':user1['token'],'message_id':message_id}
        remove_request = requests.delete(url+'/message/remove', json=(remove_info))
        assert remove_request.status_code == 400

### message_edit ###

# Testing normal use case (no errors)
def test_message_edit_valid(url):
    # Creates three users
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user3_info = {'email':'user3@gmail.com', 'password':'CerealB0x3s!', 'name_first':'Beth', 'name_last':'Smith'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    user3_request = requests.post(url+'/auth/register', json=(user3_info))
    user3 = user3_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    # Adds user3 as a member of the channel
    invite_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'u_id':user3['u_id']}
    requests.post(url+'/channel/invite',json=(invite_info))

    # Owner sends and edits his own message
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 200
    # Member sends and edits his own message
    message_info = {'token':user3['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    edit_info = {'token':user3['token'],'message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 200
    # Member sends a message, and owner edits it
    message_info = {'token':user3['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 200

# Testing invalid message_id
def test_message_edit_invalid_id(url):
    # Creates user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    # message_id doesn't exist
    edit_info = {'token':user1['token'],'message_id':100,'message':'Message...'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 400

    # Create a message, remove it, then edit it
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    remove_info = {'token':user1['token'],'message_id':payload['message_id']}
    requests.delete(url+'/message/remove', json=(remove_info))
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 400

# Testing editing messages without the permission
def test_message_edit_invalid_token(url):
    # Creates three users
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user2_info = {'email':'user2@gmail.com', 'password':'PassingCloud', 'name_first':'Morty', 'name_last':'Smith'}
    user3_info = {'email':'user3@gmail.com', 'password':'CerealB0x3s!', 'name_first':'Beth', 'name_last':'Smith'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    user2_request = requests.post(url+'/auth/register', json=(user2_info))
    user2 = user2_request.json()
    user3_request = requests.post(url+'/auth/register', json=(user3_info))
    user3 = user3_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    # Adds user3 as a member of the channel
    invite_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'u_id':user3['u_id']}
    requests.post(url+'/channel/invite',json=(invite_info))

    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    
    # User3 (member) attempts to edit user1's (owner) message
    edit_info = {'token':user3['token'],'message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 403
    
    # User2 (not in channel) attempts to edit user1's message
    edit_info = {'token':user2['token'],'message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 403
    
     # Invalid token attempts to edit the message from user1
    edit_info = {'token':'invalid_tokennnnnn','message_id':payload['message_id'],'message':'Message is changed'}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 403

# Testing editing messages to be over the character limit
def test_message_edit_invalid_message(url):
    # Creates user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    
    # owner sends a message and edits it to be over 1000 characters
    long_message = "A " + ("long " * 500) + "message"
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':long_message}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 400

# Testing that editing a message to be "" deletes the message
def test_message_edit_empty(url):
    # Creates three users
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user3_info = {'email':'user3@gmail.com', 'password':'CerealB0x3s!', 'name_first':'Beth', 'name_last':'Smith'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    user3_request = requests.post(url+'/auth/register', json=(user3_info))
    user3 = user3_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    # Adds user3 as a member of the channel
    invite_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'u_id':user3['u_id']}
    requests.post(url+'/channel/invite',json=(invite_info))

    # Owner sends and removes his own message
    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':''}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':'edited again'} # testing that the message no longer exists
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 400

    # Member sends and removes his own message
    message_info = {'token':user3['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    edit_info = {'token':user3['token'],'message_id':payload['message_id'],'message':''}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    edit_info = {'token':user3['token'],'message_id':payload['message_id'],'message':'edited again'} # testing that the message no longer exists
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 400
    
    # Member sends a message, and owner removes it
    message_info = {'token':user3['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':''}
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':'edited again'} # testing that the message no longer exists
    edit_request = requests.put(url+'/message/edit', json=(edit_info))
    assert edit_request.status_code == 400


# Sending message data of different types (int, float, dict, list etc)
def test_message_edit_invalid_types(url):
    # Creates user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"Message here..."}
    message_request = requests.post(url+'/message/send', json=(message_info))
    payload = message_request.json()

    invalid_message_types = [
        ["Invalid"],
        10101,
        123.123,
        {"message": "this is the new message"},
    ]

    for message in invalid_message_types:
        edit_info = {'token':user1['token'],'message_id':payload['message_id'],'message':message}
        edit_request = requests.put(url+'/message/edit', json=(edit_info))
        assert edit_request.status_code == 400
     
def test_channel_messages_empty(url):
    '''Tests for messages while channel has none'''
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user = register.json()
    assert register.status_code == 200
    
    new_channel_details = {'token':payload_user['token'], 'name':'Ye_Fans', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200 
    
    messages_details = {'token':payload_user['token'],'channel_id':payload_channel['channel_id'], 'start': 0}
    channel_messages = requests.get(url+'channel/messages', params=(messages_details))
    assert channel_messages.status_code == 200 

def test_channel_messages_with_messages(url):
    '''Tests for messages while channel has none'''
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user = register.json()
    assert register.status_code == 200
    
    new_channel_details = {'token':payload_user['token'], 'name':'Ye_Fans', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200 

    message_info = {'token':payload_user['token'],'channel_id':payload_channel['channel_id'],'message':"Message here..."}
    requests.post(url+'/message/send', json=(message_info))
    message_info = {'token':payload_user['token'],'channel_id':payload_channel['channel_id'],'message':"Second message"}
    requests.post(url+'/message/send', json=(message_info))
    
    messages_details = {'token':payload_user['token'],'channel_id':payload_channel['channel_id'], 'start': 0}
    channel_messages = requests.get(url+'channel/messages', params=(messages_details))
    assert channel_messages.status_code == 200 

def test_channel_join(url):
    # Register owner
    register_owner = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    register = requests.post(url+'/auth/register', json=(register_owner))
    payload_owner = register.json()
    assert register.status_code == 200
    
    # Create new channel
    new_channel_details = {'token':payload_owner['token'], 'name':'New_Channel', 'is_public':True}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200  
    
    # Send request to register user
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_joiner = register.json()
    assert register.status_code == 200

    # User tries to join public channel
    join_info = {'token':payload_joiner['token'],'channel_id':payload_channel['channel_id']}
    join_channel = requests.post(url+'channel/join',json = (join_info))
    assert join_channel.status_code == 200

def test_channel_join_private(url):
    
    # Register owner
    register_owner = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    register = requests.post(url+'/auth/register', json=(register_owner))
    payload_owner = register.json()
    assert register.status_code == 200
    
    # Create new channel
    new_channel_details = {'token':payload_owner['token'], 'name':'New_Channel', 'is_public':False}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200  
    
    # Send request to register user
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_joiner = register.json()
    assert register.status_code == 200

    # user tries to join private channel, should fail
    join_info = {'token':payload_joiner['token'],'channel_id':payload_channel['channel_id']}
    join_channel = requests.post(url+'channel/join',json = (join_info))
    assert join_channel.status_code == 403


def test_channel_join_rejoin(url):
    
    # Register owner
    register_owner = {'email':'ianjacobs@gmail.com', 'password':'Il0vetrimesters', 'name_first':'Ian', 'name_last':'Jacobs'} 
    register = requests.post(url+'/auth/register', json=(register_owner))
    payload_owner = register.json()
    assert register.status_code == 200
    
    # Create new channel
    new_channel_details = {'token':payload_owner['token'], 'name':'New_Channel', 'is_public':False}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200  

    # Owner tries to rejoin, should fail
    join_info = {'token':payload_owner['token'],'channel_id':payload_channel['channel_id']}
    join_channel = requests.post(url+'channel/join',json = (join_info))
    assert join_channel.status_code == 403
    
def test_clear(url):
    #Register User
    register_user = {'email':'abishaiphilip@gmail.com', 'password':'Ihatetrisems', 'name_first':'Abishai', 'name_last':'Philip'} 
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user = register.json()
    assert register.status_code == 200
    
    #Create channel
    new_channel_details = {'token':payload_user['token'], 'name':'New_Channel', 'is_public':'True'}
    create_channel = requests.post(url+'/channels/create', json=(new_channel_details))
    payload_channel = create_channel.json()
    assert create_channel.status_code == 200 
    #Get details
    details_payload = {'token':payload_user['token'], 'channel_id':payload_channel['channel_id']}
    get_details = requests.get(url+'/channel/details',params=details_payload)
    assert get_details.status_code == 200
    info_request ={'token':payload_user['token'],'u_id':payload_user['u_id']} 
    profile_request = requests.get(url+'/user/profile',params=(info_request))
    assert profile_request.status_code == 200
    
    requests.delete(url+'/clear')
    #Should not be able to obtain details as data is now empty
    get_details = requests.get(url+'/channel/details',params=details_payload)
    assert get_details.status_code != 200
    
    profile_request = requests.get(url+'/user/profile',params=(info_request))
    assert profile_request.status_code != 200

def test_userpermission_change(url):
    register_user = {'email':'valid@gmail.com', 'password':'validP4ss', 'name_first':'Jake', 'name_last':'Peralta'}
    register = requests.post(url+'/auth/register', json=(register_user))
    payload_user = register.json()
    assert register.status_code == 200
    
    change_info = {'token':payload_user['token'], 'u_id':payload_user['u_id'], 'permission_id': 2}
    permission_change = requests.post(url+'admin/userpermission/change', json=(change_info))
    assert permission_change.status_code == 200

def test_search_empty(url):
    # Creates user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()

    search_info = {'token':user1['token'],'query_str':"search for this"}
    search_request = requests.get(url+'/search',params=search_info)
    assert search_request.status_code == 200

def test_search_exact_match(url):
    # Creates user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()

    message_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"exact match"}
    requests.post(url+'/message/send', json=(message_info))

    search_info = {'token':user1['token'],'query_str':"exact match"}
    search_request = requests.get(url+'/search',params=search_info)
    assert search_request.status_code == 200

def test_search_multiple_channels(url):
    # Creates user1
    user1_info = {'email':'user1@gmail.com', 'password':'P455w04d!', 'name_first':'Rick', 'name_last':'Sanchez'}
    user1_request = requests.post(url+'/auth/register', json=(user1_info))
    user1 = user1_request.json()
    # Creates a channel where user1 is the owner
    channel1_info = {'token':user1['token'],'name':"The Citadel",'is_public':False}
    channel1_request = requests.post(url+'/channels/create',json=(channel1_info))
    channel1 = channel1_request.json()
    # Creates another channel where user1 is the owner
    channel2_info = {'token':user1['token'],'name':"Earth C-137",'is_public':True}
    channel2_request = requests.post(url+'/channels/create',json=(channel2_info))
    channel2 = channel2_request.json()

    message1_info = {'token':user1['token'],'channel_id':channel1['channel_id'],'message':"message 1"}
    requests.post(url+'/message/send', json=(message1_info))
    message2_info = {'token':user1['token'],'channel_id':channel2['channel_id'],'message':"message 2"}
    requests.post(url+'/message/send', json=(message2_info))

    search_info = {'token':user1['token'],'query_str':"message"}
    search_request = requests.get(url+'/search',params=search_info)
    assert search_request.status_code == 200
