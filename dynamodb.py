import boto3
from boto3.dynamodb.conditions import Key
from pprint import pprint


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
            KeySchema=[{'AttributeName': 'video_id', 'KeyType': 'HASH'},
                       {'AttributeName': 'title', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'video_id', 'AttributeType': 'S'},
                                  {'AttributeName': 'title', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
        print('Video 생성 완료')
    except Exception as e:
        print('Error occur!')
        print(e)


def put_item(table_name, info):
    table = access_dynamodb('resource').Table(table_name)
    table.put_item(Item=info)


def get_item(table_name, key):
    table = access_dynamodb('resource').Table(table_name)
    ret = table.get_item(Key=key)  # hash key, sort key 다 줘야 함
    return ret


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


def scan(table_name):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan
    # 자세한 내용은 윗 링크 참조
    # 지금 코드는 테이블의 전체 데이터를 가져오도록 설계되어있음
    table = access_dynamodb('resource').Table(table_name)
    response = table.scan()
    # for item in response:
    #     print(response[item])
    return response


def conditional_search(table_name, key):
    table = access_dynamodb('resource').Table(table_name)
    name_key_dic = {'Video': 'video_id', 'Comment': 'authorChannelId'}
    query = {'KeyConditionExpression': Key(name_key_dic[table_name]).eq(key)}
    return table.query(**query)


def update_item(table_name, key, var, value, action):
    table = access_dynamodb('resource').Table(table_name)
    ret = table.update_item(Key=key, ReturnValues='ALL_NEW',
                            AttributeUpdates={var: {'Value': value, 'Action': action}})  # Value or Action
    # AttributeUpdates, Expected, ConditionalOperator, ReturnValues, ReturnConsumedCapacity, ReturnItemCollectionMetrics
    # UpdateExpression, ConditionExpression, ExpressionAttributeNames, ExpressionAttributeValues
    return ret


def update_comment(table_name, video_id, new_comments):
    origin = conditional_search(table_name, video_id)
    before_comments = origin['Items'][0]['comments']
    for comment in new_comments:
        before_comments['test2'] = 'check?'
    update_item('Video', {'video_id': video_id, 'title': origin['Items'][0]['title']}, 'comments', comments, 'PUT')
    pprint(conditional_search('Video', 'fk8vvmHIWAA')['Items'])


if __name__ == '__main__':
    print('dynamodb.py 실행')
