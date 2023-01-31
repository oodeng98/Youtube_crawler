import googleapiclient.errors
from googleapiclient.discovery import build
import urllib.request
import datetime
import pandas as pd
import os
from tqdm import tqdm
from youtube_function import youtube_category_list, get_api_key

api_key = get_api_key()
youtube = build('youtube', 'v3', developerKey=api_key)

if 'youtube category id.xlsx' not in os.listdir():
    youtube_category_list()
category_list = pd.read_excel('youtube category id.xlsx')

now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d-%H-%M")
filePath = f'./most_popular_videos/{now}/'
data = []
if now not in os.listdir('./most_popular_videos'):
    os.mkdir(filePath)
    os.mkdir(filePath + 'image')

for categoryId in tqdm(category_list['category_id']):
    try:
        response = youtube.videos().list(part='snippet', chart='mostPopular', regionCode='kr',
                                         videoCategoryId=categoryId).execute()
    except googleapiclient.errors.HttpError:
        continue

    for item in response['items']:
        channelTitle = item['snippet']['channelTitle']
        channelId = item['snippet']['channelId']
        description = item['snippet']['description']
        title = item['snippet']['title']
        publishedAt = item['snippet']['publishedAt']
        try:
            tags = item['snippet']['tags']
        except KeyError:
            tags = ''
        url = item['snippet']['thumbnails']['default']['url']
        videoId = url.split('/')[-2]
        # print(title)
        imageFilePath = filePath + f'image/{videoId}.jpg'
        urllib.request.urlretrieve(url, imageFilePath)

        data.append((channelTitle, channelId, description, title, publishedAt, tags, imageFilePath, videoId))
df = pd.DataFrame(data, columns=['channelTitle', 'channelId', 'description', 'title', 'publishedAt', 'tags',
                                 'imageFilePath', 'videoId'])
df.to_csv(filePath + 'info.csv', index=False)
