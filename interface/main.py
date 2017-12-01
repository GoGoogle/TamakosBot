import logging


class MainZ(object):
    def __init__(self, timeout=120):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout

    def init_login(self, config):
        pass

    def search_music(self, bot, update, kw):
        pass

    def response_single_music(self, bot, update):
        pass

    def response_playlist(self, bot, update, playlist_id):
        pass

    def response_toplist(self, bot, update, search_type):
        pass

    def songlist_turning(self, bot, query, kw, page):
        pass

    def playlist_turning(self, bot, query, playlist_id, page):
        pass

    def toplist_turning(self, bot, query, search_type, page):
        pass

    def deliver_music(self, bot, query, song_id, delete):
        pass

    def handle_callback(self, bot, query, button_item):
        pass

    def download_backend(self, bot, query, songfile, edited_msg):
        pass

    def send_file(self, bot, query, songfile, edited_msg):
        pass
