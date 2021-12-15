import data
import helper as hp
from error import InputError, AccessError

def user_profile(token, u_id):
    # for valid token user check if u_id user is real then returns u_id user
    # (works like viewing the 'u_id' profile as the 'token' user)
    '''
        AccessError if:
        - invalid token
        InputError if:
        - invalid u_id
    '''
    if not hp.is_valid_token(token):
        raise AccessError('Token is invalid')
    elif not hp.is_valid_uid(u_id):
        raise InputError('User id is invalid')

    user = hp.get_user(u_id)
    return {
        'user': {
        	'u_id': user['u_id'],
        	'email': user['email'],
        	'name_first': user['name_first'],
        	'name_last': user['name_last'],
        	'handle_str': user['handle_str'],
            'profile_img_url' : user['profile_img_url']
        },
    }

def user_profile_setname(token, name_first, name_last):
    # this is used to change name on website
    '''
        AccessError if:
        - invalid token
        InputError if:
        - first name <1 or >50 chars long
        - last name <1 or >50 chars long

    '''
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_name(name_first):
        raise InputError(description='First name is invalid')
    elif not hp.is_valid_name(name_last):
        raise InputError(description='Last name is invalid')
    
    user = hp.get_user(hp.get_uid(token))
    user['name_first'] = name_first
    user['name_last'] = name_last
    return {
    }

def user_profile_setemail(token, email):
    # this is used to change email on website
    '''
        AccessError if:
        - invalid token
        InputError if:
        - invalid email
        - email already used by another user
        - email is same email as token
    '''
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_email(email):
        raise InputError(description='Email is invalid')
    elif hp.is_email_used(email):
        raise InputError(description='Email is already used')

    user = hp.get_user(hp.get_uid(token))
    user['email'] = email
    return {
    }

def user_profile_sethandle(token, handle_str): 
    '''
        AccessError if:
        - invalid token
        InputError if:
        - handle_str <3 or >20 chars long
        - handle already used by another user
        - handle is same handle as token
    '''
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    elif not hp.is_valid_handle(handle_str):
        raise InputError(description='Handle string is invalid')
    elif hp.is_handle_used(handle_str):
        raise InputError(description='Handle already used')
    
    user = hp.get_user(hp.get_uid(token))
    user['handle_str'] = handle_str
    return {
    }
    
    
def user_profile_upload(token,image_url,x_start,y_start,x_end,y_end):
    '''
    Input Error if:
        -img_url returns a HTTP status other than 200
        -x_start,y_start,x_end and y_end are not within the dimensions of image at URL
        - image uploaded is not a JPG
        - input error if x and y , start and end values are the same
    Access Error if:
        -invalid token
    '''
    if not hp.is_valid_token(token):
        raise AccessError(description='Token is invalid')
    if not hp.check_valid_url(image_url):
        raise InputError('Invalid URL')  
    if not hp.is_url_jpg(image_url):
        raise InputError('URL is not a JPG')
    if not hp.is_equal_xy(x_start,y_start,x_end,y_end):
        raise InputError('End coordinates need to be >= to start coordinates')     
    if not hp.is_dimensions_correct(image_url,x_start,y_start,x_end,y_end):
        raise InputError('Coordinates are not within the dimensions of image at URL')
    # Check the helper.py file for specific implementation of the following functions
    filename = hp.get_filename(token)
    path = hp.download_jpg(image_url,filename)
    hp.crop_image(path,x_start,y_start,x_end,y_end)
    hp.insert_image_url(token)
    return {
    }
        
