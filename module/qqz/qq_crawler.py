import json
import math
import re
import time
from random import choice, random as rand

import requests
from requests import RequestException

from config.application import CHUNK_SIZE
from entity.bot_music import Song, Album, Artist, SongList
from interface.crawler import CrawlerZ
from util.encrypt_util import userAgentList
from util.excep_util import (
    SongNotAvailable, GetRequestIllegal, exception_handle)
from util.telegram_util import BotResult

QQ_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://y.qq.com/portal/search.html',
    'Host': 'c.y.qq.com',
    'X-Real-IP': '117.185.116.152',
    'User-Agent': choice(userAgentList)
}


class Crawler(CrawlerZ):
    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CrawlerZ, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120, proxy=None):
        super().__init__(timeout, proxy)
        self.session = requests.session()
        self.session.headers.update(QQ_HEADERS)
        self.download_session = requests.session()

    @staticmethod
    def dump_single_song(song, mode=0):
        artist_list = []
        for ar in song['singer']:
            artist_id, artist_name = ar['mid'], ar['name']
            artist_list.append(Artist(artist_id, artist_name))

        album_id, album_name = song['album']['mid'], song['album']['name']
        album = Album(album_id, album_name)

        song_id, song_name, song_duration, artists, album = \
            song['mid'], song['name'], song['interval'], artist_list, album
        song = Song(song_id, song_name, song_duration, artists, album)
        return song

    @staticmethod
    def dump_songs(songs, mode=0):
        song_list = []
        for song in songs:
            song = Crawler.dump_single_song(song, mode)
            song_list.append(song)
        return song_list

    @exception_handle
    def get_request(self, url, params=None, custom_session=None, callback=None):
        """Send a get request.

        warning: old api.
        :return: a dict or raise Exception.
        """
        if not custom_session:
            resp = self.session.get(url, params=params, timeout=self.timeout,
                                    proxies=self.proxies)
        else:
            resp = custom_session.get(url, params=params, timeout=self.timeout,
                                      proxies=self.proxies)
        if callback:
            regex_str = r'{}\((.+)\)'.format(callback)
            data = re.match(regex_str, resp.text).group(1)
            return json.loads(data)
        else:
            result = resp.json()
            return result

    def parse_guid(self, guid):
        """
        解析 url的关键参数
        :return: {'code':0, 'sip': [], ... , 'key': ''}
        """
        url = "https://c.y.qq.com/base/fcgi-bin/fcg_musicexpress.fcg"
        payload = {
            'guid': guid,
            'json': 3,
            'format': 'json'
        }
        result = self.get_request(url, payload)
        return result

    def search_song(self, song_name, page=1):
        url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
        payload = {
            'w': song_name,
            'n': 5,
            'p': page,
            'aggr': 1,
            'lossless': 1,
            'cr': '1',
            'jsonpCallback': 'callback',
            'new_json': 1,
            'format': 'json'
        }
        result = self.get_request(url, payload)
        if result['code'] != 0:
            self.logger.warning('Song %s search failed! url=%s result=%s', song_name, url, result)
            return BotResult(400, 'Song {} search failed.'.format(song_name))
        if result['data']['song']['totalnum'] <= 0:
            self.logger.warning('Song %s not existed!', song_name)
            return BotResult(404, 'Song {} not existed.'.format(song_name))
        else:
            keyword, song_count, songs = song_name, result['data']['song']['totalnum'], result['data']['song']['list']
            songlist = SongList(keyword, song_count, Crawler.dump_songs(songs))
            return BotResult(200, body=songlist)

    def get_song_detail(self, song_id):
        url = 'http://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg'
        payload = {
            'songmid': song_id,
            'format': 'json'
        }
        try:
            result = self.get_request(url, payload)
            song = result['data'][0]
            single_song = Crawler.dump_single_song(song)
            file = result['data'][0]['file']
            if file['size_320mp3']:
                type_o = ('M800', 'mp3')
            elif file['size_128mp3']:
                type_o = ('M500', 'mp3')
            elif file['size_96aac']:
                type_o = ('C400', 'm4a')
            else:
                type_o = ('C200', 'm4a')
            url = self.get_song_url(song_id, type_o)
            single_song.song_url = url
            return BotResult(200, body=single_song)
        except (SongNotAvailable, GetRequestIllegal, RequestException) as e:
            self.logger.warning('Song %s get detail error', song_id)
            return BotResult(400, 'Return {0} when try to get {1} => {2}'.format(e, url, payload))

    def get_song_url(self, song_id, type_o=None):
        guid = math.floor(rand() * 1000000000)
        secret_token = self.parse_guid(guid)
        base, prefix, extension, vkey, guid, fromtag = \
            secret_token['sip'][0], type_o[0], type_o[1], secret_token['key'], guid, 30
        song_url = "{0}{1}{2}.{3}?vkey={4}&guid={5}&fromtag={6}".format(
            base, prefix, song_id, extension, vkey, guid, fromtag)
        return song_url

    @exception_handle
    def write_file(self, songfile, handle=None):
        resp = self.download_session.get(songfile.file_url, stream=True, timeout=self.timeout)
        length = int(resp.headers.get('content-length'))
        dl = 0
        for chunk in resp.iter_content(CHUNK_SIZE):
            dl += len(chunk)
            songfile.file_stream.write(chunk)

            middle_num, full_status, empty_remaining = int(10 * dl / length), "»»»»»»»»»»", "          "
            dl_status = full_status[:middle_num] + empty_remaining[middle_num:]
            progress = '[ {0} ] {1:.0f}% {2:.2f}M'.format(dl_status, dl / length * 100, length / (1024 * 1024))
            if handle:
                handle.update(progress)

    def login(self, username, password):
        pass
