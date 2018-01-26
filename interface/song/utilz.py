import logging
from others import bot_telegram


class UtilZ(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.tmp_folder = bot_telegram.get_config().get('file', 'tmp_path')

    def get_songlist_selector(self, curpage, songlist):
        pass

    def produce_songlist_panel(self, module_name, songlist_selector):
        pass

    def get_playlist_selector(self, curpage, playlist):
        pass

    def produce_playlist_panel(self, module_name, playlist_selector):
        pass

    def get_toplist_selector(self, curpage, toplist):
        pass

    def produce_toplist_panel(self, module_name, toplist_selector):
        pass

    def get_songfile(self, song):
        pass
