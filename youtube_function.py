import requests
import json
import pandas as pd
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


def hot_video_list():
    now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d-%H")
    print(f'{now} program start')
    youtube = build('youtube', 'v3', developerKey=get_api_key())

    # 폴더 및 파일 생성 파트
    if 'video_category.json' not in os.listdir():
        video_category_list()
        time.sleep(5)

    with open('./video_category.json', 'r') as file:
        category_dic = json.load(file)

    file_path = './most_popular_videos'
    if 'most_popular_videos' not in os.listdir():
        os.mkdir('most_popular_videos')
        os.mkdir(file_path + '/image')

    if 'image_list.json' not in os.listdir(file_path + '/image/'):
        with open(file_path + '/image_list.json', 'w', encoding='utf-8') as file:
            temp = {}
            json.dump(temp, file)
            time.sleep(5)
    with open(file_path + '/image_list.json', 'r', encoding='utf-8') as file:
        image_list = json.load(file)

    # data = []
    for categoryId in tqdm(category_dic):
        try:
            response = youtube.videos().list(part='snippet, statistics, topicDetails', chart='mostPopular',
                                             regionCode='kr',
                                             videoCategoryId=categoryId, maxResults=50).execute()  # 50이 최대
        except googleapiclient.errors.HttpError:
            continue

        rank = 1
        for item in response['items']:
            video = {}
            popular_video = {'confirmation_time': now, 'rank': rank}

            for statistic in ['viewCount', 'likeCount', 'commentCount']:
                try:
                    popular_video[statistic] = item['statistics'][statistic]
                except KeyError:
                    popular_video[statistic] = ''
            popular_video['category'] = category_dic[categoryId]

            video['popularVideo'] = [popular_video]
            rank += 1

            if dynamodb.conditional_search('Video', item['id'])['Items']:
                dynamodb.update_item('Video', 'popularVideo', popular_video, 'ADD')
                continue

            video['video_id'] = item['id']
            for snip in ['title', 'description', 'publishedAt', 'tags', 'channelId', 'channelTitle']:
                try:
                    video[snip] = item['snippet'][snip]
                except KeyError:
                    video[snip] = ''
            # print(video['title'])

            imageFilePath = file_path + f'/image/{item["id"]}.jpg'
            video['imageFilePath'] = imageFilePath

            for image in ['maxres', 'standard', 'high', 'medium', 'default']:
                try:
                    if item["id"] not in image_list:
                        video['imageUrl'] = item['snippet']['thumbnails'][image]['url']
                        image_list[item['id']] = 1
                        urllib.request.urlretrieve(video['imageUrl'], imageFilePath)
                    break
                except KeyError:
                    continue
            try:
                video['topicCategories'] = item['topicDetails']['topicCategories']
            except KeyError:
                video['topicCategories'] = []
            dynamodb.put_item('Video', video)

    with open(file_path + f'/image_list.json', 'w', encoding='utf-8') as file:
        json.dump(image_list, file)

    # return data


def video_comment(video_id):
    api_obj = build('youtube', 'v3', developerKey=get_api_key())
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

    while response:
        for item in response['items']:
            pprint(item)
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


def daily_video_comment():
    # 하루치 hot_video list를 가져온 후 댓글을 가져오는 형태로 진행?
    # 오후 10시에 진행하면 되지 않을까 싶은데
    pass


def run():
    sched = BackgroundScheduler()
    sched.add_job(hot_video_list, 'cron', minute=0)
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
    response = youtube.videos().list(part='snippet, statistics, topicDetails', chart='mostPopular',
                                     regionCode='kr', maxResults=50).execute()  # 50이 최대
    pprint(response)

