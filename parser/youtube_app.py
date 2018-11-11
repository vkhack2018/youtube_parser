import requests
import re
import random
from dao.dao import create_blogger, create_content, create_link, create_batch_click


def get_video_info(video_id):
    res = requests.get('https://www.googleapis.com/youtube/v3/videos'
                       '?part=statistics'
                       '&key=AIzaSyA8mrDRRbES86ExgwSobAZNEW0teFF5Qs4'
                       '&id=' + video_id)

    res = res.json()['items'][0]['statistics']

    return res["viewCount"], res['likeCount'], res['dislikeCount']


def get_videos(channel_id):
    nextTokenPage = ""
    videos = []

    while True:
        print("kek")
        res = requests.get('https://www.googleapis.com/youtube/v3/search?key=AIzaSyD9PglCo-Wtg70TB_'
                           'wmBNGlzdvj0nMqkhI&channelId=' + channel_id +
                           '&part=snippet,id'
                           '&order=date'
                           '&maxResults=50'
                           '&pageToken=' + nextTokenPage)

        for item in res.json()["items"]:
            if item["id"]['kind'] == "youtube#video":
                desc = requests.get('https://www.googleapis.com/youtube/v3/videos?'
                                    'key=AIzaSyA8mrDRRbES86ExgwSobAZNEW0teFF5Qs4'
                                    '&part=snippet'
                                    '%2CcontentDetails'
                                    '%2Cstatistics '
                                    '&id=' + item["id"]["videoId"]).json()["items"][0]["snippet"]["description"]

                video = {"id": item["id"]["videoId"],
                         "title": item["snippet"]['title'],
                         "description": desc,
                         "img": item["snippet"]["thumbnails"]["high"]["url"]
                         }

                videos.append(video)

        if "nextPageToken" in res.json():
            nextTokenPage = res.json()["nextPageToken"]
            print(nextTokenPage)
        else:
            break
    return videos


def get_author(channel_id):
    res = requests.get('https://www.googleapis.com/youtube/v3/channels'
                       '?key=AIzaSyD9PglCo-Wtg70TB_wmBNGlzdvj0nMqkhI'
                       '&part=snippet,statistics'
                       '&id=' + channel_id)

    return {"name": res.json()['items'][0]['snippet']['title'],
            "image": res.json()['items'][0]['snippet']["thumbnails"]["high"]["url"],
            "n_sub": res.json()["items"][0]["statistics"]["subscriberCount"]
            }


def find_googl_links(description=""):
    links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', description)
    return list(filter(lambda x: "goo.gl" in x, links))


def find_original_link(short_url):
    resp = requests.get(short_url, allow_redirects=False)
    return resp.headers["Location"]


def push_link_click(link_id, all_time_stat):
    buckets = all_time_stat["buckets"]
    end_time = all_time_stat["end_time"]
    bucket_size = all_time_stat["bucket_size"]
    for i in range(len(buckets)):
        start_time = end_time + bucket_size * (i - len(buckets))
        clicks = []
        if buckets[i] == 0: continue
        for t in range(buckets[i]):
            clicks.append({"link_id": link_id, "time": start_time + random.randint(0, bucket_size)})
        create_batch_click(clicks)


# TODO it can return all stats about link not only clicks
def find_link_stat(googl_url):
    url = 'https://goo.gl/api/analytics?security_token=pFz5cAU5jVcJqKbxBxbjsO3Fw6Q:1541845905725&' \
          'url=' + googl_url
    resp = requests.post(url).json()
    return resp['details']['all time']['clicks']


channel_ids = ["UC29J5CXmsnqX7JPAzlU9yCQ", "UCrRvbjv5hR1YrRoqIRjH3QA"] # ]

for channel in channel_ids:

    author = get_author(channel)
    blogger_id = create_blogger(author["name"],
                                author["image"],
                                author["n_sub"],
                                'https://www.youtube.com/channel/' + channel)
    nextTokenPage = ""

    videos = get_videos(channel)
    print("Collected videos from channel=" + str(videos.__len__()))
    for video in videos:

        googl_urls = find_googl_links(video['description'])
        if googl_urls.__len__() == 0: continue
        url = "https://www.youtube.com/watch?v=" + video['id']
        views, likes, dislikes = get_video_info(video['id'])
        content_id = create_content(video["title"],
                                    video["img"],
                                    "video",
                                    url, blogger_id, views, likes, dislikes)

        for url in googl_urls:
            original_url = find_original_link(url)
            stat = find_link_stat(url)
            link_id = create_link("from youtube parser",
                                  content_id,
                                  blogger_id,
                                  original_url, url, stat["short_url"])

            # push_link_click(link_id, stat)
