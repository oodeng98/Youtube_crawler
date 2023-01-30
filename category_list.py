import requests
import json
import pandas as pd

api_key = 'AIzaSyCEF_EY242evGW5xkDVnIsVWzj6vJWT4D0'

params = {
    'part': 'id',
    'regionCode': 'kr',
    'key': api_key
}
response = json.loads(requests.get('https://www.googleapis.com/youtube/v3/videoCategories', params=params).text)
# response = json.dumps(response, indent=4, sort_keys=True)

dic = []
for item in response['items']:
    category_id = item['id']
    category = item['snippet']['title']
    dic.append((category_id, category))

df = pd.DataFrame(dic)
df.to_excel('youtube category id.xlsx', index=False, header=['category_id', 'category'])