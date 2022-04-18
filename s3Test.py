import boto3
import tempfile
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

access_key = "AKIA2YDCPYNJFV3KUWEJ"
access_secret = "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"

def upload_test(file_name):
    s3_client = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=access_secret, region_name='us-east-1')
    s3_client.upload_file(file_name, "ece1779cc", "images/" + file_name)

def get_test(file_name):
    s3_client = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=access_secret, region_name='us-east-1')
    tmp = tempfile.NamedTemporaryFile(delete=False)
    with open(tmp.name, 'wb') as f:
        s3_client.download_fileobj("ece1779cc", "images/" + file_name, f)
        image = mpimg.imread(tmp.name)
    plt.figure(0)
    plt.imshow(image)
    plt.show()

def delete_test():
    s3_client = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=access_secret, region_name='us-east-1')
    response = s3_client.list_objects_v2(Bucket="ece1779cc", Prefix="images/")
    for object in response['Contents']:
        s3_client.delete_object(Bucket="ece1779cc", Key=object['Key'])

if __name__ == '__main__':
    src = "2.png"
    # upload_test(src)
    get_test(src)
    
    