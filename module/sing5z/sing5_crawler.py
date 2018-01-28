import os

import requests

from entity.bot_music import Artist, Song, Toplist, Album
from interface.musics.crawler import CrawlerZ
from utils.tele import GetRequestIllegal, exception_handle, SongNotAvailable
from utils.music import progress_download
from utils.tele import BotResult


class Crawler(CrawlerZ):
    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Crawler, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120, proxy=None):
        super().__init__(timeout, proxy)
        self.session = requests.Session()
        self.download_session = requests.Session()

    @staticmethod
    def dump_single_song(song, mode=0):
        song_id, song_name, artist_id, artist_name = song['ID'], song['SN'], song['user']['ID'], song['user']['NN']
        if mode == 0:
            return Song(song_id, song_name, 264, artists=[Artist(artist_id, artist_name)])
        if mode == 1:
            song_url = song.get('squrl') or song.get('hqurl') or song.get('lqurl')
            if os.path.splitext(song_url)[1] == '.m4a':
                raise SongNotAvailable(
                    'Song {0} id={1} is not available due to copyright issue.'.format(song_name, song_id))
            return Song(song_id, song_name, 264, artists=[Artist(artist_id, artist_name)],
                        album=Album(10010, "5sing 音乐"), song_url=song_url)

    @staticmethod
    def dump_songs(songs, mode=0):
        """
        将字典变成歌曲对象数组
        :param songs: dumped songs
        :param mode: 0 为 all dump，1 为 simple dump
        :return: songlist array
        """
        song_list = []
        for song in songs:
            song = Crawler.dump_single_song(song, mode)
            song_list.append(song)
        return song_list

    @exception_handle
    def get_request(self, url, params=None, custom_session=None):
        """Send a get request.

                :return: a dict or raise Exception.
                """
        if not custom_session:
            resp = self.session.get(url, params=params, timeout=self.timeout,
                                    proxies=self.proxies)
        else:
            resp = custom_session.get(url, params=params, timeout=self.timeout,
                                      proxies=self.proxies)
        result = resp.json()
        if result['success']:
            return result
        else:
            self.logger.error('Return %s when try to get %s', result, url)
            raise GetRequestIllegal(result)

    def post_request(self, url, params, custom_session=None):
        pass

    def search(self, search_content, search_type=2, page=1):
        url = 'http://goapi.5sing.kugou.com/search/search'
        payload = {
            'k': search_content,
            't': 0,
            'filterType': search_type,
            'ps': 5,
            'pn': page
        }
        try:
            result = self.get_request(url, payload)
            return BotResult(200, body=result)
        except IndexError as e:
            return BotResult(400, 'Return {0} when try to search {1}.'.format(e, search_content))

    def get_song_url(self, song_id, search_type='yc'):
        payload = {
            'songid': song_id,
            'songtype': search_type
        }
        result = self.get_request('http://mobileapi.5sing.kugou.com/song/getSongUrl', params=payload)
        return result

    def get_song_detail(self, song_id, search_type='yc'):
        url = 'http://mobileapi.5sing.kugou.com/song/newget'
        payload = {
            'songid': song_id,
            'songtype': search_type
        }
        try:
            result = self.get_request(url, payload)
            # 判断是否能下载?
            single_song = Crawler.dump_single_song(result['data'], mode=1)
            return BotResult(200, body=single_song)
        except (GetRequestIllegal, SongNotAvailable) as e:
            return BotResult(400, 'Return {0} when try to get {1} => {2}'.format(e, url, payload))

    def get_songtop(self, search_type='yc', page=1):
        url = 'http://mobileapi.5sing.kugou.com/rank/detail'
        payload = {
            'id': search_type,
            'pageindex': page,
            'pagesize': 5,
            'time': 0
        }
        result = self.get_request(url, payload)
        if not result['data']['id']:
            return BotResult(404, 'top {} not existed.'.format(search_type))
        else:
            top_id, top_name, track_count, songs = search_type, result['data']['name'], result['data']['count'], \
                                                   result['data']['songs']
            toplist = Toplist(top_id, top_name, track_count, Crawler.dump_songs(songs))
            return BotResult(200, body=toplist)

    @exception_handle
    def write_file(self, songfile, handle=None):
        progress_download(self.download_session, songfile, handle)
