import threading, time
from datetime import datetime, timedelta

def put_data(cloudwatch, instanceId, attribute, value, time):
    response = cloudwatch.put_metric_data(
        Namespace='Memcache',
        MetricData=[
            {
                'MetricName': attribute,
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': instanceId 
                    }
                ],
                'Timestamp': time,
                'Value': value, 
                'StorageResolution': 60
            },
        ]
    )

def put_statistics(cloudwatch, num, sz, req, hit_rate, miss_rate, worker_num, timestamp, id):
    put_data(cloudwatch, id, 'NumberOfItems', num, timestamp)
    put_data(cloudwatch, id, 'TotalSize', sz, timestamp)
    put_data(cloudwatch, id, 'NumberOfRequests', req, timestamp)
    put_data(cloudwatch, id, 'HitRate', hit_rate, timestamp)
    put_data(cloudwatch, id, 'MissRate', miss_rate, timestamp)
    put_data(cloudwatch, id, 'NumberOfWorkers', worker_num, timestamp)

def send_aggregate_metric(awscli):
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=60)
        running = awscli.get_state_instances('running')
        # print(running)
        worker_num = len(running)
        if worker_num == 0:
            print('No working memcache')
            raise IndexError 
        total_num = total_sz = total_req_this_min = miss_rate = 0
        for ins in running:
            statistics = awscli.get_statistics(ins['Id'], start_time, end_time)
            if not statistics['NumberOfItems']['Values']:
                continue
            total_num += statistics['NumberOfItems']['Values'][0] # total number of items of the pool
            total_sz += statistics['TotalSize']['Values'][0] # total size of items of the pool
            req_this_min = statistics['NumberOfRequests']['Values'][0] - statistics['NumberOfRequests']['Values'][-1] # number of req in this min of a single node
            total_req_this_min += req_this_min # total number of req of the pool in this minute
            miss_prev = statistics['MissRate']['Values'][-1] * statistics['NumberOfRequests']['Values'][-1] # miss reqs in 1 min ago of a single node
            miss_now = statistics['MissRate']['Values'][0] * statistics['NumberOfRequests']['Values'][0] # miss reqs currently of a single node
            miss_rate_this_min = (miss_now - miss_prev) / req_this_min if req_this_min else 0 # miss rate of a single node during this whole mintue
            miss_rate += miss_rate_this_min

            # print(ins['Id'], miss_rate_this_min, req_this_min)
            
        miss_rate /= worker_num
        hit_rate = 100 - miss_rate if total_req_this_min else 0

        print('aggregate', total_num, total_sz, total_req_this_min, hit_rate, miss_rate, worker_num, end_time)
        put_statistics(awscli.cloudwatch, total_num, total_sz, total_req_this_min, hit_rate, miss_rate, worker_num, end_time, 'aggregate')

    except IndexError:
        print('no data aviliable')

    sleep_time = 60 - (datetime.utcnow() - end_time).total_seconds()
    threading.Timer(sleep_time, send_aggregate_metric, args=[awscli]).start()
 
if __name__ == '__main__':
    send_aggregate_metric()

