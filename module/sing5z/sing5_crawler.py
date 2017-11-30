# https://github.com/i5sing/5sing-mobile-api
import logging

import requests


class Crawler(object):
    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Crawler, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120, proxy=None):
        self.session = requests.Session()
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}
        self.logger = logging.getLogger(__name__)


def search_musics_by_keyword_pagecode_and_filter(kw, pagecode=1, filter_type=2):
    payload = {
        'k': kw,
        't': 0,
        'filterType': filter_type,
        'ps': 5,
        'pn': pagecode
    }
    response = requests.get('http://goapi.5sing.kugou.com/search/search', params=payload)

    return response.json()


def get_music_url_by_id_and_type(music_id, song_type='yc'):
    payload = {
        'songid': music_id,
        'songtype': song_type
    }
    response = requests.get('http://mobileapi.5sing.kugou.com/song/getSongUrl', params=payload)

    return response.json()


def get_music_detail_by_id_and_type(music_id, song_type='yc'):
    payload = {
        'songid': music_id,
        'songtype': song_type
    }
    response = requests.get('http://mobileapi.5sing.kugou.com/song/newget', params=payload)

    return response.json()


def get_music_top_date():
    response = requests.get('http://mobileapi.5sing.kugou.com/song/listsupportcardcycle')

    return response.json()


def get_music_top_by_type_pagecode_and_date(mtype='yc', pagecode=1, date=0):
    payload = {
        'id': mtype,
        'pageindex': pagecode,
        'pagesize': 5,
        'time': date
    }
    response = requests.get('http://mobileapi.5sing.kugou.com/rank/detail', params=payload)

    return response.json()
