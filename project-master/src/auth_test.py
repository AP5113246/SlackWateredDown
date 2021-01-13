import pytest

from data import DATA
from auth import auth_login, auth_register, auth_logout, auth_password_reset_request, auth_passwordreset_reset
from error import InputError
from other import clear
import helper as hp

#### auth_register ####
# First note:
# A dictionary returned from auth_register if valid register.
# contains 'u_id' and 'token'
# If invalid register returns InputError
def test_reg_valid():
    clear()
    res = auth_register("valid@gmail.com", "validP4ss", "Jake", "Peralta")
    assert 'u_id' and 'token' in res.keys() and len(res) == 2
    assert res["token"] == hp.token_generate("valid@gmail.com")

def test_reg_email_invalid():
    with pytest.raises(InputError):
        auth_register("failedemail.com", "password123", "John", "Johnson")

def test_reg_email_existing():
    clear()
    auth_register("newemail@gmail.com", "passW0rD", "Abed", "Nadir")
    with pytest.raises(InputError):
        auth_register("newemail@gmail.com", "passW0rD", "Troy", "Barnes")

def test_reg_var_too_short():
    # password < 6 chars
    with pytest.raises(InputError):
        auth_register("testemail@hotmail.com", "test!", "Sherlock", "Holmes")
    # name_first < 1 char (empty name_first)
    with pytest.raises(InputError):
        auth_register("validemail@gmail.com.au", "validPass", "", "Jones")
    # name_last < 1 char (empty name_last)
    with pytest.raises(InputError):
        auth_register("validemail@gmail.org", "V4LidpAsS!", "Mark", "")

def test_reg_var_too_long():
    name = "ThisIsAVeryLongNameForSomeoneThatIsMoreThan50Characters"
    # name_first > 50 chars
    with pytest.raises(InputError):
        auth_register("validemail@gmail.org.au", "valiDP4ss", name, "Martin")
    # name_last > 50 chars
    with pytest.raises(InputError):
        auth_register("validemail@hotmail.org", "Val!dP4Ss!", "John", name)

def test_reg_invalid_type():
    clear()
    email_inputs = [76, 10.03, ["list@gmail.com"], {"thisisvalid@gmail.com": 'email'}]
    passw_inputs = [19, 12.1332, ["PasswordValid"], {"ValidPa45": 'Password'}]
    name_inputs = [11, 9.11, ["Eleven"], {'name_first': 'eleven'}]
    
    with pytest.raises(InputError):
        # Testing email
        for in_type in email_inputs:
            auth_register(in_type, "ValidPass", "Terry", "Jeffords")
            clear()
        # Testing password
        for in_type in passw_inputs:
            auth_register("validemail@gmail.com", in_type, "Troy", "Barnes")
            clear()
        # Testing name_first
        for in_type in name_inputs:
            auth_register("valid@yahoo.com", "validpass", in_type, "Jones")
            clear()
        # Testing name_last
        for in_type in name_inputs:
            auth_register("correct@hotmail.com", "correctpass123", "Martin", in_type)
            clear()

def test_owner_first_user():
    clear()
    user = auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    u_id = user['u_id'] 
    assert hp.get_user(u_id)["permission_id"] == 1
    user1 = auth_register('potato@gmail.com', 'potato', 'Sora', 'Phillips')
    u_id = user1['u_id'] 
    assert hp.get_user(u_id)["permission_id"] == 2
    
#### auth_login ####
# First note:
# clear() is used for testing to ensure 'u_id' starts at 0
def test_login_success():
    clear()
    auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    res = auth_login('validemail@gmail.com', '123abc!@#')
    assert res["token"] == hp.token_generate("validemail@gmail.com")
    assert 'u_id' and 'token' in res.keys() and len(res) == 2

def test_login_email_invalid():
    with pytest.raises(InputError):
        auth_login("notrealmailau", "apples")

def test_login_email_not_registered():
    clear()
    with pytest.raises(InputError):
        auth_login("notmyemail@mail.com", "biscuits")

