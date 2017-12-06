import logging
from abc import abstractmethod


class CrawlerZ(object):
    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CrawlerZ, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=220, proxy=None):
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def dump_single_song(song):
        pass

    @staticmethod
    def dump_songs(songs):
        pass

    @abstractmethod
    def get_request(self, url, params=None, custom_session=None):
        pass

    def post_request(self, url, params, custom_session=None):
        pass

    def search(self, search_content, search_type, page):
        pass

    def search_song(self, song_name, page=1):
        pass

    def get_playlist(self, playlist_id, page=1):
        pass

    @abstractmethod
    def get_song_detail(self, song_id):
        pass

    def get_song_url(self, song_id):
        pass

    def get_songtop(self, search_type, page=1):
        pass

    def write_file(self, songfile, handle=None):
        pass

    def login(self, username, password):
        pass
