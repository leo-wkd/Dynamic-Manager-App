from time import sleep
import boto3
import random
import requests
from datetime import datetime, timedelta
from ec2_metadata import ec2_metadata
import requests
import pymysql
from sqlalchemy import true
from aws import AWSClient

if __name__ == '__main__':
    print("AutoScaler Works")

    awscli = AWSClient()
    '''
    db = pymysql.connect(host="ece1779-a2.cdq1cmhoazdn.us-east-1.rds.amazonaws.com",
                        user="admin",password="19971121",database="webapp_2")
    cursor = db.cursor()
    '''
    while True:
        db = pymysql.connect(host="ece1779-a2.cdq1cmhoazdn.us-east-1.rds.amazonaws.com",
                        user="admin",password="19971121",database="webapp_2")
        cursor = db.cursor()
        sql = ''' select * from AutoScaling; '''
        cursor.execute(sql)
        data = cursor.fetchall()
        if not data:
            sleep(5)
            continue
        mode = data[0][1]
        maxThresh, minThresh = data[0][2], data[0][3]
        gRatio, sRatio = data[0][4], data[0][5]
        if mode == "auto":
            "Automatic Mode"
            metric = awscli.get_aggregate_metric()
            missRate = metric["MissRate"][-1]
            timestamps = metric["simpletime"][-1]
            if missRate > maxThresh:
                print(timestamps + "--- Auto Grow. {} > {}".format(missRate, maxThresh))
                awscli.grow_by_ratio(gRatio)
                
            elif missRate < minThresh:
                print(timestamps + "--- Auto Shrink {} < {}".format(missRate, minThresh))
                awscli.shrink_by_ratio(sRatio)
                
            sleep(60)
        else:
            sleep(5)
