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

    if 'video_category.json' not in os.listdir():
        video_category_list()
        time.sleep(10)

    with open('./video_category.json', 'r') as file:
        category_dic = json.load(file)

    file_path = './most_popular_videos'
    if 'most_popular_videos' not in os.listdir():
        os.mkdir('most_popular_videos')
        os.mkdir(file_path + '/image')
        os.mkdir(file_path + '/data')

    if 'image_list.json' not in os.listdir(file_path + '/image/'):
        with open(file_path + '/image_list.json', 'w', encoding='utf-8') as file:
            temp = {}
            json.dump(temp, file)
            time.sleep(10)
    with open(file_path + '/image_list.json', 'r', encoding='utf-8') as file:
        image_list = json.load(file)

    data = []
    for categoryId in tqdm(category_dic):
        print(category_dic[categoryId])
        try:
            response = youtube.videos().list(part='snippet, statistics, topicDetails', chart='mostPopular',
                                             regionCode='kr',
                                             videoCategoryId=categoryId, maxResults=50).execute()
        except googleapiclient.errors.HttpError:
            continue

        rank = 1
        for item in response['items']:
            popular_video = {}
            video = {}
            channel = {}

            popular_video['confirmation_time'] = now
            for statistic in ['viewCount', 'likeCount', 'commentCount']:
                try:
                    popular_video[statistic] = item['statistics'][statistic]
                except KeyError:
                    popular_video[statistic] = ''
            popular_video['videoId'] = item['id']
            popular_video['rank'] = rank
            popular_video['category'] = category_dic[categoryId]
            rank += 1

            video['videoId'] = item['id']
            for snip in ['description', 'title', 'publishedAt', 'tags', 'channelId']:
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

            channel['channelTitle'] = item['snippet']['channelTitle']
            channel['channelId'] = item['snippet']['channelId']

            data.append({'popular_video': popular_video, 'video': video, 'channel': channel})
    with open(file_path + f'/data/{now}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file)

    with open(file_path + f'/image_list.json', 'w', encoding='utf-8') as file:
        json.dump(image_list, file)

    return data


def video_comment(video_id, filepath='./comments'):
    if 'comments' not in os.listdir():
        os.mkdir('./comments')
        time.sleep(10)
    comments = []
    api_obj = build('youtube', 'v3', developerKey=get_api_key())
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append(
                [comment['textOriginal'], comment['authorDisplayName'], comment['publishedAt'], comment['likeCount']])

            if item['snippet']['totalReplyCount']:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    comments.append(
                        [reply['textOriginal'], reply['authorDisplayName'], reply['publishedAt'], reply['likeCount']])

        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id,
                                                     pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            break

    df = pd.DataFrame(comments)
    df.to_csv(filepath + f'/{video_id}.csv', header=['comment', 'author', 'date', 'num_likes'], index=False)


if __name__ == "__main__":
    # sched = BackgroundScheduler()  # 이렇게 실행해도 Blocking이랑 마찬가지지만 여러개를 실행할 수 잇다는 장점이 있는건가?
    # sched.add_job(hot_video_list, 'cron', minute=0)
    # sched.start()
    # try:
    #     while True:
    #         time.sleep(6000)
    #         print('파일 아직 실행중')
    # except (KeyboardInterrupt, SystemExit):
    #     sched.shutdown()
    hot_video_list()


