import boto3
import pandas as pd
import botocore


def access_dynamodb(type):
    # df = pd.read_csv('JeongTaeWan_accessKeys.csv')
    # aws_access_key_id = df['Access key ID'].values[0]
    # aws_secret_access_key = df['Secret access key'].values[0]
    # aws_default_region = "ap-northeast-2"
    # aws configure
    if type == 'client':
        return boto3.client('dynamodb')
    else:
        return boto3.resource('dynamodb')


def create_table():
    dynamodb = access_dynamodb('resource')
    try:
        table = dynamodb.create_table(
            TableName='Video',
            KeySchema=[
                {
                    'AttributeName': 'video_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'publishedAt',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'video_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'publishedAt',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.create_table(
            TableName='Channel',
            KeySchema=[
                {
                    'AttributeName': 'channelId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'channelTitle',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'channelId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'channelTitle',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.create_table(
            TableName='PopularVideo',
            KeySchema=[
                {
                    'AttributeName': 'popularvideo_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'confirmation_time',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'popularvideo_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'confirmation_time',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.create_table(
            TableName='Comment',
            KeySchema=[
                {
                    'AttributeName': 'comment_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'date',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'comment_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'date',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except:
        print('Error occur!')


def put_item(table_name, info):
    table = access_dynamodb('resource').Table(table_name)

    table.put_item(
        Item=info
    )


def get_item(table_name, key):
    table = access_dynamodb('resource').Table(table_name)
    table.get_item(Key=key)


if __name__ == '__main__':
    pass
