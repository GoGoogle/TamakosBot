import hashlib
import json
import re
import time
from http import cookiejar

import requests
from requests import RequestException

from config.application import HEADERS, COOKIE_PATH, CHUNK_SIZE
from entity.bot_music import Song, Album, Artist, Playlist, User, SongList
from interface.crawler import CrawlerZ
from util.bot_result import BotResult
from util.encrypt import encrypted_request
from util.exception import (
    SongNotAvailable, GetRequestIllegal, PostRequestIllegal, exception_handle)


class Crawler(CrawlerZ):
    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Crawler, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120, proxy=None):
        super().__init__(timeout, proxy)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.cookies = cookiejar.LWPCookieJar(COOKIE_PATH)
        self.login_session = requests.Session()
        # self.download_session = requests.Session()

    @staticmethod
    def dump_single_song(song):
        artist_list = []
        for ar in song['ar']:
            artist_id, artist_name = ar['id'], ar['name']
            artist_list.append(Artist(artist_id, artist_name))

        album_id, album_name, album_pic_id = song['al']['id'], song['al']['name'], song['al'][
            'pic']

        album = Album(album_id, album_name, album_pic_id)
        song_id, song_name, song_duration, artists, album = song['id'], song['name'], song['dt'], artist_list, album
        song = Song(song_id, song_name, song_duration, artists, album)
        return song

    @staticmethod
    def dump_songs(songs):
        song_list = []
        for song in songs:
            song = Crawler.dump_single_song(song)
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
        if result['code'] != 200:
            self.logger.error('Return %s when try to get %s', result, url)
            raise GetRequestIllegal(result)
        else:
            return result

    @exception_handle
    def post_request(self, url, params, custom_session=None):
        """Send a post request.

        :return: a dict or raise Exception.
        """

        data = encrypted_request(params)
        if not custom_session:
            resp = self.session.post(url, data=data, timeout=self.timeout,
                                     proxies=self.proxies)
        else:
            resp = custom_session.post(url, data=data, timeout=self.timeout,
                                       proxies=self.proxies)
        result = resp.json()
        if result['code'] != 200:
            self.logger.error('Return %s when try to post %s => %s',
                              result, url, params)
            raise PostRequestIllegal(result)
        else:
            return result

    def search(self, search_content, search_type, page):
        """Search interface.

        :params search_content: search content.
        :params search_type: search type.
        :params limit: result count returned by weapi.
        :return: a dict.
        """

        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        params = {'s': search_content, 'type': search_type, 'offset': (page - 1) * 5,
                  'sub': 'false', 'limit': 5}
        result = self.post_request(url, params)
        return result

    def search_song(self, song_name, page=1):
        """Search song by song name.

        :params song_name: song name.
        :params quiet: automatically select the best one.
        :params limit: song count returned by weapi.
        :return: a Song object.
        """

        result = self.search(song_name, search_type=1, page=page)

        if result['result']['songCount'] <= 0:
            self.logger.warning('Song %s not existed!', song_name)
            return BotResult(404, 'Song {} not existed.'.format(song_name))
        else:
            keyword, song_count, songs = song_name, result['result']['songCount'], result['result']['songs']
            songlist = SongList(keyword, song_count, Crawler.dump_songs(songs))
            return BotResult(200, body=songlist)

    # def search_album(self, album_name, quiet=False, page=1):
    #     """Search album by album name.
    #
    #     :params album_name: album name.
    #     :params quiet: automatically select the best one.
    #     :params limit: album count returned by weapi.
    #     :return: a Album object.
    #     """
    #
    #     result = self.search(album_name, search_type=10, page=page)
    #
    #     if result['result']['albumCount'] <= 0:
    #         logger.warning('Album %s not existed!', album_name)
    #         raise SearchNotFound('Album {} not existed'.format(album_name))
    #     else:
    #         albums = result['result']['albums']
    #         if quiet:
    #             album_id, album_name = albums[0]['id'], albums[0]['name']
    #             album = Album(album_id, album_name)
    #             return album
    #         else:
    #             return self.display.select_one_album(albums)
    #
    # def search_artist(self, artist_name, quiet=False, page=1):
    #     """Search artist by artist name.
    #
    #     :params artist_name: artist name.
    #     :params quiet: automatically select the best one.
    #     :params limit: artist count returned by weapi.
    #     :return: a Artist object.
    #     """
    #
    #     result = self.search(artist_name, search_type=100, page=page)
    #
    #     if result['result']['artistCount'] <= 0:
    #         logger.warning('Artist %s not existed!', artist_name)
    #         raise SearchNotFound('Artist {} not existed.'.format(artist_name))
    #     else:
    #         artists = result['result']['artists']
    #         if quiet:
    #             artist_id, artist_name = artists[0]['id'], artists[0]['name']
    #             artist = Artist(artist_id, artist_name)
    #             return artist
    #         else:
    #             return self.display.select_one_artist(artists)

    # def search_playlist(self, playlist_name, quiet=False, page=1):
    #     """Search playlist by playlist name.
    #
    #     :params playlist_name: playlist name.
    #     :params quiet: automatically select the best one.
    #     :params limit: playlist count returned by weapi.
    #     :return: a Playlist object.
    #     """
    #
    #     result = self.search(playlist_name, search_type=1000, page=page)
    #
    #     if result['result']['playlistCount'] <= 0:
    #         logger.warning('Playlist %s not existed!', playlist_name)
    #         raise SearchNotFound('playlist {} not existed'.format(playlist_name))
    #     else:
    #         playlists = result['result']['playlists']
    #         if quiet:
    #             playlist_id, playlist_name = playlists[0]['id'], playlists[0]['name']
    #             playlist = Playlist(playlist_id, playlist_name)
    #             return playlist
    #         else:
    #             return self.display.select_one_playlist(playlists)
    #
    # def search_user(self, user_name, quiet=False, page=1):
    #     """Search user by user name.
    #
    #     :params user_name: user name.
    #     :params quiet: automatically select the best one.
    #     :params limit: user count returned by weapi.
    #     :return: a User object.
    #     """
    #
    #     result = self.search(user_name, search_type=1002, page=page)
    #
    #     if result['result']['userprofileCount'] <= 0:
    #         logger.warning('User %s not existed!', user_name)
    #         raise SearchNotFound('user {} not existed'.format(user_name))
    #     else:
    #         users = result['result']['userprofiles']
    #         if quiet:
    #             user_id, user_name = users[0]['userId'], users[0]['nickname']
    #             user = User(user_id, user_name)
    #             return user
    #         else:
    #             return self.display.select_one_user(users)
    #
    # def get_user_playlists(self, user_id, limit=1000):
    #     """Get a user's all playlists.
    #
    #     warning: loggerin is required for private playlist.
    #     :params user_id: user id.
    #     :params limit: playlist count returned by weapi.
    #     :return: a Playlist Object.
    #     """
    #
    #     url = 'http://music.163.com/weapi/user/playlist?csrf_token='
    #     csrf = ''
    #     params = {'offset': 0, 'uid': user_id, 'limit': limit,
    #               'csrf_token': csrf}
    #     result = self.post_request(url, params)
    #     playlists = result['playlist']
    #     return self.display.select_one_playlist(playlists)

    def get_playlist(self, playlist_id, page=1):
        """Get a playlists's all songs.

        :params playlist_id: playlist id.
        :params limit: length of result returned by weapi.
        :return: a list of Song object.
        """

        url = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token='
        csrf = ''
        params = {'id': playlist_id, 'offset': (page - 1) * 5, 'total': True,
                  'limit': 5, 'n': 1000, 'csrf_token': csrf}
        result = self.post_request(url, params)
        creator = User(result['playlist']['creator']['userId'], result['playlist']['creator']['nickname'])
        playlist_id, playlist_name, track_count, creator, songs = \
            result['playlist']['id'], result['playlist']['name'], result['playlist']['trackCount'], creator, \
            result['playlist']['tracks']
        playlist = Playlist(playlist_id, playlist_name, track_count, creator, Crawler.dump_songs(songs))
        return BotResult(200, body=playlist)

    # def get_album_songs(self, album_id):
    #     """Get a album's all songs.
    #
    #     warning: use old api.
    #     :params album_id: album id.
    #     :return: a list of Song object.
    #     """
    #
    #     url = 'http://music.163.com/api/album/{}/'.format(album_id)
    #     result = self.get_request(url)
    #
    #     songs = result['album']['songs']
    #     songs = [Song(song['id'], song['name']) for song in songs]
    #     return songs
    #
    # def get_artists_hot_songs(self, artist_id):
    #     """Get a artist's top50 songs.
    #
    #     warning: use old api.
    #     :params artist_id: artist id.
    #     :return: a list of Song object.
    #     """
    #     url = 'http://music.163.com/api/artist/{}'.format(artist_id)
    #     result = self.get_request(url)
    #
    #     hot_songs = result['hotSongs']
    #     songs = [Song(song['id'], song['name']) for song in hot_songs]
    #     return songs

    def get_song_detail(self, song_id):
        url = 'http://music.163.com/weapi/v3/song/detail?csrf_token='
        params = {'c': [json.dumps({'id': song_id})], 'ids': [song_id]}
        try:
            result = self.post_request(url, params)
            song = result['songs'][0]
            single_song = Crawler.dump_single_song(song)
            # 获取 song_url
            url = self.get_song_url(song_id)
            single_song.song_url = url
            return BotResult(200, body=single_song)
        except (SongNotAvailable, RequestException) as e:
            return BotResult(400, 'Return {0} when try to post {1} => {2}'.format(e, url, params))

    @exception_handle
    def get_song_url(self, song_id, bit_rate=999000):
        """Get a song's download address.

        :params song_id: song id<int>.
        :params bit_rate: {'MD 128k': 128000, 'HD 320k': 320000}
        :return: a song's download address.
        """
        # 登录成功，使用 login_session，登录失败使用原来的 session
        if self.login_session.cookies.items():
            custom_session = self.login_session
        else:
            custom_session = self.session
        url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        csrf = ''
        params = {'ids': [song_id], 'br': bit_rate, 'csrf_token': csrf}
        result = self.post_request(url, params, custom_session=custom_session)
        song_url = result['data'][0]['url']  # download address
        if song_url is None:  # Taylor Swift's song is not available
            self.logger.warning(
                'Song %s is not available due to copyright issue. => %s',
                song_id, result)
            raise SongNotAvailable(
                'Song {} is not available due to copyright issue.'.format(song_id))
        else:
            self.logger.info('Song url is :{}'.format(song_url))
            return song_url

    # def get_song_lyric(self, song_id):
    #     """Get a song's lyric.
    #
    #     warning: use old api.
    #     :params song_id: song id.
    #     :return: a song's lyric.
    #     """
    #
    #     url = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(  # NOQA
    #         song_id)
    #     result = self.get_request(url)
    #     if 'lrc' in result and result['lrc']['lyric'] is not None:
    #         lyric_info = result['lrc']['lyric']
    #     else:
    #         lyric_info = 'Lyric not found.'
    #     return lyric_info

    def login(self, username, password):
        """Login interface."""

        pattern = re.compile(r'^0\d{2,3}\d{7,8}$|^1[34578]\d{9}$')
        if pattern.match(username):  # use phone number to login
            url = 'https://music.163.com/weapi/login/cellphone'
            params = {
                'phone': username,
                'password': hashlib.md5(password.encode('utf-8')).hexdigest(),
                'rememberLogin': 'true'}
        else:  # use email to login
            url = 'https://music.163.com/weapi/login?csrf_token='
            params = {
                'username': username,
                'password': hashlib.md5(password.encode('utf-8')).hexdigest(),
                'rememberLogin': 'true'}
        try:
            result = self.post_request(url, params, custom_session=self.login_session)
            # self.session.cookies.save()
            uid = result['account']['id']
            msg = '{0}xxxx{1} login success! Uid is {2}'.format(username[:3], username[7:11], uid)
            return BotResult(200, msg)
        except (PostRequestIllegal, RequestException) as e:
            return BotResult(400, 'Return {0} when try to post {1} => {2}'.format(e, url, params))

    @exception_handle
    def write_file(self, songfile, handle=None):
        resp = self.login_session.get(songfile.file_url, stream=True, timeout=self.timeout)
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
