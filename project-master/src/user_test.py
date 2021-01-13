import pytest
from error import InputError, AccessError
from other import clear, users_all
from auth import auth_register, auth_logout, auth_login
from user import user_profile, user_profile_setemail, user_profile_sethandle, user_profile_setname, user_profile_upload
from helper import get_handle


def test_user_prof_pass():
    clear()
    user = auth_register("aest@gmail.com", "val21sss", "John", "Silver")
    result = user_profile(user['token'], user['u_id'])
    # Asserts the elements of the 'user' data
    assert len(result['user'].keys()) == 6
    assert 'user_id' and 'email' and 'name_first' and 'name_last' and 'handle_str' in result['user'].keys()
    # Asserts the user_prof result (dictionary with 'user' key)
    assert len(result) == 1 and 'user' in result.keys()


def test_user_prof_error():
    clear()
    user = auth_register("ascii@gmail.com", "val21sss", "Jason", "Sozmann")
    token = user['token']
    u_id = user['u_id']
    # invalid token AccessError
    inv_token = ["notrealtoken", 9384, 87234.83274, [user['token']], {"tokne": 34}]
    for tok in inv_token:
        with pytest.raises(AccessError):
            user_profile(tok, u_id)

    # invalid u_id InputError - invalid types included
    inv_uid = [-5, "0", [0], 0.57, {"u_id": 0}]
    for uid in inv_uid:
        with pytest.raises(InputError):
            user_profile(token, uid)

def test_user_prof_multiple():
    clear()
    user1 = auth_register("abcd@gmail.com", "val2dfsss", "John", "Silver")
    user2 = auth_register("awcd@gmail.com", "val2dsfss", "John", "Silver")
    user3 = auth_register("wdfv@gmail.com", "val2wevsss", "John", "Silver")

    res1 = user_profile(user1['token'], user2['u_id'])['user']
    res2 = user_profile(user1['token'], user3['u_id'])['user']
    assert res1['handle_str'] == get_handle(user2['token'])
    assert res2['handle_str'] == get_handle(user3['token'])

    res1 = user_profile(user2['token'], user1['u_id'])['user']
    res2 = user_profile(user2['token'], user3['u_id'])['user']
    assert res1['handle_str'] == get_handle(user1['token'])
    assert res2['handle_str'] == get_handle(user3['token'])

    res1 = user_profile(user3['token'], user1['u_id'])['user']
    res2 = user_profile(user3['token'], user2['u_id'])['user']
    assert res1['handle_str'] == get_handle(user1['token'])
    assert res2['handle_str'] == get_handle(user2['token'])

def test_user_setname_pass():
    clear()
    name_first = "John"
    name_last = "Silver"
    user = auth_register("alsotest@gmail.com", "validP4ss", name_first, name_last) 
    token = user["token"]
    
    # Asserts that users can set their previous name
    # if no errors raised, returns empty dictionary
    assert user_profile_setname(token, name_first, name_last) == {}

    # setting name to different person
    new_first = "Steve"
    new_last = "Aoki"
    # if no errors raised, returns empty dictionary
    assert user_profile_setname(token, new_first, new_last) == {}

    # Check that the user's name has been changed
    prof = user_profile(user['token'], user['u_id'])
    assert prof['user']['name_first'] == new_first
    assert prof['user']['name_last'] == new_last

def test_user_setname_multiple():
    # setting name multiple times
    clear()
    user = auth_register("alsotest@gmail.com", "validP4ss", "John", "Silver") 
    token = user["token"]
    res = user_profile_setname(token, "Stevena", "Aaoki")
    assert res == {}
    res2 = user_profile_setname(token, "Steve", "Aaoki")
    assert res2 == {}
    res3 = user_profile_setname(token, "Steven", "Aoki")
    assert res3 == {}
    res4 = user_profile_setname(token, "Steve", "Aoki")
    assert res4 == {}

    user2 = auth_register("askme@gmail.com", "validP4ss", "Steve", "Aoki") 
    # two people can have the same name
    assert user_profile_setname(user2['token'], "Steve", "Aoki") == {}

def test_user_setname_error():
    clear()
    user = auth_register("alsotest@gmail.com", "oasisontheshore", "John", "Silver") 
    token = user["token"]

    name = "thisisanamethatiswaybiggerthan50characterslongandexceedssetname"
    # name_first < 1 or > 50 chars InputError
    with pytest.raises(InputError):
        user_profile_setname(token, name, "Silver")
    with pytest.raises(InputError):
        user_profile_setname(token, "", "Silver")

    # name_last < 1 or > 50 chars InputError
    with pytest.raises(InputError):
        user_profile_setname(token, "John", name)        
    with pytest.raises(InputError):
        user_profile_setname(token, "John", "")        

    # invalid token
    with pytest.raises(AccessError):
        user_profile_setname("johnsilvertoken", "John", "Silver")

    # Invalid types
    invalid_types = [["John"], 10, 0.6723, {"name": "John"}]
    for inv_type in invalid_types:
        # Typecheck for name_last
        with pytest.raises(InputError):
            user_profile_setname(user['token'], "John", inv_type)
        # Typecheck for name_first
        with pytest.raises(InputError):
            user_profile_setname(user['token'], inv_type, "Silver")
        # Typecheck for token
        with pytest.raises(AccessError):
            user_profile_setname(inv_type, "John", "Silver")
    
    result = user_profile(user['token'], user['u_id'])['user']
    assert result['name_first'] == "John"
    assert result['name_last'] == "Silver"

