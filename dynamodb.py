import boto3


def access_dynamodb(type):
    if type == 'client':
        return boto3.client('dynamodb')
    else:
        return boto3.resource('dynamodb')


def create_table():
    dynamodb = access_dynamodb('client')
    try:
        table = dynamodb.create_table(
            TableName='Video',
            KeySchema=[
                {
                    'AttributeName': 'videoId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'publishedAt',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'videoId',
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
        print('Video 생성 완료')

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
        print('Channel 생성 완료')

        table = dynamodb.create_table(
            TableName='PopularVideo',
            KeySchema=[
                {
                    'AttributeName': 'videoId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'confirmation_time',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'videoId',
                    'AttributeType': 'S'
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
        print('PopularVideo 생성 완료')

        table = dynamodb.create_table(
            TableName='Comment',
            KeySchema=[
                {
                    'AttributeName': 'author',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'date',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'author',
                    'AttributeType': 'S'
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
        print('Comment 생성 완료')

    except Exception as e:
        print('Error occur!')
        print(e)


def put_item(table_name, info):
    table = access_dynamodb('resource').Table(table_name)
    table.put_item(Item=info)


def get_item(table_name, key):
    table = access_dynamodb('resource').Table(table_name)
    table.get_item(Key=key)


def get_table_list():
    resource = access_dynamodb('resource')
    print('현재 존재하는 테이블 목록은 ', end='')
    ret = []
    for table in resource.tables.all():
        name = table.name
        ret.append(name)
        print(name, end=' ')
    print('입니다.')
    return ret


def delete_table(table_name):
    table = access_dynamodb('resource').Table(table_name)
    ret = table.delete()
    print(ret)


if __name__ == '__main__':
    print('dynamodb.py 실행')
    create_table()
    get_table_list()
    # put_item('PopularVideo', {'videoId': '1', 'confirmation_time': '0'})  # 이건 된다