def test_login_email_incorrect():
    clear()
    auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError): 
       auth_login('didntusethis@gmail.com', '123abcd!@#')

def test_login_var_empty():
    clear()
    auth_register('test@gmail.com', 'bananas', 'Hayden', 'Everest')    
    # password empty
    with pytest.raises(InputError):
        auth_login("test@gmail.com", "")
    # email empty (same as email invalid)
    with pytest.raises(InputError):
        auth_login("", "bananas")

def test_login_var_close():
    clear()
    auth_register('test@gmail.com', 'bananas', 'Hayden', 'Everest')    
    # password incorrect
    with pytest.raises(InputError):
        auth_login("test@gmail.com", "bananas ")
    # email incorrect
    with pytest.raises(InputError):
        auth_login("test@gmail.com.", "bananas")

def test_login_multiple_times():
    clear()
    auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    auth_login('validemail@gmail.com', '123abc!@#')
    auth_login('validemail@gmail.com', '123abc!@#')
    auth_login('validemail@gmail.com', '123abc!@#')
    res = auth_login('validemail@gmail.com', '123abc!@#')
    assert res["token"] == hp.token_generate("validemail@gmail.com")
    assert 'u_id' and 'token' in res.keys() and len(res) == 2    

def test_login_three_users():
    clear()
    auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    auth_register('thatsmy@gmail.com', 'potato', 'Hayden', 'Everest')
    auth_register('ohwaitemail@gmail.com', 'aampqw', 'Hayden', 'Everest')
    res = auth_login('validemail@gmail.com', '123abc!@#')
    assert res["token"] == hp.token_generate("validemail@gmail.com")
    assert 'u_id' and 'token' in res.keys() and len(res) == 2
    res = auth_login('ohwaitemail@gmail.com', 'aampqw')
    assert res["token"] == hp.token_generate('ohwaitemail@gmail.com')
    assert 'u_id' and 'token' in res.keys() and len(res) == 2
    res = auth_login('thatsmy@gmail.com', 'potato')
    assert res["token"] == hp.token_generate('thatsmy@gmail.com')
    assert 'u_id' and 'token' in res.keys() and len(res) == 2

    
#### auth_logout ####
# NOTE: when a user is registered, they are logged in.
def test_logout_valid_active_user():
    clear()
    user = auth_register("second@usermail.com", "password1", "Amy", "Santiago")
    res = auth_logout(user['token']) 
    assert res["is_success"] == True
    assert len(res) == 1

def test_logout_invalid_token():
    clear()
    res =  auth_logout("notloggedin@gmail.com")
    assert res["is_success"] == False
    assert len(res) == 1

    res = auth_logout("invalidtoken")
    assert res["is_success"] == False
    assert len(res) == 1

def test_logout_empty_token():
    clear()
    res = auth_logout("")
    assert res["is_success"] == False
    assert len(res) == 1

def test_logout_multiple():
    clear()
    user1 = auth_register('potato@gmail.com', 'potato', 'Sora', 'Phillips')
    auth_logout(user1['token'])
    auth_login('potato@gmail.com', 'potato')
    auth_logout(user1['token'])
    res = auth_logout(user1['token'])
    assert res["is_success"] == False
    res = auth_logout(user1['token'])
    assert res["is_success"] == False
    auth_login('potato@gmail.com', 'potato')
    res = auth_logout(user1['token'])
    assert res['is_success'] == True

def test_logout_twice():
    clear()
    user = auth_register('potato@gmail.com', 'potato', 'Sora', 'Phillips')
    assert 'u_id' and 'token' in user.keys() and len(user) == 2
    assert user['token'] == hp.token_generate("potato@gmail.com")

    res = auth_login('potato@gmail.com', 'potato')
    assert res['token'] == hp.token_generate("potato@gmail.com")
    assert 'u_id' and 'token' in res.keys() and len(res) == 2

    res = auth_logout(user['token'])
    assert res['is_success']  == True
    assert len(res) == 1

    # 2nd logout, token is not active
    res = auth_logout(user['token'])
    assert res["is_success"] == False
    assert len(res) == 1

