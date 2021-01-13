'''
    This file contains a bunch of helper functions that are used in
    different functions of the assignment.
'''
import jwt
import re 
import hashlib
from data import DATA
import requests
import urllib.request
from PIL import Image
from flask import request
from error import InputError


SECRET = "temp_secret"
FOLDER_NAME = 'src/user_photos/'

def user_in_channel(u_id, channel_id):
    '''
    Checks if u_id in 'all_members' of channel
    returns True if is member
            False otherwise
    '''
    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            for user in channel['all_members']:
                if user['u_id'] == u_id:
                    return True
    return False

def is_valid_token(token):
    '''
    Checks if token in 'active' data
    returns True if valid token
            False otherwise
    '''
    if isinstance(token, str) and bool(token):
        for user in DATA['active']:
            if user == token:
                return True
    return False

def is_valid_channel_id(channel_id):
    '''
    Checks if channel in 'channels' data
    returns True if valid channel
            False otherwise
    '''
    if isinstance(channel_id, int):
        for channel in DATA['channels']:
            if channel['channel_id'] == channel_id:
                return True
    return False

def is_valid_password(password):
    '''
    Checks if the password is of type str, and if it is
    > 6 chars
    '''
    if isinstance(password, str) and len(password) >= 6:
        return True
    return False

def is_valid_uid(u_id):
    '''
    Checks if u_id in 'users' data
    returns True if valid u_id
            False otherwise
    '''
    if isinstance(u_id, int) and u_id > -1:
        for user in DATA['users']:
            if user['u_id'] == u_id:
                return True
    return False

def is_valid_name(name):
    '''
    Checks if the name is of type str, and if it is between
    1 <-> 50 chars
    '''
    if isinstance(name, str) and len(name) >= 1 and len(name) <= 50:
        return True
    return False

def is_valid_handle(handle):
    '''
    Checks if the handle is of type str and if it
    is between 3 and 20 characters
    '''
    if isinstance(handle, str) and len(handle) >= 3 and len(handle) <= 20:
        return True
    return False

def is_valid_query(query_str):
    '''
    Checks if query is empty, and if it
    is a string
    '''
    if isinstance(query_str, str) and len(query_str) > 0:
            return True
    return False

def is_valid_permission_id(permission_id):
    '''
    Checks that permission id is in the set list
    of valid id's
    '''
    valid_permissions = [1, 2]

    # This means that permission_id has to be an int / the same type
    # as the valid permission id's
    if permission_id in valid_permissions:
        return True
    return False

def is_owner_permission(u_id):
    '''
    Checks if the given user has
    owner priviledges
    '''
    for user in DATA['users']:
        if user['u_id'] == u_id and user['permission_id'] == 1:
                return True
    return False

def is_allowed_message_id(u_id, message_id):
    '''
    Checks if the message exists, then if the user is allowed
    to view it. - for use in message_react
    '''
    message_info = get_message_info(message_id)
    if message_info:
        channel_id = message_info['channel_id']
        if user_in_channel(u_id, channel_id):
            return True
    return False

def is_valid_react_id(react_id):
    react_ids = [
        1, # Thumbs up
    ]
    if react_id in react_ids:
        return True
    else:
        return False

def get_uid(token):
    '''
    Gets u_id of given token
    returns 'u_id' if in data
            None if not found
    '''
    for user in DATA['users']:
        if user['token'] == token:
            return user['u_id']
    return None

def get_user(u_id):
    '''
    Gets user data of given u_id
    returns dict of user if in data
            None if not found
    '''
    for user in DATA['users']:
        if user['u_id'] == u_id:
            return user
    return None

def get_messages(channel_id):
    '''
    Gets messages in channel
    returns dict of messages if in data
            None if not found
    '''
    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            return channel['messages']
    return None

def get_channel(channel_id):
    '''
    Gets the channel information for the
    given channel_id
    '''
    if isinstance(channel_id, int):
        for channel in DATA['channels']:
            if channel['channel_id'] == channel_id:
                return channel
    return None

def is_owner(u_id, channel_id):
    '''
    Checks if u_id is owner if channel
    returns True if u_id is owner
            False otherwise
    '''
    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            for owner in channel['owner_members']:
                if owner['u_id'] == u_id:
                    return True
            return False
    return False

def public_chan(channel_id):
    '''
    Checks if channel is public
    returns True if public channel
            False otherwise
    '''
    for channels in DATA['channels']:
        if channels['channel_id'] == channel_id and channels['is_public'] is True:
                return True
    return False

