'''File contains all the server routes for Flockr functions'''
import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from auth import auth_register, auth_login, auth_logout, auth_password_reset_request, auth_passwordreset_reset
from channels import channels_create, channels_list, channels_listall
from message import message_send, message_remove, message_edit, message_react, message_unreact, message_sendlater, message_pin, message_unpin
from channel import channel_details, channel_invite, channel_messages, channel_join,channel_leave,channel_addowner,channel_removeowner
from other import users_all,clear, admin_userpermission_change, search
from user import user_profile, user_profile_setemail, user_profile_sethandle, user_profile_setname, user_profile_upload
from standup import standup_active, standup_start, standup_send
from error import InputError
from helper import make_int,insert_image_url



def defaultHandler(err):
    '''Given code for handling errors'''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__,static_url_path='/user_photos/',static_folder='user_photos')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)
@APP.route("/echo", methods=['GET'])
def echo():
    '''Example that echo's input'''
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })
    
@APP.route("/auth/login", methods=['POST'])
def server_auth_login():
    '''Logs in user'''
    data = request.get_json()
    return dumps(auth_login(data['email'], data['password']))

@APP.route("/auth/logout", methods=['POST'])
def server_auth_logout():
    '''Logs out user'''
    data = request.get_json()
    return dumps(auth_logout(data['token']))

@APP.route("/auth/register", methods=['POST'])
def server_auth_register():
    '''Regisers user'''
    data = request.get_json()
    email = data['email']
    password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']
    response = auth_register(email, password, name_first, name_last)
    return dumps({'u_id':response['u_id'],'token': response['token']})
    
@APP.route("/auth/passwordreset/request", methods=['POST'])
def server_passwordreset_request():
    data = request.get_json()
    return dumps(auth_password_reset_request(data['email']))
    
@APP.route("/auth/passwordreset/reset",methods=['POST'])
def server_password_reset():
    data = request.get_json()
    reset_code = data['reset_code']
    new_password = data['new_password']
    return dumps(auth_passwordreset_reset(reset_code, new_password))

@APP.route("/channels/create", methods=['POST'])
def server_channels_create():
    '''Create a channel'''
    data = request.get_json()
    user_token = data['token']
    channel_name = data['name']
    is_public = data['is_public']
    new_channel = channels_create(user_token, channel_name, is_public)
    return dumps({'channel_id':new_channel['channel_id']})

@APP.route("/channels/list",methods=['GET'])
def server_channels_list():
    '''Lists out channels the authorised user is part of'''
    token = request.args.get('token')
    users_channels = channels_list(token)
    return dumps({'channels':users_channels['channels']})


@APP.route("/channels/listall",methods=['GET'])
def server_channels_listall():
    '''Lists out channels the authorised user is part of'''
    token = request.args.get('token')
    users_channels = channels_listall(token)
    return dumps({'channels':users_channels['channels']})

@APP.route("/message/send", methods=['POST'])
def server_message_send():
    '''Sends a message to a channel'''
    attempt_send = request.get_json()
    token = attempt_send['token']
    channel_id = make_int(attempt_send['channel_id'])
    message = attempt_send['message']
    return dumps(message_send(token,channel_id,message))

@APP.route("/message/remove", methods=['DELETE'])
def server_message_remove():
    '''Deletes a message from a channel'''
    attempt_remove = request.get_json()
    token = attempt_remove['token']
    message_id = make_int(attempt_remove['message_id'])
    return dumps(message_remove(token,message_id))

@APP.route("/message/edit", methods=['PUT'])
def server_message_edit():
    '''Edits a message in a channel'''
    attempt_edit = request.get_json()
    token = attempt_edit['token']
    message_id = make_int(attempt_edit['message_id'])
    message = attempt_edit['message']
    return dumps(message_edit(token,message_id,message))
    
@APP.route("/message/sendlater", methods=["POST"])
def server_message_sendlater():
    '''Sends a message at a later time'''
    attempt_send = request.get_json()
    token = attempt_send['token']
    channel_id = make_int(attempt_send['channel_id'])
    message = attempt_send['message']
    time_sent = int(attempt_send['time_sent'])
    return dumps(message_sendlater(token, channel_id, message, time_sent))

@APP.route("/message/react", methods=["POST"])
def server_message_react():
    '''Reacts to a message in a channel'''
    attempt_react = request.get_json()
    token = attempt_react['token']
    message_id = make_int(attempt_react['message_id'])
    react_id = make_int(attempt_react['react_id'])
    return dumps(message_react(token, message_id, react_id))

@APP.route("/message/unreact", methods=["POST"])
def server_message_unreact():
    '''Unreacts to a message in a channel'''
    attempt_unreact = request.get_json()
    token = attempt_unreact['token']
    message_id = make_int(attempt_unreact['message_id'])
    react_id = make_int(attempt_unreact['react_id'])
    return dumps(message_unreact(token, message_id, react_id))

@APP.route("/message/pin", methods=["POST"])
def server_message_pin():
    '''Pins a message in a channel'''
    attempt_pin = request.get_json()
    token = attempt_pin['token']
    message_id = make_int(attempt_pin['message_id'])
    return dumps(message_pin(token, message_id))

@APP.route("/message/unpin", methods=["POST"])
def server_message_unpin():
    '''Unpins a message in a channel'''
    attempt_unpin = request.get_json()
    token = attempt_unpin['token']
    message_id = make_int(attempt_unpin['message_id'])
    return dumps(message_unpin(token, message_id))

