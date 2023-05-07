from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
api_key = 'AIzaSyBfwQfMcFWVFIztDAr6qpAJ8KmImWFyJPw'
#channel_id = 'UCnz-ZXXER4jOvuED5trXfEA'

ch1=st.text_input('Paste Channel ID 1  :','UCnz-ZXXER4jOvuED5trXfEA',key=1)
ch2=st.text_input('Paste Channel ID 2  :','UCLLw7jmFsvfIVaUFsLs8mlQ',key=2)
ch3=st.text_input('Paste Channel ID 2  :','UCiT9RITQ9PW6BhXK0y2jaeg',key=3)
ch4=st.text_input('Paste Channel ID 2  :','UC7cs8q-gJRlGwj4A8OmCmXg',key=4)
ch5=st.text_input('Paste Channel ID 2  :','UC2UXDak6o7rBm23k3Vv5dww',key=5)
''.join(ch1)
''.join(ch2)
''.join(ch3)
''.join(ch4)
''.join(ch5)
channel_ids=[ch1,ch2,ch3,ch4,ch5]
st.write(channel_ids)
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
                        Total_videos = response['items'][i]['statistics']['videoCount'],
                        playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
            all_data.append(data)
        
        return all_data


    channel_statistics = get_channel_stats(youtube, channel_ids)

    channel_data = pd.DataFrame(channel_statistics)

    st.write(channel_data)

    channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
    channel_data['Views'] = pd.to_numeric(channel_data['Views'])
    channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])

    ax = px.bar(channel_data,x='Channel_name', y='Subscribers')
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)


    ax = px.bar(channel_data,x='Channel_name', y='Views')
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)


    ax = px.bar(channel_data,x='Channel_name', y='Total_videos')
    left_column,middle_column, right_column = st.columns(3)
    left_column,middle_column,right_column = st.columns([0.1,1, 0.1])
    middle_column.plotly_chart(ax, use_container_width=True)