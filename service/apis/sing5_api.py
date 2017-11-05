# https://github.com/i5sing/5sing-mobile-api

import requests

# proxies = application.API_PROXY
proxies = {}


def search_musics_by_keyword_pagecode_and_filter(kw, pagecode=1, filter_type=2):
    payload = {
        'k': kw,
        't': 0,
        'filterType': filter_type,
        'ps': 5,
        'pn': pagecode
    }
    response = requests.get('http://goapi.5sing.kugou.com/search/search', params=payload, proxies=proxies)

    return response.json()


def get_music_url_by_id_and_type(music_id, song_type='fc'):
    payload = {
        'songid': music_id,
        'songtype': song_type
    }
    response = requests.get('http://mobileapi.5sing.kugou.com/song/getSongUrl', params=payload, proxies=proxies)

    return response.json()


def get_music_detail_by_id_and_type(music_id, song_type='fc'):
    payload = {
        'songid': music_id,
        'songtype': song_type
    }
    response = requests.get('http://mobileapi.5sing.kugou.com/song/newget', params=payload, proxies=proxies)

    return response.json()
