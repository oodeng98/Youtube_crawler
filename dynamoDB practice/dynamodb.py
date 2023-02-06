import boto3
import pandas as pd


def access_dynamodb():
    df = pd.read_csv('JeongTaeWan_accessKeys.csv')
    aws_access_key_id = df['Access key ID'].values[0]
    aws_secret_access_key = df['Secret access key'].values[0]
    aws_default_region = "ap-northeast-2"
    dynamodb = boto3.client('dynamodb',
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=aws_default_region
                            )
    return dynamodb


def create_table():
    dynamodb = access_dynamodb()
    table = dynamodb.create_table(  # 데이터 스키마에 맞게 변형해놓기
        TableName='users',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'last_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # print(table)


def put_item():
    dynamodb = access_dynamodb()
    response = dynamodb.put_item(
        TableName='string',
        Item={
            'string': {
                'S': 'string',
                'N': 'string',
                'B': b'bytes',
                'SS': [
                    'string',
                ],
                'NS': [
                    'string',
                ],
                'BS': [
                    b'bytes',
                ],
                'M': {
                    'string': {'... recursive ...'}
                },
                'L': [
                    {'... recursive ...'},
                ],
                'NULL': True | False,
                'BOOL': True | False
            }
        },
        Expected={
            'string': {
                'Value': {
                    'S': 'string',
                    'N': 'string',
                    'B': b'bytes',
                    'SS': [
                        'string',
                    ],
                    'NS': [
                        'string',
                    ],
                    'BS': [
                        b'bytes',
                    ],
                    'M': {
                        'string': {'... recursive ...'}
                    },
                    'L': [
                        {'... recursive ...'},
                    ],
                    'NULL': True | False,
                    'BOOL': True | False
                },
                'Exists': True | False,
                'ComparisonOperator': 'EQ' | 'NE' | 'IN' | 'LE' | 'LT' | 'GE' | 'GT' | 'BETWEEN' | 'NOT_NULL' | 'NULL' | 'CONTAINS' | 'NOT_CONTAINS' | 'BEGINS_WITH',
                'AttributeValueList': [
                    {
                        'S': 'string',
                        'N': 'string',
                        'B': b'bytes',
                        'SS': [
                            'string',
                        ],
                        'NS': [
                            'string',
                        ],
                        'BS': [
                            b'bytes',
                        ],
                        'M': {
                            'string': {'... recursive ...'}
                        },
                        'L': [
                            {'... recursive ...'},
                        ],
                        'NULL': True | False,
                        'BOOL': True | False
                    },
                ]
            }
        },
        ReturnValues='NONE' | 'ALL_OLD' | 'UPDATED_OLD' | 'ALL_NEW' | 'UPDATED_NEW',
        ReturnConsumedCapacity='INDEXES' | 'TOTAL' | 'NONE',
        ReturnItemCollectionMetrics='SIZE' | 'NONE',
        ConditionalOperator='AND' | 'OR',
        ConditionExpression='string',
        ExpressionAttributeNames={
            'string': 'string'
        },
        ExpressionAttributeValues={
            'string': {
                'S': 'string',
                'N': 'string',
                'B': b'bytes',
                'SS': [
                    'string',
                ],
                'NS': [
                    'string',
                ],
                'BS': [
                    b'bytes',
                ],
                'M': {
                    'string': {'... recursive ...'}
                },
                'L': [
                    {'... recursive ...'},
                ],
                'NULL': True | False,
                'BOOL': True | False
            }
        }
    )