import googleapiclient.errors
from googleapiclient.discovery import build
import urllib.request
import datetime
import pandas as pd
import os
from tqdm import tqdm
from youtube_function import video_category_list, get_api_key
import time
import json

api_key = get_api_key()
youtube = build('youtube', 'v3', developerKey=api_key)

if 'video_category.json' not in os.listdir():
    video_category_list()
    time.sleep(10)

with open('./video_category.json', 'r') as file:
    category_dic = json.load(file)


now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d-%H-%M")
filePath = f'./most_popular_videos/{now}'
data = []
if 'most_popular_videos' not in os.listdir():
    os.mkdir('most_popular_videos')

if now not in os.listdir('./most_popular_videos'):
    os.mkdir(filePath)
    os.mkdir(filePath + '/image')

for categoryId in tqdm(category_dic):
    count = 0
    try:
        response = youtube.videos().list(part='snippet, statistics, topicDetails', chart='mostPopular', regionCode='kr',
                                         videoCategoryId=categoryId, maxResults=50).execute()
    except googleapiclient.errors.HttpError:
        continue
    # response = json.dumps(response['items'][0], indent="\t")
    # print(response)
    # exit()
    for item in response['items']:
        channelTitle = item['snippet']['channelTitle']
        channelId = item['snippet']['channelId']
        description = item['snippet']['description']
        title = item['snippet']['title']
        print(title)
        publishedAt = item['snippet']['publishedAt']  # 이거 년월일시분으로 나눠야할듯
        try:
            tags = item['snippet']['tags']
        except KeyError:
            tags = ''

        videoId = item['id']
        imageFilePath = filePath + f'/image/{videoId}.jpg'
        urllib.request.urlretrieve(item['snippet']['thumbnails']['default']['url'], imageFilePath)

        viewCount = item['statistics']['viewCount']
        likeCount = item['statistics']['likeCount']
        commentCount = item['statistics']['commentCount']

        topicCategories = item['topicDetails']['topicCategories']

        data.append((channelTitle, channelId, description, title, publishedAt, tags, imageFilePath, videoId))
df = pd.DataFrame(data, columns=['channelTitle', 'channelId', 'description', 'title', 'publishedAt', 'tags',
                                 'imageFilePath', 'videoId'])
df.to_csv(filePath + '/info.csv', index=False)