@APP.route("/channel/details", methods=['GET'])
def server_channel_details():
    token = request.args.get('token')
    channel_id = make_int(request.args.get('channel_id'))
    return dumps(channel_details(token,channel_id))

@APP.route("/channel/invite", methods=['POST'])
def server_channel_invite():
    invite_info = request.get_json()
    token = invite_info['token']
    channel_id = make_int(invite_info['channel_id'])
    u_id = make_int(invite_info['u_id'])
    channel_invite(token,channel_id,u_id)
    return dumps({})

@APP.route("/channel/messages",methods=['GET'])
def server_channel_messages():
    token = request.args.get('token')
    channel_id = make_int(request.args.get('channel_id'))
    start_indicator = int(request.args.get('start'))
    return dumps(channel_messages(token,channel_id,start_indicator))

@APP.route("/channel/join", methods=['POST'])
def server_channel_join():
    join_info = request.get_json()
    token = join_info['token']
    channel_id = make_int(join_info['channel_id'])
    channel_join(token,channel_id)
    return dumps({})

@APP.route("/channel/leave", methods=['POST'])
def server_channel_leave():
    leave_info = request.get_json()
    token = leave_info['token']
    channel_id = make_int(leave_info['channel_id'])
    channel_leave(token,channel_id)
    return dumps({})
    
@APP.route("/channel/addowner", methods=['POST'])
def server_channel_addowner():
    new_owner_info = request.get_json()
    token = new_owner_info['token']
    channel_id = make_int(new_owner_info['channel_id'])
    u_id = make_int(new_owner_info['u_id'])
    channel_addowner(token,channel_id,u_id)
    return dumps({})
    
@APP.route("/channel/removeowner", methods=['POST'])
def server_channel_removeowner():
    remove_owner_info = request.get_json()
    token = remove_owner_info['token']
    channel_id = make_int(remove_owner_info['channel_id'])
    u_id = make_int(remove_owner_info['u_id'])
    channel_removeowner(token,channel_id,u_id)
    return dumps({})
'''
Routes for User/s functions
'''
@APP.route("/users/all", methods=['GET'])
def server_users_all():
    token = request.args.get('token')
    return dumps(users_all(token))
    
@APP.route("/user/profile", methods=['GET'])
def server_user_profile():
    token = request.args.get('token')
    u_id = make_int(request.args.get('u_id'))
    return dumps(user_profile(token,u_id))

@APP.route("/user/profile/setname", methods=['PUT'])
def server_user_setname():
   setname_details = request.get_json()
   token = setname_details['token']
   name_first = setname_details['name_first']
   name_last = setname_details['name_last']
   return dumps(user_profile_setname(token,name_first,name_last))

@APP.route("/user/profile/setemail", methods=['PUT'] )
def server_user_setemail():
    setemail_details = request.get_json()
    token = setemail_details['token']
    new_email = setemail_details['email']
    return dumps(user_profile_setemail(token,new_email))
    
@APP.route("/user/profile/sethandle", methods=['PUT'])
def server_user_sethandle():
    sethandle_details = request.get_json()
    token = sethandle_details['token']
    handle_str = sethandle_details['handle_str']
    return dumps(user_profile_sethandle(token,handle_str))
    
@APP.route("/user/profile/uploadphoto", methods=['POST'])
def server_user_uploadphoto():
    upload_details = request.get_json()
    token = upload_details['token']
    image_url = upload_details['img_url']
    x_start = make_int(upload_details['x_start'])
    y_start = make_int(upload_details['y_start'])
    x_end = make_int(upload_details['x_end']) 
    y_end = make_int(upload_details['y_end'])
    return dumps(user_profile_upload(token,image_url,x_start,y_start,x_end,y_end))

    
@APP.route('/user_photos/<path:path>')
def send_js(path):
    return send_from_directory('',path)
    
    
@APP.route("/standup/start", methods=['POST'])
def server_standup_start():
    data = request.get_json()
    token = data['token']
    channel_id = make_int(data['channel_id'])
    length = data['length']
    return dumps(standup_start(token,channel_id,length))

@APP.route("/standup/active", methods=['GET'])
def server_standup_active():
    token = request.args.get('token')
    channel_id = make_int(request.args.get('channel_id'))
    return dumps(standup_active(token,channel_id))

@APP.route("/standup/send", methods=['POST'])
def server_standup_send():
    data = request.get_json()
    token = data['token']
    channel_id = make_int(data['channel_id'])
    message = data['message']
    return dumps(standup_send(token,channel_id,message))
    
@APP.route("/clear", methods=['DELETE'])
def server_delete():
    clear()
    return dumps({})
    
@APP.route("/admin/userpermission/change", methods=['POST'])
def server_userpermission_change():
    change_info = request.get_json()
    token = change_info['token']
    u_id = make_int(change_info['u_id'])
    permission_id = change_info['permission_id']
    return dumps(admin_userpermission_change(token,u_id,permission_id))
    
@APP.route("/search", methods=['GET'])
def server_search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(search(token, query_str))

if __name__ == "__main__":
    prt = 0
    if len(sys.argv) == 2:
        prt = sys.argv[1]
    APP.run(port=prt) # Do not edit this port
