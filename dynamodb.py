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
        dynamodb.create_table(
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
    ret = []
    for table in resource.tables.all():
        name = table.name
        ret.append(name)
    return ret


def delete_table(table_name):
    table = access_dynamodb('resource').Table(table_name)
    ret = table.delete()
    return ret


def scan(table_name):
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


def check(table_name, partition_key, check_id):
    item = get_item(table_name, partition_key, check_id)
    if 'Item' in item:
        return 1
    return 0


if __name__ == '__main__':
    print('dynamodb.py 실행')
    update_item('Youtube', {'Item': 'Test', 'Id': '정태완1'}, 'data', ['정태완이다이자식아'], 'ADD')

