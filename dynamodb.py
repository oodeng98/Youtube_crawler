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
            TableName='Youtube',
            KeySchema=[{'AttributeName': 'Item', 'KeyType': 'HASH'},
                       {'AttributeName': 'Id', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'Item', 'AttributeType': 'S'},
                                  {'AttributeName': 'Id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
        print('Youtube table 생성 완료')
    except Exception as e:
        print('Error occur!')
        print(e)


def put_item(table_name, info):
    table = access_dynamodb('resource').Table(table_name)
    table.put_item(Item=info)


def get_item(table_name, partition_key, sort_key):
    table = access_dynamodb('resource').Table(table_name)
    ret = table.get_item(Key={'Item': partition_key, 'Id': sort_key})
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


def conditional_search(table_name, keyconditionexpression):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.query 참조
    table = access_dynamodb('resource').Table(table_name)
    ret = table.query(KeyConditionExpression=keyconditionexpression)
    return ret


def update_item(table_name, key, var, value, action):
    table = access_dynamodb('resource').Table(table_name)
    ret = table.update_item(Key=key, ReturnValues='ALL_NEW',
                            AttributeUpdates={var: {'Value': value, 'Action': action}})
    return ret


def update_pv(table_name, video_id, new_pv):
    update_item(table_name, {'Item': 'Video', 'Id': video_id}, 'popularVideo', new_pv, 'ADD')


if __name__ == '__main__':
    print('dynamodb.py 실행')