#### handle_str tests ####
def test_handle_str_pass():
    clear()
    # Assert that the user creation is valid
    name_first = "Chadwick"
    name_last = "Boseman"
    email = "cboseman@gmail.com"
    password = "PantherB!4ck"
    user = auth_register(email, password, name_first, name_last)
    assert len(user) == 2    

    handle_str = hp.create_handle(name_first, name_last, user['u_id'])
    # Ensure that the handle is at most 20 characters
    assert len(handle_str) <= 20
    # Ensure that the handle is unique
    # Since auth_register created a unique handle and added it into data.py
    #   even though the handle_str that we created above uses the same credentials,
    #   it shouldn't appear in data.py if each handle is unique

    assert not hp.is_handle_used(handle_str)


#### auth_reset tests ####
def test_pass_reset_req_pass():
    clear()
    user1 = auth_register('johnsmith@hotmail.com', 'password', 'Pickman', 'Steve')
    res = auth_password_reset_request('johnsmith@hotmail.com')
    assert res == {}
    assert len(hp.get_user(user1['u_id'])['reset_codes']) == 1


def test_pass_reset_req_error():
    clear()
    auth_register('johnsmith@hotmail.com', 'password', 'Pickman', 'Steve')
    with pytest.raises(InputError):
        # Invalid email
        auth_password_reset_request("realemail.com")
        # Email not in database
        auth_password_reset_request('chrishemsworth@gmail.com')
        # Email incorrect because of typo
        auth_password_reset_request('johnsmith@hotmail.com ')
        auth_password_reset_request(' johnsmith@hotmail.com')
        auth_password_reset_request('johsmith@hotmail.com')

def test_pass_reset_req_multiple():
    clear()
    user1 = auth_register('johnsmith@hotmail.com', 'password', 'Pickman', 'Steve')
    res = auth_password_reset_request('johnsmith@hotmail.com')
    assert res == {}
    res = auth_password_reset_request('johnsmith@hotmail.com')
    assert res == {}
    res = auth_password_reset_request('johnsmith@hotmail.com')
    assert res == {}
    res = auth_password_reset_request('johnsmith@hotmail.com')
    assert res == {}
    res = auth_password_reset_request('johnsmith@hotmail.com')
    assert res == {}
    assert len(hp.get_user(user1['u_id'])['reset_codes']) == 5

def test_pass_reset_reset_pass():
    clear()
    user1 = auth_register('johnsmith@hotmail.com', 'password', 'Pickman', 'Steve')
    auth_password_reset_request('johnsmith@hotmail.com')
    # we can only consider the reset code if we assert there is only one code
    codes = hp.get_user(user1['u_id'])['reset_codes']
    assert len(codes) == 1
    res = auth_passwordreset_reset(codes[0], 'new_pass')
    # returns nothing if password successfully reset
    assert res == {}


def test_pass_reset_reset_error():
    clear()
    user1 = auth_register('johnsmith@hotmail.com', 'password', 'Pickman', 'Steve')
    auth_password_reset_request('johnsmith@hotmail.com')
    with pytest.raises(InputError):
        # reset code is invalid
        auth_passwordreset_reset("thisismyresetcode", "new_pass")

    # assert a code exists in database
    codes = hp.get_user(user1['u_id'])['reset_codes']
    assert len(codes) == 1
    with pytest.raises(InputError):    
        # invalid pass
        auth_passwordreset_reset(codes[0], 'pass')   

def test_boost_coverage():
    clear()
    auth_register('johnsmith@hotmail.com', 'password', 'Pickman', 'Steve')

    # testing invalid first name
    with pytest.raises(InputError):
        auth_register('johnsm@hotmail.com', 'password', '', 'Steve')

    # testing valid email but does not belong to a user
    with pytest.raises(InputError):
        auth_password_reset_request("johnsmi@hotmail.com")

    # testing password reset request with 2 users in database
    # corrects the error of always true if statement
    auth_register('janesmith@hotmail.com', 'password', 'Pikmin', 'Steven')
    auth_password_reset_request('janesmith@hotmail.com')