import logging
from configparser import ConfigParser


class UtilZ(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        cfg = ConfigParser()
        cfg.read('custom.ini')
        self.tmp_folder = cfg.get('file', 'temporary_directory')

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
