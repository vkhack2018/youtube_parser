import requests
import json

base_url = "http://172.20.39.62:8080"
import logging

# add filemode="w" to overwrite
logging.basicConfig(filename="sample.log", level=logging.INFO)


def create_blogger(name, img, n_subs, channel_link):
    res = requests.post(base_url + '/blogger', json={"name": name,
                                                     "channel_pic_url": img,
                                                     "subscribers": n_subs,
                                                     "channel_link": channel_link})
    return res.json()['id']


def create_content(text, picUrl, content_type, url, blogger_id, views, likes, dislikes):
    res = requests.post(base_url + '/content', json={'name': text,
                                                     'picurl': picUrl,
                                                     'type': content_type,
                                                     'url': url,
                                                     'blogger_id': blogger_id,
                                                     'views': views,
                                                     'likes': likes,
                                                     'dislikes': dislikes
                                                     })

    logging.info({'type': content_type,
                  'url': url,
                  "pickUrl": picUrl,
                  'blogger_id': blogger_id,
                  'views': views,
                  'likes': likes,
                  'dislikes': dislikes
                  }.__str__())

    return res.json()['id']


def create_link(description, content_id, blogger_id, long, short, clicks):
    res = requests.post(base_url + '/links', json={"description": description,
                                                   "content_id": content_id,
                                                   "blogger_id": blogger_id,
                                                   "long": long,
                                                   "short": short,
                                                   "clicks": clicks
                                                   }
                        )

    logging.info({"description": description,
                  "content_id": content_id,
                  "blogger_id": blogger_id,
                  "long": long,
                  "short": short,
                  "clicks": clicks
                  }.__str__())
    temp = 0
    try:
        temp = res.json()['id']
    except Exception:
        print(short)
        print(long)

    return temp


def create_click(link_id, time):
    resp = requests.post(base_url + '/click', json={"link_id": link_id,
                                                    "time": time
                                                    }
                         )
    return resp.json()["id"]


def create_batch_click(clicks):
    resp = requests.post(base_url + '/click/batch', json=clicks)
