import boto3
import logging
from pprint import pprint
from botocore.exceptions import ClientError


def access(type='client'):
    if type == 'client':
        return boto3.client('s3')
    else:
        return boto3.resource('s3')


def create_bucket(bucket_name):
    s3 = access()
    try:
        s3.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def get_bucket_list():
    s3 = access()
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        print(f'{bucket["Name"]}')


def upload_file(file_name, bucket_name, key):
    # key는 파일이 S3에서 저장될 위치를 의미한다.
    # S3에서 존재하지 않는 폴더를 지정하면 폴더가 생성된다.
    s3 = access()
    try:
        response = s3.upload_file(file_name, bucket_name, key)
        # with open("FILE_NAME", "rb") as f:
        #     s3.upload_fileobj(f, "BUCKET_NAME", "OBJECT_NAME")
        # 이렇게도 가능하다
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(bucket_name, object_name, file_name):
    # object_name은 다운로드 받을 파일의 이름을 의미한다
    s3 = access()
    try:
        response = s3.download_file(bucket_name, object_name, file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == '__main__':
    print('S3 실행')
    # upload_file('most_popular_videos/image/0BbFh3LWOpM.jpg', 'parenhark', 'Youtubee_image/0BbFh3LWOpM.jpg')
