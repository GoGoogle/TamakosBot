import time

import requests
from requests import RequestException

from config.application import CHUNK_SIZE, KUGOU_HEADERS
from entity.bot_music import Song, Album, Artist, SongList
from interface.crawler import CrawlerZ
from util.telegram_util import BotResult
from util.encrypt_util import md5_encrypt
from util.excep_util import (
    SongNotAvailable, GetRequestIllegal, exception_handle)


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