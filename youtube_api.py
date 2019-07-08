import feedparser
import requests
import json
import main
import re
import os

RSS_FEED = "http://www.tested.com/podcast-xml/this-is-only-a-test/"
TESTED_YOUTUBE_ID = "UCiDJtJKMICpb9B1qf7qjEOA"


def get_access_token():
    url = "https://www.googleapis.com/oauth2/v4/token"

    querystring = {"client_secret": os.environ("TESTED_YOUTUBE_CLIENT_SECRET"),
                   "grant_type": "refresh_token",
                   "refresh_token": os.environ("TESTED_YOUTUBE_REFRESH_TOKEN"),
                   "client_id": os.environ("TESTED_YOUTUBE_CLIENT_ID")}

    response = requests.request("POST", url, params=querystring)
    return json.loads(response.text)["access_token"]


def get_newest_podcast_video_id_and_name():
    url = "https://www.googleapis.com/youtube/v3/search"

    querystring = {
        "part": "snippet",
        "channelId": TESTED_YOUTUBE_ID,
        "maxResults": "25",
        "order": "date"
    }

    headers = {
        'Authorization': "Bearer " + get_access_token(),
        'Accept': "application/json",
        'Cache-Control': "no-cache",
        'Host': "www.googleapis.com",
        'accept-encoding': "gzip, deflate",
        'Connection': "keep-alive"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    videos = json.loads(response.text)

    print(videos)
    print(response.status_code)

    for video in videos['items']:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']

        if "this is only a test" in video_title.lower():
            return video_id, video_title


def have_i_already_commented(video_id):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    querystring = {
        "part": "snippet,replies",
        "videoId": video_id,
        "searchTerms": "Tested Timestamp Bot"
    }

    headers = {
        'Authorization': "Bearer " + get_access_token(),
        'Accept': "application/json",
        'Cache-Control': "no-cache",
        'Host': "www.googleapis.com",
        'accept-encoding': "gzip, deflate",
        'Connection': "keep-alive",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    my_comments = json.loads(response.text)

    return len(my_comments['items']) > 0


def comment_on_video(video_id, message):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    querystring = {"part": "snippet"}

    payload = {
        'snippet': {
            'videoId': video_id,
            'topLevelComment': {
                'snippet': {
                    'textOriginal': message
                }
            }
        }
    }

    headers = {
        'Authorization': "Bearer " + get_access_token(),
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Host': "www.googleapis.com",
        'accept-encoding': "gzip, deflate",
        'Connection': "keep-alive",
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)
    print(response.text)


def get_newest_rss_episode_number():
    feed = feedparser.parse(RSS_FEED)
    title = feed.entries[0].title

    # Find the largest digit in the title, assume that it's the episode number
    pattern = r'\d\d\d+'
    return sorted(list(map(int, re.findall(pattern, title))), reverse=True)[0]



def youtube_main(force=False):
    """
    :param force: If true post on the episode regardless of the episode number matching or if already commented
    """
    video_id, video_name = get_newest_podcast_video_id_and_name()
    print(video_id, video_name)
    already_commented = have_i_already_commented(video_id)

    if (not force) and already_commented:
        return "Already commented on video " + video_name

    newest_rss = get_newest_rss_episode_number()
    if (not force) and newest_rss not in video_name:
        return "The newest podcast in the RSS feed does not correspond to the youtube channel. " + newest_rss + " " + video_name

    segments = main.generate_timestamps()
    to_post = ""
    for segment in segments:
        to_post += main.FILE_NAMES_TO_NAME[segment[0]] + " " + main.format_seconds(segment[1])
        to_post += "\n"
    comment_on_video(video_id, to_post)
    return "Posted on " + video_name + "\n\n" + to_post


if __name__ == "__main__":
    youtube_main()
