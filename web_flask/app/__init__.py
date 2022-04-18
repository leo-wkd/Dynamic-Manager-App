import imp
from flask import Flask
import boto3
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from uhashring import HashRing

db = SQLAlchemy()
webapp = Flask(__name__)
webapp.config.from_object(Config)
s3_client = boto3.client("s3", aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
uhash = HashRing()

print("stage1")
# ip of cache for remote access
# ip_addr = "http://54.152.50.47:5001"

from app import photos
from app import cache
from app import api
from app import main
from app.init_cache import AWSClient

from app.models import create_tables
from app.models import clear_storage

clear_storage.clear_old_contents()

db.app = webapp
db.init_app(webapp)
# db.drop_all()
# clear_storage.clear_rds()
db.create_all()
print("stage2")

aswcli = AWSClient()
aswcli.grow_by_1()
print("stage3")
