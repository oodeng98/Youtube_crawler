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

import S3
import dynamodb
from pprint import pprint
import sys


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
    if 'image' not in os.listdir():
        os.mkdir('image')

    if 'image_list.json' not in os.listdir():
        with open('./image_list.json', 'w', encoding='utf-8') as file:
            json.dump({}, file)


def image_download(id, image_list, imagefileurl, imagefilepath):
    if id not in image_list:
        img = requests.get(imagefileurl)
        image_list[id] = sys.getsizeof(img.content)
        with open(imagefilepath, 'wb') as image:
            image.write(img.content)


def video_collect():
    now = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
    youtube = build('youtube', 'v3', developerKey=get_api_key())
    with open('./video_category.json', 'r') as file:
        category_dic = json.load(file)
    with open('./image_list.json', 'r') as file:
        image_list = json.load(file)

    channel = set()
    for categoryId in tqdm(category_dic):
        try:
            response = youtube.videos().list(part='id, snippet, statistics, topicDetails', chart='mostPopular',
                                             regionCode='kr',
                                             videoCategoryId=categoryId, maxResults=50).execute()
        except googleapiclient.errors.HttpError as e:
            print(e)
            continue

        for rank, item in enumerate(response['items']):
            if rank == 10:
                return
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
            print(video['title'])
            imageFilePath = f'./image/{item["id"]}.jpg'
            video['thumbnailFilePath'] = imageFilePath
            for image in ['maxres', 'standard', 'high', 'medium', 'default']:
                try:
                    video['thumbnailUrl'] = item['snippet']['thumbnails'][image]['url']
                    break
                except KeyError:
                    continue
            try:
                video['topicCategories'] = item['topicDetails']['topicCategories']
            except KeyError:
                pass

            dynamodb.update_item('Youtube', {'Item': 'Video', 'Id': item['id']}, 'data', [video], 'ADD')
            image_download(item['id'], image_list, video['thumbnailUrl'], imageFilePath)
            # S3.upload_file(imageFilePath, 'parenhark', f'Youtube_image/{item["id"]}.jpg')
            channel.add(item['snippet']['channelId'])

    channel_id = []
    for index, i in enumerate(channel):
        channel_id.append(i)
        if index % 50 == 49:
            channel_collect(channel_id)
            channel_id = []

    return channel


def channel_collect(channel_id):  # channel_id는 list 형태도 무관
    now = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
    with open('./image_list.json', 'r') as file:
        image_list = json.load(file)
    youtube = build('youtube', 'v3', developerKey=get_api_key())
    response = youtube.channels().list(part='snippet, statistics, topicDetails', id=channel_id, maxResults=50).execute()
    for item in response['items']:
        channel = {'confirmationAt': now}
        for snip in 'title description customUrl country'.split():
            try:
                channel[snip] = item['snippet'][snip]
            except KeyError:
                pass
        print(channel['title'])

        imageFilePath = f'./image/{item["id"]}.jpg'
        channel['thumbnailFilePath'] = imageFilePath
        for image in ['high', 'medium', 'default']:
            try:
                channel['thumbnailUrl'] = item['snippet']['thumbnails'][image]['url']
                break
            except KeyError:
                continue
        for stat in 'viewCount subscriberCount videoCount':
            channel[stat] = item['statistics'][stat]
        try:
            channel['topicCategories'] = item['topicDetails']['topicCategories']
        except KeyError:
            pass
        dynamodb.update_item('Youtube', {'Item': 'Channel', 'Id': item['id']}, 'data', [channel], 'ADD')
        image_download(item['id'], image_list, channel['thumbnailUrl'], imageFilePath)
        # S3.upload_file(imageFilePath, 'parenhark', f'Youtube_image/{item["id"]}.jpg')


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


def run():
    pre_work()
    sched = BackgroundScheduler(timezone='Asia/Seoul')
    sched.add_job(video_collect, 'cron', minute=0)
    sched.add_job(video_collect, 'cron', minute=10)
    sched.add_job(video_collect, 'cron', minute=20)
    sched.add_job(video_collect, 'cron', minute=30)
    sched.add_job(video_collect, 'cron', minute=40)
    sched.start()
    try:
        while True:
            time.sleep(6000)
            print('파일 아직 실행중')
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()


if __name__ == "__main__":
    print('youtube_function.py 실행')
    run()
