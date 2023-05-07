import datetime
import dateutil
from apiclient.discovery import build
import unidecode
import argparse
import seaborn as sns
from googleapiclient.discovery import build
import streamlit.components as stc
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from oauth2client.tools import argparser, run_flow
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from apiclient.errors import HttpError
from apiclient.discovery import build_from_document
import base64
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pandas as pd
import os
import httplib2
import time
from PIL import Image
from streamlit_option_menu import option_menu
import streamlit as st
api_key = 'AIzaSyAZOtU_pIaHMh2aTIoND_LXcCWqlWzEKno'
# 1=sidebar menu, 2=horizontal menu, 3=horizontal menu w/ custom menu
EXAMPLE_NO = 1
timestr = time.strftime('%Y%m%d-%H%M%S')
timestr = time.strftime('%Y%m%d-%H%M%S')
timestr = time.strftime('%Y%m%d-%H%M%S')


def convert_df(df):
    return df.to_csv().encode('utf-8')


def csv_downloader(data):
    csvfile = data.to_csv()
    b64 = base64.b64encode(csvfile.encode()).decode()
    new_filename = "new_text_file_{}_.csv".format(timestr)
    st.markdown("#### Download File ###")
    href = f'<a href="data: file/csv;base64, {b64}" download="{new_filename}">Click Here!!</a>'
    st.markdown(href, unsafe_allow_html=True)


timer = 0.001
count = 0

fresult = {"positivenum": 0, "negativenum": 0, "neutralnum": 0, "linknum": 0}

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
        textFormat="plainText"
    ).execute()
    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        comments.append(text)

    if "nextPageToken" in results:
        return get_comment_threads(youtube, video_id, comments, results["nextPageToken"])
    else:
        return comments


def ValidatingVideoID(v_link):
    if ("watch?v=" in v_link):
        return v_link.split("watch?v=")[1]
    st.write("\nISSUE in Link: ", v_link, "\n")
    exit(0)


def streamlit_menu(example=3):
    selected = option_menu(
        menu_title=None,  # required
        options=["Analyze Video", "Search Topic", "About"],  # required
        icons=["search", "search", "book"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "20px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
                "color": "grey"
            },
            "nav-link-selected": {"background-color": "grey", "color": "white"},
        },
    )
    return selected


tik = 200
selected = streamlit_menu(example=EXAMPLE_NO)
st.markdown("<h1 style='text-align: center; color:;'>BOMFY</h1>",
            unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: grey;'>Bring Out Most From Youtube</h2>",
            unsafe_allow_html=True)
st.write("---")

# --------------------------#############################------------------ANALYZE VIDEOOO -------------------------------------------------------------

if selected == "Analyze Video":
    with st.container():
        # st.title('Youtube Comment Analyser','')
        col1, col2, col3 = st.columns([0.05, 1, 0.05])
    with col1:
        st.write("")
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.image("yt.png")
        st.write("")
        st.write("")
        st.write("")
    with col3:
        st.write("")
    video_link = st.text_input('Paste Link of Youtube Video here :',
                               placeholder='https://www.youtube.com/watch?v=r-GFmH0EK9Y')
