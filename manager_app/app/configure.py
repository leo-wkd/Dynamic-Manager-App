from dataclasses import replace
from flask import render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import db
from app import webapp
from app.models import modify_tables
from app.models.create_tables import Cache
from app.models.create_tables import Statistics
import os
import requests
from app import s3_client
from app import awscli

####################    Mem Cache Node  ##################
@webapp.route('/api/cache/form',methods=['GET'])

def cache_config_form():
    return render_template("cache_config_form.html")

@webapp.route('/api/cache',methods=['POST'])

def cache_config():
    capacity = request.form.get("capacity", type=int)
    replace = request.form.get("replacement_policy")

    modify_tables.config_cache(capacity, replace)

    ip_list = modify_tables.get_ip()
    for ip_addr in ip_list:
        response = requests.get(ip_addr + '/refresh')
    cache_response = response.json()
    
    return render_template("returnPage.html", content=cache_response["msg"])

@webapp.route('/api/cache/clear_form',methods=['GET'])
def clear_cache_form():
    return render_template("clear.html")

@webapp.route('/api/cache/clear',methods=['GET', 'POST'])
def clear_cache():
    ip_list = modify_tables.get_ip()
    for ip_addr in ip_list:
        response = requests.get(ip_addr + '/clear')
    cache_response = response.json()
    return render_template("returnPage.html", content=cache_response["msg"])


####################    S3 and RDS   ##################
@webapp.route('/api/data/clear_form',methods=['Get'])
def data_clear_form():
    return render_template("delete.html")

@webapp.route('/api/data/clear',methods=['Get', 'POST'])
def delete_data():
    # delete info on database
    modify_tables.clear_photo()

    # delete images on S3
    response = s3_client.list_objects_v2(Bucket=webapp.config["BUCKET_NAME"], Prefix="images/")
    if response.get("Contents") is None:
        return render_template("returnPage.html", content="Actually no photo in system!")

    for object in response["Contents"]:
        s3_client.delete_object(Bucket=webapp.config["BUCKET_NAME"], Key=object["Key"])

    return render_template("returnPage.html", content="Successfully clear all photos!")


####################    Manager Pool  ##################
@webapp.route('/api/pool/form',methods=['GET'])

def pool_config_form():
    return render_template("pool_config_form.html")

@webapp.route('/api/pool',methods=['POST'])

def pool_config():
    maxThresh = request.form.get("maxThresh", type=int)
    minThresh = request.form.get("minThresh", type=int)
    exRatio = request.form.get("expandRatio", type=float)
    shRatio = request.form.get("shrinkRatio", type=float)

    modify_tables.config_scaler(maxThresh, minThresh, exRatio, shRatio)

    thresh_info = "Max miss rate threshold: {} --- Min miss rate threshold: {} --- ".format(maxThresh, minThresh)
    ratio_info = "Expand ratio: {} --- Shrink ratio: {}".format(exRatio, shRatio)
    return render_template("returnPage.html", content="Set Automatic Mode --- "+ thresh_info + ratio_info)

@webapp.route('/api/pool/grow',methods=['POST'])
def pool_grow():
    modify_tables.switch_mode()
    response = awscli.grow_by_1()
    return render_template("returnPage.html", content="Set Manual Mode --- " + response["msg"])

@webapp.route('/api/pool/shrink',methods=['POST'])
def pool_shrink():
    modify_tables.switch_mode()
    response = awscli.shrink_by_1()
    return render_template("returnPage.html", content="Set Manual Mode --- " + response["msg"])