def test_user_setname_token_expired():
    clear()
    user = auth_register("alsotest@gmail.com", "oasisontheshore", "John", "Silver") 
    token = user["token"]
    # token no longer valid
    auth_logout(token)
    with pytest.raises(AccessError):
        user_profile_setname(token, "John", "Silverman")
    
    # Ensure name remains unchanged
    user_login = auth_login("alsotest@gmail.com", "oasisontheshore")
    result = user_profile(user_login['token'], user_login['u_id'])['user']
    assert result['name_first'] == "John"
    assert result['name_last'] == "Silver"

def test_user_setemail_pass():
    clear()
    email = "viable@gmail.com"
    user  = auth_register(email, "oasisontheshore", "John", "Silver")

    new_mail = "viable2@gmail.com"
    # if no errors raised, returns empty dictionary
    assert user_profile_setemail(user["token"], new_mail) == {}

    # check if the data was changed
    assert user_profile(user['token'], user['u_id'])['user']['email'] == new_mail

def test_user_setemail_error():
    clear()
    email = "viable@gmail.com"
    user  = auth_register(email, "oasisontheshore", "John", "Silver")

    # invalid token
    with pytest.raises(AccessError):
        user_profile_setemail("token", email)

    # invalid email
    with pytest.raises(InputError):
        user_profile_setemail(user["token"], "email")

    # setemail is same email as user
    with pytest.raises(InputError):
        user_profile_setemail(user["token"], email)

    user2 = auth_register("ascii@gmail.com", "val21sss", "Jason", "Sozmann")

    # email is already used by another user
    with pytest.raises(InputError):
        user_profile_setemail(user2['token'], email)

    # Assert that the data wasn't changed
    assert user_profile(user2['token'], user2['u_id'])['user']['email'] == "ascii@gmail.com"

def test_user_sethandle_pass():
    clear()
    user = auth_register("alsotest@gmail.com", "oasisontheshore", "John", "Silver") 
    # if no errors raised, returns empty dictionary
    assert user_profile_sethandle(user["token"], "jsilver") == {}

    # Assert data was changed
    assert user_profile(user['token'], user['u_id'])['user']['handle_str'] == "jsilver"

def test_user_sethandle_error():
    clear()
    user = auth_register("alsotest@gmail.com", "oasisontheshore", "John", "Silver") 
    token = user["token"]
    
    initial_handle = user_profile(user['token'], user['u_id'])['user']['handle_str']

    # handle < 3 chars
    with pytest.raises(InputError):
        user_profile_sethandle(token, "js")

    # handle > 20 chars
    with pytest.raises(InputError):
        user_profile_sethandle(token, "johnnyboysilvermetalspoon")

    # Assert data wasn't changed
    assert user_profile(user['token'], user['u_id'])['user']['handle_str'] == initial_handle

    # handle already used
    user_profile_sethandle(token, "jsilver")
    user2 = auth_register("valid@email.com", "paradisemd", "Josh", "Silman") 
    initial_handle2 = user_profile(user2['token'], user2['u_id'])['user']['handle_str']
    with pytest.raises(InputError):
        user_profile_sethandle(user2["token"], "jsilver")

    # Invalid token
    inv_tokens = ["invalid_tok", [token], 12, 192.239, {'token': token}]
    for tok in inv_tokens:
        with pytest.raises(AccessError):
            user_profile_sethandle(tok, "jonosilvaa")

    # Invalid handle type
    inv_handle = [["thisisahandle"], 9823, 98.7631, {"handle_str": "This be a handle"}]
    for handles in inv_handle:
        with pytest.raises(InputError):
            user_profile_sethandle(user2['token'], handles)

    # Assert data wasn't changed
    assert user_profile(user2['token'], user2['u_id'])['user']['handle_str'] == initial_handle2
    assert user_profile(user['token'], user['u_id'])['user']['handle_str'] == "jsilver"

def test_user_sethandle_multiple():
    clear()
    user = auth_register("alsotest@gmail.com", "oasisontheshore", "John", "Silver")
    token = user["token"]    
    with pytest.raises(InputError):
       user_profile_sethandle(token, get_handle(token))
    res = user_profile_sethandle(token, "johnsilver")
    assert res == {}
    res = user_profile_sethandle(token, "johnsilveronflock")
    assert res == {}
    # set handle to possible create_handle but not used yet
    res = user_profile_sethandle(token, "jsilver1")
    assert res == {}
    auth_register("notmy@gmail.com", "oasisontheshore", "John", "Silver")
    # handle here should change to jsilver2
    user2 = auth_register("noky@gmail.com", "oasisontheshore", "John", "Silver")
    assert get_handle(user2['token']) != "jsilver1" 
    
       
def test_user_uploadphoto_error():
    clear()
    user = auth_register("alsotest@gmail.com", "oasisontheshore", "John", "Silver")
    token = user["token"]    
    url = 'https://variety.com/wp-content/uploads/2020/07/kanye-west.jpg'
    #check for invalid token
    invalid_tokens = ['not a token',[token],4422,{'token':token},'Appen', 23.5]
    for tokens in invalid_tokens:
        with pytest.raises(AccessError):
            user_profile_upload(tokens,url,0,0,100,100)

    #Check for when x,y start and end values are the same   
    with pytest.raises(InputError):
        user_profile_upload(token,url,20,20,20,20)
    with pytest.raises(InputError):
        user_profile_upload(token,url,20,50,20,50)
 
    #Check for invalid url
    with pytest.raises(InputError):
        user_profile_upload(token,url+'invalid',0,1,2,3)
        
    #Check for invalid image file i.e not jpg
    with pytest.raises(InputError):
        user_profile_upload(token,'https://fileinfo.com/extension/png',0,1,2,3) 
    
    
    
    
    
    
    
