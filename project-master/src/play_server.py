from flask import Flask, request, send_from_directory
from helper import generate_img_url
# /src/user_photos/jrogan0_dp.jpg
APP = Flask(__name__,static_url_path='/user_photos/',static_folder='user_photos')

@APP.route('/user_photos/<path:path>')
def send_js(path):
   
    return send_from_directory('',path)

@APP.route('/img_url',methods=['GET'])
def send_img():
    return generate_img_url('bob')
    
if __name__=="__main__":
    APP.run(port=0)
    
    
 
