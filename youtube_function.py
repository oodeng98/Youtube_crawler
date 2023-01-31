import requests
import json
import pandas as pd
import configparser
from googleapiclient.discovery import build


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['Youtube_crawler']['youtube_api_key']


def youtube_category_list():
    api_key = 'AIzaSyCEF_EY242evGW5xkDVnIsVWzj6vJWT4D0'

    params = {
        'part': 'id',
        'regionCode': 'kr',
        'key': api_key
    }
    response = json.loads(requests.get('https://www.googleapis.com/youtube/v3/videoCategories', params=params).text)

    dic = []
    for item in response['items']:
        category_id = item['id']
        category = item['snippet']['title']
        dic.append((category_id, category))

    df = pd.DataFrame(dic)
    df.to_excel('youtube category id.xlsx', index=False, header=['category_id', 'category'])


def comment():
    api_key = get_api_key()
    video_id = 'X3EbONEL9f8'

    comments = []
    api_obj = build('youtube', 'v3', developerKey=api_key)
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append(
                [comment['textOriginal'], comment['authorDisplayName'], comment['publishedAt'], comment['likeCount']])

            if item['snippet']['totalReplyCount'] > 0:
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
    df.to_excel('results.xlsx', header=['comment', 'author', 'date', 'num_likes'], index=None)




if __name__ == "__main__":
    print(get_api_key())
