from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import time
import httplib2
import os
import numpy as np
import sys
import csv
import base64
import matplotlib.pyplot as plt
import unidecode
import dateutil
import datetime
import argparse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import streamlit.components as stc
timestr=time.strftime('%Y%m%d-%H%M%S')



YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
api_key = 'AIzaSyBfwQfMcFWVFIztDAr6qpAJ8KmImWFyJPw'
youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=api_key)

# ====================================================comment analyser part==========================================





commentbot = SentimentIntensityAnalyzer()

CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    with open("youtube-v3-discoverydocument.json", "r", encoding='utf-8') as f:
        doc = f.read()
        return build_from_document(doc, http=credentials.authorize(httplib2.Http()))


def get_comment_threads(youtube, video_id, comments=[], token=""):
    results = youtube.commentThreads().list(
        part="snippet",
        pageToken=token,
        videoId=video_id,
        maxResults=80,
        textFormat="plainText"
    ).execute()
    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        comments.append(text)

    if len(comments)>200:
        return comments

    if "nextPageToken" in results:
        return get_comment_threads(youtube, video_id, comments, results["nextPageToken"])
    else:
        return comments


#-----------------------------------------------END COMMENTS --------------------------------------------------------#

def youtube_mobie_review(options):    
    print(youtube)  
    search_response = youtube.search().list(q=options.q, part="id, snippet",
                                            maxResults=options.max_results).execute()
    video_ids=[]
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videoId = search_result["id"]["videoId"]
            video_ids.append(videoId)

    # print(video_ids)
    return video_ids    



def channelID_video(youtube,video_id,channel_id):
    request = youtube.videos().list(
        part="snippet",
        id=','.join(video_id)
    )

    response=request.execute()
    for i in range(len(response['items'])):
        channel_id.append(response['items'][i]['snippet']['channelId'])





# ---------------------------------------------------Video Score -------------------------------------------------------------------------------------#

