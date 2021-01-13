from error import InputError
from data import DATA
import helper as hp
import random, string
def auth_login(email, password):
    '''
        InputError if:
        1: Invalid Email
        2: Email doesn't exist 
        3: Password incorrect
    '''
    if not hp.is_valid_email(email):
        raise InputError('Email is invalid')
    elif not hp.is_email_used(email):
        raise InputError(f"User with email '{email}' doesn't exist")
    elif not hp.is_password_correct(email, password):
        raise InputError('Password is incorrect')

    u_token = hp.token_generate(email)
    user = hp.get_user(hp.get_uid(u_token))
    
    # Logged in means 'active' user.
    # Removes duplicate logins
    if user['token'] not in DATA['active']:
        DATA['active'].append(user['token'])
    
    return {
        'u_id': user['u_id'],
        'token': hp.token_generate(user['email']),
    }

def auth_logout(token):
    # Check if the token is empty
    if hp.is_valid_token(token):
        # if token in DATA["active"]: 
        # commented since it is already a valid token in data users
            DATA["active"].remove(token)
            return {"is_success" : True}
    return {"is_success" : False}
    
    

# auth_register is a function that adds a new user to DATA
# if valid, returns a dic with 'u_id' and 'token'
# else InputError is raised
def auth_register(email, password, name_first, name_last):
    '''
        InputError is raised when:
        - invalid email
        - email already registered
        - password < 6 characters
        - name_first is not between 1 <= ..<= 50 characters
        - name_last is not between 1 <= ..<= 50 characters
    '''
    if hp.is_email_used(email):
        raise InputError(description='Email already registered')
    elif not hp.is_valid_email(email):
        raise InputError(description='Email is invalid')
    elif not hp.is_valid_password(password):
        raise InputError(description='Password is too short')
    elif not hp.is_valid_name(name_first):
        raise InputError(description='First name is invalid')
    elif not hp.is_valid_name(name_last):
        raise InputError(description='Last name is invalid')
    else:
        # Easy access to change token when necessary
        token = hp.token_generate(email)
        # u_id represents the persons special id, cannot overlap
        u_id = len(DATA['users'])
        # handle str is created when registering
        handle_str = hp.create_handle(name_first, name_last, u_id)
        
        # First registered user gets owner permissions
        permission_id = 2
        if len(DATA['users']) == 0:
            permission_id = 1

        new_user = {
            "u_id" : u_id,
            "email" : email,
            "password" : hp.pass_hash(password),
            "name_first": name_first,
            "name_last" : name_last,
            "token" : token,
            "handle_str": handle_str,
            "channels" : [],
            "permission_id" : permission_id,
            "reset_codes" : [],
            "profile_img_url" : '' #hp.generate_img_url('default')
        }

    # A registered user is automatically logged in
    DATA["active"].append(new_user["token"])
    # User is added to database
    DATA["users"].append(new_user)

    return {
        "u_id" : new_user['u_id'],
        'token': new_user['token'],
    }

def auth_password_reset_request(email):
    # NOTE: this function can be requested multiple times
    if not hp.is_valid_email(email):
        raise InputError(description='Email entered is not a valid email.')
    elif not hp.is_email_used(email):
        raise InputError(description='Email entered does not belong to a user.')

    # passes if email is being used and valid email

    # NOTE: code generated does not require any encryption since random string
    code = generate_pass_reset_code(42)
    for user in DATA['users']:
        if user['email'] == email:
            # since auth_reset can be used multiple times,
            # add a new reset code to a list not singular code
            user['reset_codes'].append(code)
    return {}

# https://stackoverflow.com/questions/37675280/how-to-generate-a-random-string
def generate_pass_reset_code(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def auth_passwordreset_reset(reset_code, new_password):
    for user in DATA['users']:
        for code in user['reset_codes']:
            if code == reset_code:
                if not hp.is_valid_password(new_password):
                    raise InputError(description='New password entered is an invalid password')
                # reset code has been used, remove it so they cant change it again with same code
                user['reset_codes'].remove(reset_code)
                # passwords stored in database have to be encrypted again
                user['password'] = hp.pass_hash(new_password)
                return {}
    
    # if didn't return, then code was not valid
    raise InputError(description='Reset code is not a valid reset code.')

