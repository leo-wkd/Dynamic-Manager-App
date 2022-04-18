from calendar import month
import boto3
import time
from datetime import datetime, timedelta
def get_data(client, instanceId, attribute, start_time, end_time):
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'statistics',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'Memcache',
                        'MetricName': attribute,
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId 
                            }
                        ]
                    },
                    'Period': 5,
                    'Stat': 'Sum',
                },
            },
        ],
        StartTime = start_time,
        EndTime = end_time
    )
    print(response)
    response = response['MetricDataResults'][0]
    return str(response['Values'])

if __name__ == '__main__':
    client = boto3.client('cloudwatch', aws_access_key_id="AKIA2YDCPYNJFV3KUWEJ", aws_secret_access_key="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", region_name = 'us-east-1')
    while True:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=60)
        print("num: " + get_data(client, "i-007452a3c2dfcdb9c", 'NumberOfItems', start_time, end_time))
        time.sleep(5)

