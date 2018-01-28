from random import choice

import requests
from requests import RequestException

from entity.bot_music import Song, Album, Artist, SongList
from interface.song.crawler import CrawlerZ
from utils.song import md5_encrypt, userAgentList
from utils.telegram import (
    SongNotAvailable, GetRequestIllegal, exception_handle)
from utils.song import progress_download
from utils.telegram import BotResult

KUGOU_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://www.kugou.com/',
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
        self.session.headers.update(KUGOU_HEADERS)
        self.download_session = requests.session()

    @staticmethod
    def dump_single_song(song, mode=0):
        if mode == 0:
            artist_list = [Artist(10010, song['singername'])]
            album_id, album_name = song['album_id'], song['album_name']
            album = Album(album_id, album_name)
            song_id = song.get('sqhash') or song.get('320hash') or song.get('128hash') or song.get('hash')
            song_id, song_name, song_duration, artists, album = song_id, song['songname'], song[
                'duration'], artist_list, album
            song = Song(song_id, song_name, song_duration, artists, album)
        if mode == 1:
            artist_list = []
            for ar in song['authors']:
                artist_id, artist_name = ar['author_id'], ar['author_name']
                artist_list.append(Artist(artist_id, artist_name))

            album_id, album_name = song['album_id'], song['album_name']
            album = Album(album_id, album_name)
            song_id = song['hash']
            song_id, song_name, song_duration, artists, album = song_id, song['song_name'], song[
                'timelength'], artist_list, album
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
        if result.get('err_code') or result.get('errcode') or result.get('error'):
            self.logger.error('Return %s when try to get %s', result, url)
            raise GetRequestIllegal(result)
        else:
            return result

    def post_request(self, url, params, custom_session=None):
        pass

    def search_song(self, song_name, page=1):
        url = "http://mobilecdn.kugou.com/api/v3/search/song"
        payload = {
            'keyword': song_name,
            'page': page,
            'pagesize': 5,
            'format': 'json',
            'showtype': 1
        }
        try:
            result = self.get_request(url, payload)
            if result['data']['total'] <= 0:
                self.logger.warning('Song %s not existed!', song_name)
                return BotResult(404, 'Song {} not existed.'.format(song_name))
            else:
                keyword, song_count, songs = song_name, result['data']['total'], result['data']['info']
                songlist = SongList(keyword, song_count, Crawler.dump_songs(songs))
                return BotResult(200, body=songlist)
        except (GetRequestIllegal, RequestException) as e:
            self.logger.warning('Song %s search error', song_name)
            return BotResult(400, 'Return {0} when try to get {1} => {2}'.format(e, url, payload))

    def get_playlist(self, playlist_id, page=1):
        pass

    def get_song_detail(self, song_id):
        url = 'http://www.kugou.com/yy/index.php'
        payload = {
            'r': 'play/getdata',
            'hash': song_id
        }
        try:
            result = self.get_request(url, payload)
            song = result['data']
            single_song = Crawler.dump_single_song(song, mode=1)
            # 获取 song_url
            url = self.get_song_url(song_id)
            single_song.song_url = url
            return BotResult(200, body=single_song)
        except (SongNotAvailable, GetRequestIllegal, RequestException) as e:
            self.logger.warning('Song %s get detail error', song_id)
            return BotResult(400, 'Return {0} when try to get {1} => {2}'.format(e, url, payload))

    def get_song_url(self, song_id):
        url = "http://trackercdn.kugou.com/i/"
        payload = {
            'acceptMp3': 1,
            'cmd': 4,
            'pid': 6,
            'hash': song_id,
            'key': md5_encrypt(song_id + 'kgcloud')
        }
        result = self.get_request(url, payload)
        if result.get('error'):
            self.logger.warning(
                'Song %s is not available due to copyright issue. => %s',
                song_id, result)
            raise SongNotAvailable(
                'Song {} is not available due to copyright issue.'.format(song_id))
        else:
            return result['url']

    def get_songtop(self, search_type, page=1):
        pass

    @exception_handle
    def write_file(self, songfile, handle=None):
        progress_download(self.download_session, songfile, handle)

    def login(self, username, password):
        pass
