import boto3


def access(type):
    if type == 'client':
        return boto3.client('dynamodb')
    else:
        return boto3.resource('dynamodb')


def create_table():
    # KeySchema와 AttributeDefinitions의 AttributeName은 똑같아야 한다.
    dynamodb = access('client')
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
    # info에 Hash key와 Range key는 무조건 들어가야 함
    table = access('resource').Table(table_name)
    table.put_item(Item=info)


def get_item(table_name, partition_key, sort_key):
    table = access('resource').Table(table_name)
    ret = table.get_item(Key={'Item': partition_key, 'Id': sort_key})
    return ret


def get_table_list():
    dynamodb = access('resource')
    ret = []
    for table in dynamodb.tables.all():
        name = table.name
        ret.append(name)
    return ret


def delete_table(table_name):
    table = access('resource').Table(table_name)
    ret = table.delete()
    return ret


def scan(table_name):
    # scan은 테이블의 모든 테이터를 가져온다
    table = access('resource').Table(table_name)
    response = table.scan()
    return response


def conditional_search(table_name, keyconditionexpression):
    # query문을 활용한 검색, 이를 더 활용하고 싶다면 GSI, LSI등을 설정하는 것이 좋다.
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.query 참조
    table = access('resource').Table(table_name)
    ret = table.query(KeyConditionExpression=keyconditionexpression)
    return ret


def update_item(table_name, key, var, value, action):
    # 기존에 존재하지 않는 item을 update하는 경우, put_item과 다를게 없다.
    # action의 종류는 공식 문서를 참고하자
    table = access('resource').Table(table_name)
    ret = table.update_item(Key=key, ReturnValues='ALL_NEW',
                            AttributeUpdates={var: {'Value': value, 'Action': action}})
    return ret


def check(table_name, partition_key, check_id):
    # 주어진 partition_key(Hash key)와 check_id(Range key)를 가진 아이템이 이미 존재하는지 확인하는 함수
    item = get_item(table_name, partition_key, check_id)
    if 'Item' in item:
        return 1
    return 0


if __name__ == '__main__':
    print('dynamodb.py 실행')
