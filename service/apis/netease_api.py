import requests

from config import application

proxies = application.API_PROXY


def account_login():
    account = application.NETEASE_ACCOUNT
    if account:
        response = requests.get('http://localhost//login/cellphone', params=payload, proxies=proxies)
        return response.json()
    else:
        return {'code': 400}


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


def get_mv_detail_by_mvid(mvid):
    payload = {
        'mvid': mvid
    }
    response = requests.get('http://localhost/mv', params=payload, proxies=proxies)

    return response.json()


def get_mv_true_url_by_mv_url(mv_url):
    return '{0}/mv/url?url={1}'.format(proxies['http'], mv_url)


def get_playlist_by_playlist_id(playlist_id):
    payload = {
        'id': playlist_id
    }
    response = requests.get('http://localhost/playlist/detail', params=payload, proxies=proxies)

    return response.json()
