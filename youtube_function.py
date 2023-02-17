import requests
import json
import configparser
from googleapiclient.discovery import build
import os
import time
import datetime
from tqdm import tqdm
import googleapiclient.errors
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
import dynamodb
from pprint import pprint


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['Youtube_crawler']['youtube_api_key']


def video_category_list():
    params = {
        'part': 'id',
        'regionCode': 'kr',
        'key': get_api_key()
    }
    response = json.loads(requests.get('https://www.googleapis.com/youtube/v3/videoCategories', params=params).text)
    dic = {0: 'integrated'}
    for item in response['items']:
        if item['snippet']['assignable']:
            category_id = item['id']
            category = item['snippet']['title']
            dic[category_id] = category

    with open('./video_category.json', 'w', encoding='utf-8') as file:
        json.dump(dic, file)
    return dic


def pre_work():
    now = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
    print(f'{now} program start')
    if 'video_category.json' not in os.listdir():
        video_category_list()
        time.sleep(2)
    for folder in ['most_popular_videos', 'channel']:
        if folder not in os.listdir():
            os.mkdir(folder)
            os.mkdir(folder + '/image')
        if 'image_list.json' not in os.listdir(folder + '/image/'):
            with open(folder + '/image_list.json', 'w', encoding='utf-8') as file:
                json.dump({}, file)
                time.sleep(2)


def video_collect():
    now = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
    youtube = build('youtube', 'v3', developerKey=get_api_key())
    with open('./video_category.json', 'r') as file:
        category_dic = json.load(file)
    file_path = './most_popular_videos'
    with open(file_path + '/image_list.json', 'r', encoding='utf-8') as file:
        image_list = json.load(file)

    channel = set()
    for categoryId in tqdm(category_dic):
        try:
            response = youtube.videos().list(part='id, snippet, statistics, topicDetails', chart='mostPopular',
                                             regionCode='kr',
                                             videoCategoryId=categoryId, maxResults=50).execute()  # 50이 최대
        except googleapiclient.errors.HttpError:
            continue

        for rank, item in enumerate(response['items']):
            video = {'confirmationAt': now, 'rank': rank + 1}
            for statistic in ['viewCount', 'likeCount', 'commentCount']:
                try:
                    video[statistic] = item['statistics'][statistic]
                except KeyError:
                    continue
            video['category'] = category_dic[categoryId]

            for snip in ['title', 'description', 'publishedAt', 'tags', 'channelId']:
                try:
                    video[snip] = item['snippet'][snip]
                except KeyError:
                    continue
            imageFilePath = file_path + f'/image/{item["id"]}.jpg'
            video['thumbnailFilePath'] = imageFilePath
            for image in ['maxres', 'standard', 'high', 'medium', 'default']:
                try:
                    if item["id"] not in image_list:
                        video['thumbnailUrl'] = item['snippet']['thumbnails'][image]['url']
                        image_list[item['id']] = 1  # 이것도 dynamodb 로 해결할 수 있을 것 같은데?
                        urllib.request.urlretrieve(video['thumbnailUrl'], imageFilePath)
                    break
                except KeyError:
                    continue
            try:
                video['topicCategories'] = item['topicDetails']['topicCategories']
            except KeyError:
                pass

            if dynamodb.check('Youtube', 'Video', item['id']):  # 이미 존재하는 경우
                dynamodb.update_item('Youtube', {'Item': 'Video', 'Id': item['id']}, 'data', [video], 'ADD')
            else:
                data = {'Item': 'Video', 'Id': item['id'], 'data': [video]}
                dynamodb.put_item('Youtube', data)

            channel.add(item['snippet']['channelId'])
            print('video:', video['title'])

    channel_id = []
    for index, i in enumerate(channel):
        channel_id.append(i)
        if index % 50 == 49:
            channel_collect(channel_id)
            channel_id = []

    with open(file_path + f'/image_list.json', 'w', encoding='utf-8') as file:
        json.dump(image_list, file)

    return channel


def channel_collect(channel_id):  # channel_id는 list 형태도 무관
    now = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
    youtube = build('youtube', 'v3', developerKey=get_api_key())
    response = youtube.channels().list(part='snippet, statistics, topicDetails', id=channel_id, maxResults=50).execute()  # 50이 최대
    for item in response['items']:
        channel = {'confirmationAt': now}
        for snip in 'title description customUrl country'.split():  # country 가 오류가 뜨는데?
            channel[snip] = item['snippet'][snip]

        imageFilePath = './channel' + f'/image/{item["id"]}.jpg'
        with open('./channel' + '/image_list.json', 'r', encoding='utf-8') as file:
            image_list = json.load(file)
        channel['thumbnailFilePath'] = imageFilePath
        for image in ['high', 'medium', 'default']:
            try:
                if item["id"] not in image_list:
                    channel['thumbnailUrl'] = item['snippet']['thumbnails'][image]['url']
                    image_list[item['id']] = 1  # 이것도 dynamodb 로 해결할 수 있을 것 같은데?
                    urllib.request.urlretrieve(channel['thumbnailUrl'], imageFilePath)
                break
            except KeyError:
                continue
        for stat in 'viewCount subscriberCount videoCount':
            channel[stat] = item['statistics'][stat]
        try:
            channel['topicCategories'] = item['topicDetails']['topicCategories']
        except KeyError:
            pass

        if dynamodb.check('Youtube', 'Channel', item['id']):  # 이미 존재하는 경우
            dynamodb.update_item('Youtube', {'Item': 'Channel', 'Id': item['id']}, 'data', [channel], 'ADD')
        else:
            data = {'Item': 'Channel', 'Id': item['id'], 'data': [channel]}
            dynamodb.put_item('Youtube', data)
        print('channel:', channel['title'])
    # dynamodb.put_item('Youtube', ???)  여기도 수정 요망


