import pandas as pd
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pandas.core.indexes import category
from oauth2client.tools import argparser

DEVELOPER_KEY = "Your key"

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)

# search_response = youtube.search().list(
#     q="SBS 뉴스",
#     order="relevance",
#     part="snippet",
#     maxResults=50
# ).execute()
# print(search_response)
# channel_id = search_response['items'][0]['id']['channelId']

# 채널ID 입력
channel_id = "UCzKH70qfN_yuXq3s91fdwmg"

playlists = youtube.playlists().list(
    channelId=channel_id,
    part="snippet",
    maxResults=500
).execute()
# print(playlists)
# 채널 플레이리스트 가져오기
ids = []
titles = []
for i in playlists['items']:
    ids.append(i['id'])
    titles.append(i['snippet']['title'])

df = pd.DataFrame([ids, titles]).T
df.columns = ["Playlists", 'Titles']

print(len(df))
print(df)

video_names = []
video_ids = []
date = []

# 맨 뒤에 숫자는 플레이리스트 id
for k in range(len(df)):
    list_id = df['Playlists'][k]
    playlist_videos = youtube.playlistItems().list(
        playlistId=list_id,
        part='snippet',
        maxResults=50000
    )
    playlistitems_list_response = playlist_videos.execute()

    # 해당 플레이리스트의 영상 가져오기

    for v in playlistitems_list_response['items']:
        video_names.append(v['snippet']['title'])
        video_ids.append(v['snippet']['resourceId']['videoId'])
        date.append(v['snippet']['publishedAt'])

vdf = pd.DataFrame([date, video_names, video_ids]).T
vdf.columns = ['Date', 'Title', 'Ids']

print(vdf)
# vdf.to_excel("도날드 트럼프.xlsx")

# 영상 정보 가져오기
dates = []
category_id = []
views = []
likes = []
dislikes = []
comments = []
fan_prop = []
mins = []
seconds = []
title = []

for u in range(len(vdf)):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=vdf['Ids'][u]
    )
    response = request.execute()

    if response['items'] == []:
        ids.append("-")
        category_id.append("-")
        views.append("_")
        likes.append("_")
        dislikes.append("_")
        comments.append("_")
    elif (int(response['items'][0]['statistics']['viewCount']) < 100000):
        continue
    else:
        dates.append(v['snippet']['publishedAt'])
        title.append(response['items'][0]['snippet']['title'])
        category_id.append(response['items'][0]['snippet']['categoryId'])
        views.append(response['items'][0]['statistics']['viewCount'])
        try:
            likes.append(response['items'][0]['statistics']['likeCount'])
        except:
            likes.append("Can't access")
        try:
            dislikes.append(response['items'][0]['statistics']['dislikeCount'])
        except:
            dislikes.append("Can't access")
        try:
            comments.append(response['items'][0]['statistics']['commentCount'])
        except:
            comments.append("Can't access")
        try:
            fan_prop.append(
                round((int(likes[-1])+int(dislikes[-1]))/int(views[-1])*100, 2))
        except:
            fan_prop.append("Can't access")

video_stats = pd.DataFrame(
    [dates, title, category_id, views, likes, dislikes, comments, fan_prop]).T
video_stats.columns = ['date', 'title', 'categoryId',
                       'views', 'likes', 'dislikes', 'comments', 'Proportion']

video_stats.to_excel("TV5MONDE Info.xlsx")
