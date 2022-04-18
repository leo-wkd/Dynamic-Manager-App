import os
import boto3
from app import s3_client
from app import webapp
from app import db
from app.models.create_tables import Photo, Cache, AutoScalingConfig, MemNode
'''
def clear_old_contents(dir):
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
'''

def clear_old_contents():
    response = s3_client.list_objects_v2(Bucket=webapp.config["BUCKET_NAME"], Prefix="images/")
    if response.get("Contents") is None:
        return
    for object in response["Contents"]:
        s3_client.delete_object(Bucket=webapp.config["BUCKET_NAME"], Key=object["Key"])

def clear_rds():
    db.session.query(Photo).delete()
    db.session.query(Cache).delete()
    db.session.query(AutoScalingConfig).delete()
    db.session.query(MemNode).delete()
    db.session.commit()
