import requests

proxies = {
    "http": "http://127.0.0.1:3000",
}


def search_musics_by_keyword_and_pagecode(kw, pagecode=1):
    payload = {
        'keywords': kw,
        'limit': 5,
        'offset': (pagecode - 1) * 5
    }
    response = requests.get('http://localhost/search', params=payload, proxies=proxies)

    return response.json()


def get_music_url_by_musicid(music_id):
    payload = {
        'id': music_id
    }
    response = requests.get('http://localhost/music/url', params=payload, proxies=proxies)

    return response.json()


def get_music_detail_by_musicid(music_id):
    payload = {
        'ids': music_id
    }
    response = requests.get('http://localhost/song/detail', params=payload, proxies=proxies)

    return response.json()