def video_score(video_id):
    fresult= {"Channel Title":"","score":0,"views":0,"numcomments":0,"age":0,"likes":0,"positivenum":0,"negativenum":0,"neutralnum":0,"linknum":0,"title":"","vID":""}
    args = argparser.parse_args()
    args.videoid = video_id
    print(video_id)
    # st.write("Processing...")
    youtube = get_authenticated_service(args)
    try:
        video_comment_threads = get_comment_threads(youtube, args.videoid)
        with open('commentscraperfile.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for comment in video_comment_threads:
                writer.writerow([comment])
                writer.writerow("!@#$%U^&*()")

    except HttpError as e:
        st.write(" ==>An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    count=0
    with open("commentscraperfile.csv","r",errors='ignore', encoding='utf-8') as csvfile:
        for line in csvfile.read().split("\n!,@,#,$,%,U,^,&,*,(,)\n"):
            vs = commentbot.polarity_scores(line)
            if(count == len(video_comment_threads)):
                break
            count += 1
            if("https" in line):
                fresult["linknum"] +=1
            elif("http" in line):
                fresult["linknum"] +=1
            elif vs['compound']>= 0.05:
                fresult["positivenum"] +=1
            elif vs['compound']<= - 0.05:
                fresult["negativenum"] += 1
            else:
                fresult["neutralnum"] += 1

    request = youtube.videos().list(
        part="statistics,snippet",
        id=video_id
    )
    response = request.execute()
    fresult["views"]=response["items"][0]["statistics"]["viewCount"]
    fresult["likes"]=response["items"][0]["statistics"]["likeCount"]
    fresult["Channel Title"]=response["items"][0]["snippet"]["channelTitle"]
    fresult["title"]=response["items"][0]["snippet"]["title"]
    fresult["vID"]='https://www.youtube.com/watch?v='+video_id
    # fresult["fav"]=response["items"][0]["statistics"]["favoriteCount"]
    fresult["numcomments"]=response["items"][0]["statistics"]["commentCount"]
    yourdate = dateutil.parser.parse(response["items"][0]["snippet"]["publishedAt"])
    present_datetime = datetime.date.today()  
    date_format = "%m/%d/%Y"
    a = datetime.datetime.strftime(yourdate, date_format)
    a= datetime.datetime.strptime(a, date_format).date()
    b= datetime.datetime.strftime(present_datetime, date_format)
    b= datetime.datetime.strptime(b, date_format).date()
    delta = b - a
    fresult["age"]=delta.days
    fresult["score"]=((fresult["positivenum"]-fresult["negativenum"])*100 + int(fresult["views"])+int(fresult["numcomments"])+int(fresult["likes"])*300)/(int(fresult["age"])*10+1)
    # print(fresult)
    return fresult

def video_stat_helper(search_videoID):
    all_video_stat=[]
    for i in search_videoID:
        l=video_score(i)
        appendi=True
        for k in all_video_stat:
            if k['Channel Title']==l['Channel Title']:
                if k['score']<l['score']:
                    all_video_stat.remove(k)
                else:
                    appendi=False
        if appendi==True:
            all_video_stat.append(l)
                

    return all_video_stat


# ------------------------------------------------------------------------################################################################-----------------------#
    
x=st.text_input('Search Keyword  :','Buuble sort',key=1)
parser = argparse.ArgumentParser(description='youtube search')
parser.add_argument("--q", help="Search term",
                    default=x)
parser.add_argument("--max-results", help="Max results", default=10)
args = parser.parse_args()
search_videoID= youtube_mobie_review(args)
# print(search_videoID)
# st.write(x)
channel_ids=[]
channelID_video(youtube,search_videoID,channel_ids)
# print(channel_ids)
# --------------------------Scoring END----------------------------------------------





if st.button('Analyse Video'):
    youtube = build('youtube', 'v3', developerKey=api_key)
    def get_channel_stats(youtube, channel_ids):
        all_data = []
        request = youtube.channels().list(
                    part='snippet,contentDetails,statistics',
                    id=','.join(channel_ids))
        response = request.execute() 
        
        for i in range(len(response['items'])):
            data = dict(Channel_name = response['items'][i]['snippet']['title'],
                        Subscribers = response['items'][i]['statistics']['subscriberCount'],
                        Views = response['items'][i]['statistics']['viewCount'],
                        Total_videos = response['items'][i]['statistics']['videoCount'])
                        # playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
            all_data.append(data)
        
        return all_data


    channel_statistics = get_channel_stats(youtube, channel_ids)
    video_stat=video_stat_helper(search_videoID)

    channel_data = pd.DataFrame(channel_statistics)
    video_data = pd.DataFrame(video_stat)
    # video_data = video_data.sort_values(by = 'score',ascending=False)
    # video_data.reset_index()
    max_indi=video_data["score"].idxmax()
    st.write("**Best video about '"+x+"' is** : "+video_data.iloc[max_indi,-2])
    st.write("**Channel Name** :",video_data.iloc[max_indi,0])
    st.write("**Link of the video is** : " 'https://www.youtube.com/watch?v='+video_data.iloc[max_indi,-1])
    st.write("Statistics of All Videos")
    st.write(video_data.sort_values(by = 'score',ascending=False))
    st.write("Statistics of All Channels")
    st.write(channel_data)
    
    channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
    video_data['views'] = pd.to_numeric(video_data['views'])
    video_data['score'] = pd.to_numeric(video_data["score"])

    ax = px.line(video_data,x='Channel Title', y='score',title="Score Of All videos")
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)


    ax = px.bar(video_data,x='Channel Title', y='views',title="Comparison of Videos by Number Of Views ")
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)
   
    
    ax2 = px.pie(video_data,names='Channel Title', values='likes',title="Comparison of Videos by Number Of Likes")
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.01,1,0.01])
    # left_column.plotly_chart(ax)
    right_column.plotly_chart(ax2)
    
    ax = px.pie(video_data,names='Channel Title', values='numcomments',hole=0.5,title="Comparison of Videos by Number Of Comments")
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)

    ax = px.bar(channel_data,x='Channel_name', y='Subscribers',title="Comparison of Videos by Number Of Subscribers of Channel")
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)
    