def video_comment(video_id):  # 수정 요망
    api_obj = build('youtube', 'v3', developerKey=get_api_key())
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

    while response:
        for item in response['items']:
            temp = item['snippet']['topLevelComment']['snippet']
            comment = {'authorChannelId': temp['authorChannelId']['value'], 'author': temp['authorDisplayName']}
            for i in ['textOriginal', 'publishedAt', 'likeCount']:
                comment[i] = temp[i]

            comment['reply'] = []
            if item['snippet']['totalReplyCount']:
                for reply_item in item['replies']['comments']:
                    temp = reply_item['snippet']
                    reply = {'authorChannelId': temp['authorChannelId']['value'], 'author': temp['authorDisplayName']}
                    for i in ['textOriginal', 'publishedAt', 'likeCount']:
                        reply[i] = temp[i]
                    comment['reply'].append(reply)

        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id,
                                                     pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            break
    # with open('comments' + f'/{video_id}.json', 'w', encoding='utf-8') as file:
    #     json.dump(comments, file)


def local_to_db():  # 이것도 변경해야함
    filepath = 'most_popular_videos/data/'
    file_lst = os.listdir(filepath)

    for f in file_lst:
        with open(filepath + f, 'r', encoding='utf-8') as file:
            js = json.load(file)
            for item in js:
                dynamodb.put_item('PopularVideo', item['popular_video'])
                dynamodb.put_item('Channel', item['channel'])
                dynamodb.put_item('Video', item['Video'])


def run():
    pre_work()
    sched = BackgroundScheduler()
    sched.add_job(video_collect, 'cron', minute=0)
    sched.add_job(channel_collect, 'cron', minute=0)
    sched.start()
    try:
        while True:
            time.sleep(6000)
            print('파일 아직 실행중')
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()


if __name__ == "__main__":
    print('youtube_function.py 실행')
    youtube = build('youtube', 'v3', developerKey=get_api_key())
    response = youtube.videos().list(part='id, snippet, statistics, topicDetails', id='KAu18xjSMRw',
                                     regionCode='kr').execute()  # 50이 최대
    pprint(response)
    '''
    {'etag': '_-KCtnchui7g8P6ij73vZ5jCcOo',
 'items': [{'etag': 'xxXjqU7pmmzbMpAN4LXS0d4bbRE',
            'id': 'KAu18xjSMRw',
            'kind': 'youtube#video',
            'snippet': {'categoryId': '22',
                        'channelId': 'UCMoAISkur2XdBt54uAK_Dsg',
                        'channelTitle': '정태완',
                        'description': '',
                        'liveBroadcastContent': 'none',
                        'localized': {'description': '',
                                      'title': '임베디드 SW경진대회 기술 동영상'},
                        'publishedAt': '2021-06-23T04:08:20Z',
                        'thumbnails': {'default': {'height': 90,
                                                   'url': 'https://i.ytimg.com/vi/KAu18xjSMRw/default.jpg',
                                                   'width': 120},
                                       'high': {'height': 360,
                                                'url': 'https://i.ytimg.com/vi/KAu18xjSMRw/hqdefault.jpg',
                                                'width': 480},
                                       'maxres': {'height': 720,
                                                  'url': 'https://i.ytimg.com/vi/KAu18xjSMRw/maxresdefault.jpg',
                                                  'width': 1280},
                                       'medium': {'height': 180,
                                                  'url': 'https://i.ytimg.com/vi/KAu18xjSMRw/mqdefault.jpg',
                                                  'width': 320},
                                       'standard': {'height': 480,
                                                    'url': 'https://i.ytimg.com/vi/KAu18xjSMRw/sddefault.jpg',
                                                    'width': 640}},
                        'title': '임베디드 SW경진대회 기술 동영상'},
            'statistics': {'commentCount': '0',
                           'favoriteCount': '0',
                           'likeCount': '0',
                           'viewCount': '59'},
            'topicDetails': {'topicCategories': ['https://en.wikipedia.org/wiki/Knowledge']}}],
 'kind': 'youtube#videoListResponse',
 'pageInfo': {'resultsPerPage': 1, 'totalResults': 1}}
    '''