def get_message_info(message_id):
    '''
    Gets the message information based off the message id
    returns empty dictionary if it doesn't exist
    '''
    message_data = {}
    for channel in DATA['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id: 
                message_data = message
    return message_data

def token_generate(email):
    '''
    This function generates a token based on the secret defined in auth.py
    '''
    enc_jwt = jwt.encode({'token': email}, SECRET, algorithm='HS256').decode('utf-8')
    return enc_jwt

# This might be a little bit simpler in regards to email checking
def is_valid_email(email):
    # referenced from https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    re_custom = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    try:
        if re.search(regex, email) or re.search(re_custom, email): 
            return True
    except TypeError:
        return False
    else:
        return False

def is_email_used(email):
    for user in (DATA["users"]):
        if user["email"] == email:
            return True
    # This is only run if the email is not found
    return False

def pass_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_password_correct(email, password):
    if isinstance(password, str) and bool(password):
        for user in DATA["users"]:
            if user["email"] == email and user["password"] == pass_hash(password):
                return True
    # If the email isn't found or the password is empty / not a string
    return False

def get_user_index(email):
    for user in DATA["users"]:
        if user["email"] == email:
            return DATA["users"].index(user)
    return None

# creates a unique handle for a name
def create_handle(name_first, name_last, u_id):
    # tried using global x but didn't reset x with clear()
    x = u_id
    handle = name_first[0].lower() + name_last[:19 - len(str(x))].lower() + str(x)
    # if handle already created
    while is_handle_used(handle):
        # change the last digit
        x += 1
        handle = name_first[0].lower() + name_last[:19 - len(str(x))].lower() + str(x)
    return handle

def is_handle_used(handle):
    for user in DATA["users"]:
        if user["handle_str"] == handle:
            return True
    return False

def get_handle(token):
    for user in DATA['users']:
        if user['token'] == token:
            return user['handle_str']
    return None

def make_int(value):
    if isinstance(value, (int, str)):
        try:
            return int(value)
        except:
            return value
    return value

def get_standup(channel_id):
    for standup in DATA['standups']:
        if standup['channel_id'] == channel_id:
            return standup
    return None
    
def check_valid_url(url):
    '''
    Checks if given url is valid.
    '''
    #if url.startswith('https://'):
    if requests.get(url).status_code == 200:
        return True
    return False

def is_url_jpg(url):
    '''
    Checks if url is of jpg type
    Implementation inspired by https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python/48909668  
    '''
    formats = ( "image/jpeg", "image/jpg")
    r= requests.head(url)
    if r.headers["Content-Type"] in formats:
        return True
    return False

def is_equal_xy(x_start,y_start,x_end,y_end):
    '''Checks if end co-ordinates are greater than or equal to start coordinates'''
    if x_end <= x_start or y_end <= y_start:
        return False
    return True
def is_dimensions_correct(url,x_start,y_start,x_end, y_end):
    '''
    For the given url checks if image coordinates are within the bounds of the image dimensions.
    '''
    page = urllib.request.urlopen(url)
    #print(page.url)
    image = Image.open(page)
    width,height = image.size
    #print(width,height)
    if x_start >= width or x_end > width:
        return False
    if y_start >= height or y_end > height:
        return False
    return True

def download_jpg(url,file_name):
    '''
    In user.py implementation use user's name as file name
    Implementation inspired by https://youtu.be/2Rf01wfbQLk - 'Python 3 Tutorial for Beginners #29 - Downloading Images'
    '''
    path = FOLDER_NAME+file_name
    urllib.request.urlretrieve(url,path)
    return path

def crop_image(path,x_start,y_start,x_end,y_end):
    '''
    Given a path, function crops image to given dimensions.
    '''
    imageObject = Image.open(path)
    cropped = imageObject.crop((x_start,y_start,x_end,y_end))
    cropped.save(path) 
    #image = Image.open(path) this is for checking the image is cropped
   # width,height = image.size
   
    #print(width,height) 

def insert_image_url(token):
    '''
    Inserts profile_img_url for a user
    '''
    user = get_user(get_uid(token))
    user['profile_img_url'] = generate_img_url(token)

    
def generate_img_url(token):
    '''
    Generates profile_img_url
    '''

    return request.url_root+'user_photos/'+get_filename(token)

def get_filename(token):
    '''
    Generates filename for downloaded images where 'dp' stands for display picture
    '''
    return get_handle(token)+'_dp.jpg'
   


def get_last_message(channel_id):
    for channel in DATA['channels']:
        if channel['channel_id'] == channel_id:
            last_message = channel['messages'][0]
            for message in channel['messages']:
                '''# Sort by time_created
                if message['time_created'] > last_message['time_created']:
                    last_message = message
                elif message['time_created'] < last_message['time_created']:
                    continue
                # If time_created is the same, sort by message_id'''
                if message['message_id'] > last_message['message_id']:
                    last_message = message
            return last_message

    # Only run if channel not found
    raise InputError(description = "Channel ID not valid")

