import logging

import requests

from config import application

logger = logging.getLogger(__name__)

proxies = application.API_PROXY

s = requests.session()


def init_login():
    payload = application.LOGIN_PAYLOAD
    res = s.get('http://localhost/login/cellphone', params=payload, proxies=proxies)
    content = res.json()
    if content['code'] == 200:
        logger.info('{} 登录成功！'.format(content['account']['userName']))


def search_musics_by_keyword_and_pagecode(kw, pagecode=1):
    payload = {
        'keywords': kw,
        'limit': 5,
        'offset': (pagecode - 1) * 5
    }
    response = s.get('http://localhost/search', params=payload, proxies=proxies)

    return response.json()


def get_music_url_by_musicid(music_id):
    payload = {
        'id': music_id
    }
    response = s.get('http://localhost/music/url', params=payload, proxies=proxies)

    return response.json()


def get_music_detail_by_musicid(music_id):
    payload = {
        'ids': music_id
    }
    response = s.get('http://localhost/song/detail', params=payload, proxies=proxies)

    return response.json()


def get_mv_detail_by_mvid(mvid):
    payload = {
        'mvid': mvid
    }
    response = s.get('http://localhost/mv', params=payload, proxies=proxies)

    return response.json()


def get_mv_true_url_by_mv_url(mv_url):
    return '{0}/mv/url?url={1}'.format(proxies['http'], mv_url)


def get_playlist_by_playlist_id(playlist_id):
    payload = {
        'id': playlist_id
    }
    response = s.get('http://localhost/playlist/detail', params=payload, proxies=proxies)

    return response.json()
