import logging


class MainZ(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def init_login(self, config):
        pass

    def search_music(self, bot, update, kw):
        pass

    def response_single_music(self, bot, update):
        pass

    def response_playlist(self, bot, update, playlist_id):
        pass

    def songlist_turning(self, bot, query, kw, page):
        pass

    def playlist_turning(self, bot, query, playlist_id, page):
        pass

    def deliver_music(self, bot, query, song_id, delete):
        pass

    def download_backend(self, bot, query, songfile, edited_msg):
        pass

    def send__file(self, bot, query, songfile, edited_msg):
        pass
