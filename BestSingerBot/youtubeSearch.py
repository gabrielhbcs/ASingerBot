#!/usr/bin/python
from apiclient.discovery import build

DEVELOPER_KEY = "AIzaSyCVCnljWrvzc-O4rbcp9KaIaobLhmRvPck"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

def youtube_search(query, max):
    search_response = youtube.search().list(
    q=query,
    part="id,snippet",
    maxResults=max
    ).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                     search_result["id"]["videoId"]))

    print ("Videos:\n", "\n".join(videos), "\n")


if __name__ == "__main__":
    try:
        youtube_search("michael douglas", 5)
        youtube_search("fon", 5)
    except :
        print ("deu ruim")
