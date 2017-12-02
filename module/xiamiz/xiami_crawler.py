import time
from random import choice
from urllib.parse import unquote

import requests
from requests import RequestException

from config.application import CHUNK_SIZE
from entity.bot_music import Song, Album, Artist, SongList
from interface.crawler import CrawlerZ
from util.encrypt_util import userAgentList
from util.excep_util import (
    SongNotAvailable, GetRequestIllegal, exception_handle)
from util.telegram_util import BotResult

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
            'r': 'song/detail',
            'id': song_id,
            'v': '2.0',
            'app_key': 1
        }
        try:
            result = self.get_request(url, payload)
            song = result['data']['song']
            single_song = Crawler.dump_single_song(song, mode=1)
            # 获取 song_url
            url = self.get_song_url(song_id)
            single_song.song_url = url
            return BotResult(200, body=single_song)
        except (SongNotAvailable, GetRequestIllegal, RequestException) as e:
            self.logger.warning('Song %s get detail error', song_id)
            return BotResult(400, 'Return {0} when try to get {1} => {2}'.format(e, url, payload))

    def get_song_url(self, song_id):
        url = "http://www.xiami.com/song/gethqsong"
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
        resp = self.download_session.get(songfile.file_url, stream=True, timeout=self.timeout)
        start = time.time()
        length = int(resp.headers.get('content-length'))
        dl = 0
        for chunk in resp.iter_content(CHUNK_SIZE):
            dl += len(chunk)
            songfile.file_stream.write(chunk)
            network_speed = dl / (time.time() - start)
            if network_speed > 1024 * 1024:
                network_speed_status = '{:.2f} MB/s'.format(network_speed / (1024 * 1024))
            else:
                network_speed_status = '{:.2f} KB/s'.format(network_speed / 1024)
            if dl > 1024 * 1024:
                dl_status = '{:.2f} MB'.format(dl / (1024 * 1024))
            else:
                dl_status = '{:.0f} KB'.format(dl / 1024)
            # 已下载大小，总大小，已下载的百分比，网速
            progress = '{0} / {1:.2f} MB ({2:.0f}%) - {3}'.format(dl_status, length / (1024 * 1024), dl / length * 100,
                                                                  network_speed_status)
            if handle:
                handle.update(progress)

    def login(self, username, password):
        pass
