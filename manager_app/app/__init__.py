import imp
from flask import Flask
import boto3
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.aws import AWSClient
# from AutoScaler.aws import AWSClient

db = SQLAlchemy()
webapp = Flask(__name__)
webapp.config.from_object(Config)
s3_client = boto3.client("s3", aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
awscli = AWSClient()

from app import configure
from app import main
from app import display
from app import aws
from app import metrics

from app.models import create_tables



db.app = webapp
db.init_app(webapp)
# db.drop_all()
# db.create_all()

metrics.send_aggregate_metric(awscli)