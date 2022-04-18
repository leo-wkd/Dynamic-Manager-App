import imp
from multiprocessing.sharedctypes import Value
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
from app import s3_client
from app import uhash

from app.models.create_tables import Photo

@webapp.route('/api/upload/form',methods=['GET'])
#Return photo upload form
def upload_image_form():
    return render_template("upload_form.html")

@webapp.route('/api/upload_image',methods=['POST'])
def upload_image():

    photo_name = request.form.get("key")
    new_photo = request.files['file']
    if photo_name == "" and new_photo.filename == "":
        return render_template("returnPage.html", content="No input!")

    elif photo_name == "":
        return render_template("returnPage.html", content="Please assign a key for your photo!")

    elif new_photo.filename == "":
        return render_template("returnPage.html", content="Please select a photo!")

    #check valid photo type
    if not check_valid_type(new_photo.filename):
        return render_template("returnPage.html", content="Please upload photo in jpg, jpeg, gif, png type!")

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

    return render_template("returnPage.html", content="Successfully upload your photo!")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF', 'jpeg', 'JPEG'])

def check_valid_type(name):
    return '.' in name and name.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@webapp.route('/api/search/form',methods=['GET'])

def search_image_form():
    return render_template("search_form.html")

# search image from key
@webapp.route('/api/search',methods=['POST'])

def search_image():

    photo_name = request.form.get("key")

    if photo_name == "":
        return render_template("returnPage.html", content="Please input a key!")

    # First Search in Cache 
    json_data = {"key": photo_name}
    ip_addr = uhash.get_node(photo_name)
    response = requests.post(ip_addr + '/get', json=json_data)
    cache_response = response.json()

    # Find image in cache
    if cache_response["value"] != "MISS":
        #image_base64 = str(base64.b64encode(cache_response["value"]), encoding='utf-8')
        image_base64 = cache_response["value"]
    else:
        addr = modify_tables.search_photo(photo_name)
        if addr == "":
            return render_template("returnPage.html", content="No photo found!")

        # get file from S3
        data = s3_client.get_object(Bucket=webapp.config["BUCKET_NAME"], Key=addr)
        image = data.get('Body').read()
        image_base64 = str(base64.b64encode(image), encoding='utf-8')
        json_data = {"key": photo_name, "value": image_base64}
        cache_response = requests.post(ip_addr + '/put', json=json_data)
    
    return render_template("view.html", name=photo_name, content=image_base64)


# list all keys
@webapp.route('/api/key_display',methods=['GET', 'POST'])

def display_image_name():
    key_list = []
    modify_tables.query_all(key_list)
    return render_template("returnPage.html", content=key_list)


# update uhash
@webapp.route('/uhash_add',methods=['POST'])
def add_uhash():
    input = request.get_json()
    ins_id = input["id"]
    ip_addr = input["ip"]
    uhash.add_node(ip_addr)
    modify_tables.add_ins(ins_id, ip_addr)
    return jsonify({"msg": "OK"})

@webapp.route('/uhash_shrink',methods=['POST'])
def remove_uhash():
    input = request.get_json()
    ins_id = input["id"]
    ip_addr = input["ip"]
    uhash.remove_node(ip_addr)
    modify_tables.remove_ins(ins_id, ip_addr)
    return jsonify({"msg": "OK"})

