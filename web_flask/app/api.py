import os
import base64
from urllib import response
import requests
import boto3
from uhashring import HashRing

from flask import render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import webapp
from app.models import modify_tables
# from app import ip_addr
from app import uhash
from app import s3_client
from app import uhash

from app.models.create_tables import Photo

# For testing purpose
# upload image
@webapp.route('/api/upload',methods=['POST'])
def upload():

    photo_name = request.form.get("key")
    new_photo = request.files['file']
    if photo_name == "" and new_photo.filename == "":
        return jsonify(success = "false", error = {"code": 400, "message": "No input!"})

    elif photo_name == "":
        return jsonify(success = "false", error = {"code": 400, "message": "Please assign a key for your photo!"})

    elif new_photo.filename == "":
        return jsonify(success = "false", error = {"code": 400, "message": "Please select a photo!"})

    #check valid photo type
    if not check_valid_type(new_photo.filename):
        return jsonify(success = "false", error = {"code": 400, "message": "Please upload photo in jpg, gif, png, jpeg type!"})

    #save file to S3
    new_addr = "images/" + new_photo.filename
    s3_client.put_object(Body=request.files['file'], Bucket=webapp.config["BUCKET_NAME"], Key=new_addr)

    #check if photo_name(key) exists in database
    photo = Photo.query.filter_by(key = photo_name).first()
    if photo is not None:
        modify_tables.change_photo(photo, new_addr)
    else:
        modify_tables.add_photo(photo_name, new_addr)
    
    #Invalidate cache
    json_data = {"key": photo_name}
    ip_addr = uhash.get_node(photo_name)
    cache_response = requests.post(ip_addr + '/invalidate', json=json_data)

    return jsonify(success = "true")


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF', 'jpeg', 'JPEG'])

def check_valid_type(name):
    return '.' in name and name.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# For testing purpose
# search photo by key
@webapp.route('/api/key/<key_value>',methods=['POST'])
def search_by_key(key_value):

    if key_value == "":
        return jsonify(success = "false", error = {"code": 400, "message": "Please input a key!"})

    # First Search in Cache 
    json_data = {"key": key_value}
    ip_addr = uhash.get_node(key_value)
    response = requests.post(ip_addr + '/get', json=json_data)
    cache_response = response.json()

    # Find image in cache
    if cache_response["value"] != "MISS":
        #image_base64 = str(base64.b64encode(cache_response), encoding='utf-8')
        image_base64 = cache_response["value"]
    else:
        addr = modify_tables.search_photo(key_value)
        if addr == "":
            return jsonify(success = "false", error = {"code": 400, "message": "No photo found!"})
        
        # get file from S3
        data = s3_client.get_object(Bucket=webapp.config["BUCKET_NAME"], Key=addr)
        image = data.get('Body').read()
        image_base64 = str(base64.b64encode(image), encoding='utf-8')
        # PUT in cache
        json_data = {"key": key_value, "value": image_base64}
        cache_response = requests.post(ip_addr + '/put', json=json_data)
    
    return jsonify(success="true", content=image_base64)

# For testing purpose
# list all keys
@webapp.route('/api/list_keys',methods=['GET', 'POST'])

def list_keys():
    key_list = []
    modify_tables.query_all(key_list)
    return jsonify(success = "true", keys = key_list)