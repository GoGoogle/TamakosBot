from random import choice
from urllib.parse import unquote

import requests
from requests import RequestException

from entity.bot_music import Song, Album, Artist, SongList
from interface.musics.crawler import CrawlerZ
from utils.music import progress_download, userAgentList
from utils.tele import BotResult
from utils.tele import (
    SongNotAvailable, GetRequestIllegal, exception_handle)

XIAMI_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://h.xiami.com/',
    'Cookie': 'user_from=2;XMPLAYER_addSongsToggler=0;XMPLAYER_isOpen=0;_xiamitoken=cb8bfadfe130abdbf5e2282c30f0b39a;',
    'X-Real-IP': '59.111.160.197',
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
        self.session.headers.update(XIAMI_HEADERS)
        self.download_session = requests.session()

    @staticmethod
    def dump_single_song(song, mode=0):
        artist_list = [Artist(song['artist_id'], song['artist_name'])]
        album_id, album_name = song['album_id'], song['album_name']
        album = Album(album_id, album_name)
        song_id, song_name, song_duration, artists, album = song['song_id'], song[
            'song_name'], 264, artist_list, album
        song = Song(song_id, song_name, song_duration, artists, album)
        return song

    @staticmethod
    def dump_songs(songs, mode=0):
        song_list = []
        for song in songs:
            song = Crawler.dump_single_song(song, mode)
            song_list.append(song)
        return song_list

    @staticmethod
    def parse_location(location):
        rows, _str = int(location[0]), location[1:]

        out = ""
        cols = int(len(_str) / rows) + 1
        full_row = len(_str) % rows
        for c in range(cols):
            for r in range(rows):
                if c == (cols - 1) and r >= full_row:
                    continue
                if r < full_row:
                    char = _str[r * cols + c]
                else:
                    char = _str[cols * full_row + (r - full_row) * (cols - 1) + c]
                out += char
        return unquote(out).replace("^", "0")

    @exception_handle
    def get_request(self, url, params=None, custom_session=None):
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
        result = resp.json()
        return result

    def search_song(self, song_name, page=1):
        url = "http://api.xiami.com/web"
        payload = {
            'r': 'search/songs',
            'key': song_name,
            'limit': 5,
            'page': page,
            'app_key': 1,
            'v': '2.0'
        }
        result = self.get_request(url, payload)
        if result['state'] != 0:
            self.logger.warning('Song %s search failed! url=%s result=%s', song_name, url, result)
            return BotResult(400, 'Song {} search failed.'.format(song_name))
        if result['data']['total'] <= 0:
            self.logger.warning('Song %s not existed!', song_name)
            return BotResult(404, 'Song {} not existed.'.format(song_name))
        else:
            keyword, song_count, songs = song_name, result['data']['total'], result['data']['songs']
            songlist = SongList(keyword, song_count, Crawler.dump_songs(songs))
            return BotResult(200, body=songlist)

    def get_song_detail(self, song_id):
        url = 'http://api.xiami.com/web'
        payload = {
            'r': 'musics/detail',
            'id': song_id,
            'v': '2.0',
            'app_key': 1
        }
        try:
            result = self.get_request(url, payload)
            song = result['data']['musics']
            single_song = Crawler.dump_single_song(song, mode=1)
            # 获取 song_url
            url = self.get_song_url(song_id)
            single_song.song_url = url
            return BotResult(200, body=single_song)
        except (SongNotAvailable, GetRequestIllegal, RequestException) as e:
            self.logger.warning('Song %s get detail error', song_id)
            return BotResult(400, 'Return {0} when try to get {1} => {2}'.format(e, url, payload))

    def get_song_url(self, song_id):
        url = "http://www.xiami.com/musics/gethqsong"
        payload = {
            'sid': song_id
        }
        result = self.get_request(url, payload)
        if result['status'] == 1:
            song_url = self.parse_location(result['location'])
            return song_url
        else:
            self.logger.warning(
                'Song %s is not available due to copyright issue. => %s',
                song_id, result)
            raise SongNotAvailable(
                'Song {} is not available due to copyright issue.'.format(song_id))

    @exception_handle
    def write_file(self, songfile, handle=None):
        progress_download(self.download_session, songfile, handle)
