from apiclient.discovery import build
import argparse
import unidecode
import pandas as pd
DEVELOPER_KEY = "AIzaSyBfwQfMcFWVFIztDAr6qpAJ8KmImWFyJPw"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
titles = []
PublishTime = []
videoIds = []
channelTitles = []
video_descriptions = []
viewCounts = []
likeCounts = []
dislikeCounts = []
commentCounts = []
favoriteCounts = []
URLS = []
Audience_Response = []


def youtube_mobie_review(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    print(youtube)  
    search_response = youtube.search().list(q=options.q, part="id, snippet",
                                            maxResults=options.max_results).execute()
    video_ids=[]
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videoId = search_result["id"]["videoId"]
            video_ids.append(videoId)

    print(video_ids)
    return 


print("Enter the Movie Name : ")
x = str(input())
parser = argparse.ArgumentParser(description='youtube search')
parser.add_argument("--q", help="Search term",
                    default=x)
parser.add_argument("--max-results", help="Max results", default=10)
args = parser.parse_args()
search_videoID= youtube_mobie_review(args)