# if st.button('Analyse Video'):

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    def remote_css(url):
        st.markdown(
            f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

    def icon(icon_name):
        st.markdown(
            f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

    local_css("style.css")
    remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

    # # icon("search")
    if st.button("GO"):
        # video_link = "https://www.youtube.com/watch?v=WJ-UaAaumNA"
        video_id = ValidatingVideoID(video_link)
        st.write("\nVideo ID: ", video_id)
        args = argparser.parse_args()
        args.videoid = video_id
        st.write("Processing...")
        youtube = get_authenticated_service(args)
        try:
            video_comment_threads = get_comment_threads(youtube, args.videoid)
            with open('commentscraperfile.csv', 'w', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for comment in video_comment_threads:
                    writer.writerow([comment])
                    writer.writerow("!@#$%U^&*()")

            st.write("\n")

            st.write(
                ' ********************* YOUTUBE COMMENT ANALYZER *********************')
            st.write("\n")

            st.write(
                ' ********************************************************************')
            st.write("\n\n ==> Scraping {0} comments to commentscraperfile.csv \n".format(
                len(video_comment_threads)))

        except HttpError as e:
            st.write(" ==>An HTTP error %d occurred:\n%s" %
                     (e.resp.status, e.content))
        Positive_list = []
        Negative_list = []
        Neutral_list = []
        Links_list = []
        with open("commentscraperfile.csv", "r", errors='ignore', encoding='utf-8') as csvfile:
            for line in csvfile.read().split("\n!,@,#,$,%,U,^,&,*,(,)\n"):
                vs = commentbot.polarity_scores(line)
                if (count == len(video_comment_threads)):
                    break
                count += 1
                if ("https" in line):
                    Links_list.append(line)
                    fresult["linknum"] += 1
                elif ("http" in line):
                    Links_list.append(line)
                    fresult["linknum"] += 1
                elif vs['compound'] >= 0.05:
                    Positive_list.append(line)
                    fresult["positivenum"] += 1
                elif vs['compound'] <= - 0.05:
                    Negative_list.append(line)
                    fresult["negativenum"] += 1
                else:
                    Neutral_list.append(line)
                    fresult["neutralnum"] += 1

        st.write("\n")

        st.write(
            ' ************************ GENERATING REPORT *************************')

        st.write("\n ==> READING THROUGH A TOTAL OF", count, "LINES...\n")

        time.sleep(0.001)
        st.write(" ==> AFTER ANALYZING THE SENTIMENT OF", count, "LINES..\n")

        positivenum = fresult["positivenum"]
        time.sleep(0.001)
        st.write(" ==> NUMBER OF POSITIVE COMMENTS ARE : ", positivenum, "\n")

        negativenum = fresult["negativenum"]
        time.sleep(0.001)
        st.write(" ==> NUMBER OF NEGATIVE COMMENTS ARE : ", negativenum, "\n")

        neutralnum = fresult["neutralnum"]
        time.sleep(0.001)
        st.write(" ==> NUMBER OF NEUTRAL COMMENTS ARE : ", neutralnum, "\n")
        linknum = fresult["linknum"]
        time.sleep(0.001)
        st.write(" ==> NUMBER OF COMMENTS THAT CONTAIN LINK ARE : ", linknum, "\n")

        positive_percentage = positivenum / count * 100

        negative_percentage = negativenum / count * 100

        neutral_percentage = neutralnum / count * 100

        linknum_percentage = linknum / count * 100

        size1 = positive_percentage / 100 * 360

        size2 = negative_percentage / 100 * 360

        size3 = neutral_percentage / 100 * 360

        size4 = linknum_percentage / 100 * 360
        time.sleep(0.001)
        st.write(" ==> PERCENTAGE OF COMMENTS THAT ARE POSITIVE : ",
                 positive_percentage, "%\n")
        time.sleep(0.001)
        st.write(" ==> PERCENTAGE OF COMMENTS THAT ARE NEGATIVE : ",
                 negative_percentage, "%\n")
        time.sleep(0.001)
        st.write(" ==> PERCENTAGE OF COMMENTS THAT ARE NEUTRAL  : ",
                 neutral_percentage, "%\n")
        time.sleep(0.001)
        st.write(" ==> PERCENTAGE OF COMMENTS THAT CONTAIN LINK  : ",
                 linknum_percentage, "%\n")
        time.sleep(0.001)
        st.write(" ==> CALCULATING FINAL RESULT.. :-\n")
        time.sleep(3)
        st.write(
            " ********************************************************************\n")

        labels = 'Positive', 'Negative ', 'Neutral', 'Links'

        sizes = [size1, size2, size3, size4]
        df = pd.DataFrame(sizes)
        colors = ['#E6F69D', '#AADEA7', '#64C2A6', '#2D87BB']

        explode = (0.01, 0.01, 0.01, 0.01)
        fig = px.pie(df, values=sizes, names=labels)
        # fig.show()

        left_column, middle_column, right_column = st.columns(3)
        left_column, middle_column, right_column = st.columns([0.15, 1, 0.15])
        middle_column.plotly_chart(fig, use_container_width=True)

        if positive_percentage >= (neutral_percentage + negative_percentage + 10):
            st.write(" ==> You got positive feedback.")

        elif negative_percentage >= (neutral_percentage + positive_percentage + 10):
            st.write(" ==> You got negative feedback.")

        else:
            st.write(" ==> You got neutral feedback.")

        with open('Positive_comments.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for comment in Positive_list:
                writer.writerow([comment])
        with open('Negative_comments.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for comment in Negative_list:
                writer.writerow([comment])
        with open('Neutral_comments.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for comment in Neutral_list:
                writer.writerow([comment])
        with open('Links_comments.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for comment in Links_list:
                writer.writerow([comment])
        #print("\nSegragated comment write done!")

        #st.write("\nSegragated comment write done!")

        # st.write('Positive Comments')
        data1 = pd.read_csv('Positive_comments.csv', index_col=False)
        # st.dataframe(data)
        # csv_downloader(data
        # st.write('Negative Comments')
        data2 = pd.read_csv('Negative_comments.csv')
        # st.dataframe(data)
        # st.write('Positive Comments')
        data3 = pd.read_csv('Neutral_comments.csv')
        # st.dataframe(data)
        # st.write('Positive Comments')
        data4 = pd.read_csv('Links_comments.csv')
        # st.dataframe(data)

        st.write(
            "\n ********************************************************************\n")

        # right_column.plotly_chart(fig, use_container_width=True)
        # plt.tight_layout()

        # plt.axis('equal')

        # plt.show()

    # with open('Positive_comments.csv', 'rb') as f:
    #    st.download_button('Download Zip', f, file_name='archive.')

        liste = Positive_list
        df_download = pd.DataFrame(liste)
        df_download.columns = ['Title']
        # df_download
        csv = df_download.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        linko = f'<a href="data:file/csv;base64,{b64}" download="Positive_Comments.txt">Positive Comments File</a>'
        st.markdown(linko, unsafe_allow_html=True)

        liste = Negative_list
        df_download = pd.DataFrame(liste)
        df_download.columns = ['Title']
        # df_download
        csv = df_download.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        linko = f'<a href="data:file/csv;base64,{b64}" download="Negative_Comments.txt">Negative Comments File</a>'
        st.markdown(linko, unsafe_allow_html=True)

        liste = Neutral_list
        df_download = pd.DataFrame(liste)
        df_download.columns = ['Title']
        # df_download
        csv = df_download.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        linko = f'<a href="data:file/csv;base64,{b64}" download="Neutral_Comments.txt">Neutral Comments File</a>'
        st.markdown(linko, unsafe_allow_html=True)

        liste = Links_list
        df_download = pd.DataFrame(liste)
        df_download.columns = ['Title']
        # df_download
        csv = df_download.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        linko = f'<a href="data:file/csv;base64,{b64}" download="Link_Contained_comments.txt">Link Containing Comments</a>'
        st.markdown(linko, unsafe_allow_html=True)

  # -----------------------1111111111111111---------------------

if selected == "About":
    with st.container():
        st.header("About BOMFY")
        st.write("##")
        st.write(
            """
           We propose an improved context-aware YouTube recommender system that incorporates feedback analysis in addition to factors previously considered by YouTube. Sentiment analysis of user comments is also considered in recommending videos, along with the video's Meta information. The proposed system will save a user ’ s time substantially because in contrast to the previous recommendation system the present system not only relies on the information provided by the uploader it will take into account how the audience received it and thus will show us relatively better results.
            """
        )
        st.write("---")
        st.markdown(
            "<h2 style='text-align: center; color: ;'>Our Team 🖊️</h2>", unsafe_allow_html=True)
        st.write("##")
        col1, col2, col3, col4 = st.columns(4)
        
        with col2:
            st.write("***Pratham Bansal***")
            st.write("19103083")
            st.write("CSE")
        
        with col3:
            st.write("***Aayush Varshney***")
            st.write("19103002")
            st.write("CSE")
        
# ((((((((99999999999999999999999999999999999999999999))))))))
if selected == "Search Topic":
    with st.container():
        st.write("")
        st.write("")
        st.write("")
        yt = Image.open("yt.png")
        st.image(yt)
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

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

            if len(comments) > tik:
                return comments

            if "nextPageToken" in results:
                return get_comment_threads(youtube, video_id, comments, results["nextPageToken"])
            else:
                return comments

        #-----------------------------------------------END COMMENTS --------------------------------------------------------#

        def youtube_mobie_review(options):
            # print(youtube)
            search_response = youtube.search().list(q=options.q, part="id, snippet",
                                                    maxResults=options.max_results).execute()
            video_ids = []
            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                    videoId = search_result["id"]["videoId"]
                    video_ids.append(videoId)

            # print(video_ids)
            return video_ids

        def channelID_video(youtube, video_id, channel_id):
            request = youtube.videos().list(
                part="snippet",
                id=','.join(video_id)
            )

            response = request.execute()
            for i in range(len(response['items'])):
                channel_id.append(response['items'][i]['snippet']['channelId'])

        # ---------------------------------------------------Video Score -------------------------------------------------------------------------------------#

        def video_score(video_id):
            fresult = {"Channel Title": "", "score": 0, "views": 0, "numcomments": 0, "age": 0, "likes": 0,
                       "positivenum": 0, "negativenum": 0, "neutralnum": 0, "linknum": 0, "title": "", "vID": ""}
            args = argparser.parse_args()
            args.videoid = video_id
            # print(video_id)
            # st.write("Processing...")
            youtube = get_authenticated_service(args)
            try:
                video_comment_threads = get_comment_threads(
                    youtube, args.videoid)
                with open('commentscraperfile.csv', 'w', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    for comment in video_comment_threads:
                        writer.writerow([comment])
                        writer.writerow("!@#$%U^&*()")

            except HttpError as e:
                st.write(" ==>An HTTP error %d occurred:\n%s" %
                         (e.resp.status, e.content))
            count = 0
            with open("commentscraperfile.csv", "r", errors='ignore', encoding='utf-8') as csvfile:
                for line in csvfile.read().split("\n!,@,#,$,%,U,^,&,*,(,)\n"):
                    vs = commentbot.polarity_scores(line)
                    if (count == len(video_comment_threads)):
                        break
                    count += 1
                    if ("https" in line):
                        fresult["linknum"] += 1
                    elif ("http" in line):
                        fresult["linknum"] += 1
                    elif vs['compound'] >= 0.05:
                        fresult["positivenum"] += 1
                    elif vs['compound'] <= - 0.05:
                        fresult["negativenum"] += 1
                    else:
                        fresult["neutralnum"] += 1

            request = youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            response = request.execute()
            fresult["views"] = response["items"][0]["statistics"]["viewCount"]
            fresult["likes"] = response["items"][0]["statistics"]["likeCount"]
            fresult["Channel Title"] = response["items"][0]["snippet"]["channelTitle"]
            fresult["title"] = response["items"][0]["snippet"]["title"]
            fresult["vID"] = 'https://www.youtube.com/watch?v='+video_id
            # fresult["fav"]=response["items"][0]["statistics"]["favoriteCount"]
            fresult["numcomments"] = response["items"][0]["statistics"]["commentCount"]
            yourdate = dateutil.parser.parse(
                response["items"][0]["snippet"]["publishedAt"])
            present_datetime = datetime.date.today()
            date_format = "%m/%d/%Y"
            a = datetime.datetime.strftime(yourdate, date_format)
            a = datetime.datetime.strptime(a, date_format).date()
            b = datetime.datetime.strftime(present_datetime, date_format)
            b = datetime.datetime.strptime(b, date_format).date()
            delta = b - a
            fresult["age"] = delta.days
            fresult["score"] = ((fresult["positivenum"]-fresult["negativenum"])*100 + int(fresult["views"])+int(
                fresult["numcomments"])+int(fresult["likes"])*300)/(int(fresult["age"])*10+1)
            # print(fresult)
            return fresult

        def video_stat_helper(search_videoID):
            all_video_stat = []
            for i in search_videoID:
                l = video_score(i)
                appendi = True
                for k in all_video_stat:
                    if k['Channel Title'] == l['Channel Title']:
                        if k['score'] < l['score']:
                            all_video_stat.remove(k)
                        else:
                            appendi = False
                if appendi == True:
                    all_video_stat.append(l)

            return all_video_stat

        def local_css(file_name):
            with open(file_name) as f:
                st.markdown(f'<style>{f.read()}</style>',
                            unsafe_allow_html=True)

        def remote_css(url):
            st.markdown(
                f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

        def icon(icon_name):
            st.markdown(
                f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

        local_css("style.css")
        remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

        # icon("search")
        x = st.text_input("", placeholder="Search Topic...")
        parser = argparse.ArgumentParser(description='youtube search')
        parser.add_argument("--q", help="Search term",
                            default=x)
        parser.add_argument("--max-results", help="Max results", default=10)
        args = parser.parse_args()
        button_clicked = st.button("GO")

        if button_clicked:
            search_videoID = youtube_mobie_review(args)
        # print(search_videoID)
        # st.write(x)
            channel_ids = []
            channelID_video(youtube, search_videoID, channel_ids)
            youtube = build('youtube', 'v3', developerKey=api_key)

            def get_channel_stats(youtube, channel_ids):
                all_data = []
                request = youtube.channels().list(
                    part='snippet,contentDetails,statistics',
                    id=','.join(channel_ids))
                response = request.execute()

                for i in range(len(response['items'])):
                    data = dict(Channel_name=response['items'][i]['snippet']['title'],
                                Subscribers=response['items'][i]['statistics']['subscriberCount'],
                                Views=response['items'][i]['statistics']['viewCount'],
                                Total_videos=response['items'][i]['statistics']['videoCount'])
                    # playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
                    all_data.append(data)

                return all_data

            channel_statistics = get_channel_stats(youtube, channel_ids)
            video_stat = video_stat_helper(search_videoID)

            channel_data = pd.DataFrame(channel_statistics)
            video_data = pd.DataFrame(video_stat)
            # video_data = video_data.sort_values(by = 'score',ascending=False)
            # video_data.reset_index()
            max_indi = video_data["score"].idxmax()
            st.write("**Best video about '"+x+"' is** : " +
                     video_data.iloc[max_indi, -2])
            st.write("**Channel Name** :", video_data.iloc[max_indi, 0])
            st.write("**Link of the video is** : ",
                     video_data.iloc[max_indi, -1])
            st.write("Statistics of All Videos")
            st.write(video_data.sort_values(
                by='score', ascending=False, ignore_index=True))
            st.write("Statistics of All Channels")
            st.write(channel_data)

            channel_data['Subscribers'] = pd.to_numeric(
                channel_data['Subscribers'])
            video_data['views'] = pd.to_numeric(video_data['views'])
            video_data['score'] = pd.to_numeric(video_data["score"])

            ax = px.line(video_data, x='Channel Title',
                         y='score', title="Score Of All videos")
            left_column, middle_column, right_column = st.columns(3)
            left_column, middle_column, right_column = st.columns([
                                                                  0.1, 1, 0.1])
            middle_column.plotly_chart(ax, use_container_width=True)

            ax = px.bar(video_data, x='Channel Title', y='views',
                        title="Comparison of Videos by Number Of Views ")
            left_column, middle_column, right_column = st.columns(3)
            left_column, middle_column, right_column = st.columns([
                                                                  0.1, 1, 0.1])
            middle_column.plotly_chart(ax, use_container_width=True)

            ax2 = px.pie(video_data, names='Channel Title', values='likes',
                         title="Comparison of Videos by Number Of Likes")
            left_column, middle_column, right_column = st.columns(3)
            left_column, middle_column, right_column = st.columns(
                [0.01, 1, 0.01])
            # left_column.plotly_chart(ax)
            right_column.plotly_chart(ax2)

            ax = px.pie(video_data, names='Channel Title', values='numcomments',
                        hole=0.5, title="Comparison of Videos by Number Of Comments")
            left_column, middle_column, right_column = st.columns(3)
            left_column, middle_column, right_column = st.columns([
                                                                  0.1, 1, 0.1])
            middle_column.plotly_chart(ax, use_container_width=True)

            ax = px.bar(channel_data, x='Channel_name', y='Subscribers',
                        title="Comparison of Videos by Number Of Subscribers of Channel")
            left_column, middle_column, right_column = st.columns(3)
            left_column, middle_column, right_column = st.columns([
                                                                  0.1, 1, 0.1])
            middle_column.plotly_chart(ax, use_container_width=True)
