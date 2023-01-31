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


def hot_video_list():
    youtube = build('youtube', 'v3', developerKey=get_api_key())

    if 'video_category.json' not in os.listdir():
        video_category_list()
        time.sleep(10)

    with open('./video_category.json', 'r') as file:
        category_dic = json.load(file)

    if 'most_popular_videos' not in os.listdir():
        os.mkdir('most_popular_videos')

    now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d-%H-%M")
    file_path = f'./most_popular_videos/{now}'
    data = []

    if now not in os.listdir('./most_popular_videos'):
        os.mkdir(file_path)
        os.mkdir(file_path + '/image')

    ret = []

    for categoryId in tqdm(category_dic):
        try:
            response = youtube.videos().list(part='snippet, statistics, topicDetails', chart='mostPopular',
                                             regionCode='kr',
                                             videoCategoryId=categoryId, maxResults=50).execute()
        except googleapiclient.errors.HttpError:
            continue

        for item in response['items']:
            popular_video = {}
            video = {}
            channel = {}

            popular_video['confirmation_time'] = now
            popular_video['viewCount'] = item['statistics']['viewCount']
            popular_video['likeCount'] = item['statistics']['likeCount']
            popular_video['commentCount'] = item['statistics']['commentCount']
            popular_video['videoId'] = item['id']

            video['videoId'] = item['id']
            video['description'] = item['snippet']['description']
            video['title'] = item['snippet']['title']
            video['publishedAt'] = item['snippet']['publishedAt']
            try:
                video['tags'] = item['snippet']['tags']
            except KeyError:
                video['tags'] = ''
            imageFilePath = file_path + f'/image/{item["id"]}.jpg'
            video['imageFilePath'] = imageFilePath
            video['imageUrl'] = item['snippet']['thumbnails']['default']['url']
            try:
                video['topicCategories'] = item['topicDetails']['topicCategories']  # 이거 없는 경우는?
            except KeyError:
                print(item)
            video['channelId'] = item['snippet']['channelId']

            urllib.request.urlretrieve(video['imageUrl'], imageFilePath)

            channel['channelTitle'] = item['snippet']['channelTitle']
            channel['channelId'] = item['snippet']['channelId']

            data.append({'popular_video': popular_video, 'video': video, 'channel': channel})
            ret.append(item['id'])
            print(video['title'], item['topicDetails']['topicCategories'])
            return

    with open(file_path + './data.json', 'w', encoding='utf-8') as file:  # 파일 이름 설정해
        json.dump(data, file)

    return ret


def video_comment(video_id, filepath):
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
    hot_video_list()
