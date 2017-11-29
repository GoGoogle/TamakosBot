import logging

import requests

logger = logging.getLogger(__name__)

s = requests.session()


def init_login():
    pass


def search_music_by_keyword_and_pagecode(kw, pagecode=1):
    payload = {
        'keyword': kw,
        'page': pagecode,
        'pagesize': 5,
        'format': 'json',
        'showtype': 1
    }
    response = s.get('http://mobilecdn.kugou.com/api/v3/search/song', params=payload)
    return response.json()


def get_music_detail_by_musicid(music_id):
    payload = {
        'cmd': 'playInfo',
        'hash': music_id
    }
    response = s.get('http://m.kugou.com/app/i/getSongInfo.php', params=payload)
    return response.json()


def get_hqmusic_detail_by_musicid(music_id):
    payload = {
        'r': 'play/getdata',
        'hash': music_id
    }
    response = s.get('http://m.kugou.com/app/i/getSongInfo.php', params=payload)
    return response.json()
