'''
The three steps for storing and serving images in iteration 3 are

1) Fetch image via url imgDown.py
2)Cropping image week8/crop.py
3)Serving Image week8/static.py


'''

from PIL import Image
import urllib.request

import requests
import sys
from flask import Flask, request, send_from_directory
from error import InputError,AccessError
import helper as hp
import imghdr




       

if __name__ == '__main__':
    
    
    #new_url = 'https://cf-images.us-east-1.prod.boltdns.net/v1/static/1125911414/cb661a70-e225-4226-a45f-7036d5325ebb/377a8493-7d73-48b0-bed5-b57659f2196e/1280x720/match/image.jpg'
    #new_url = 'https://deadline.com/wp-content/uploads/2020/11/AP_20205316415708.jpg?w=681&h=383&crop=1'
    #new_url = 'https://gomilkyway.com/misc/how-to-read-an-image-from-url-in-python-3-and-get-the-height-and-width/'
    new_url = 'https://kittyinpink.co.uk/wp-content/uploads/2016/12/facebook-default-photo-male_1-1.jpg'
    
    
    
    x1 = 0
    x2 = 320
    y1 = 0
    y2 = 320
    if not hp.check_valid_url(new_url):
        raise InputError('Invalid URL')  
    if not hp.is_url_jpg(new_url):
        raise InputError('URL is not a JPG')
    if not hp.is_equal_xy(x1,y1,x2,y2):
        raise InputError('End coordinates need to be >= to start coordinates')     
    if not hp.is_dimensions_correct(new_url,x1,y1,x2,y2):
        raise InputError('Coordinates are not withingthe dimensions of image at URL')
    token = 'asdfadsjasf3428KSD1'
    filename = 'default_dp.jpg' #should be generateflename()
    path = hp.download_jpg(new_url,filename)
    hp.crop_image(path,x1,y1,x2,y2)
    print(type(path))
    #Is this needed
    #urllib.request.urlcleanup()
    
    
''''
app = Flask(__name__,static_url_path='/static/')
def send_js(path):
    return send_from_directory('',path)


if __name__=="__main__":
    app.run()
'''
