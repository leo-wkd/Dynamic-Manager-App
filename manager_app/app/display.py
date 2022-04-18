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
import json

@webapp.route('/api/display',methods=['GET'])

def display_charts():
    metric = awscli.get_aggregate_metric()
    content1 = metric["NumberOfWorkers"]
    content2 = metric["MissRate"]
    content3 = metric["HitRate"]
    content4 = metric["NumberOfItems"]
    content5 = metric["TotalSize"]
    content6 = metric["NumberOfRequests"]
    time_stamps = metric["simpletime"]

    return render_template('showChart.html', content1=json.dumps(content1), content2=json.dumps(content2), content3=json.dumps(content3), \
    content4=json.dumps(content4), content5=json.dumps(content5),content6=json.dumps(content6), time_stamps=json.dumps(time_stamps))