import logging


class UtilZ(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_songlist_selector(self, curpage, songlist):
        pass

    def produce_songlist_panel(self, songlist_selector):
        pass

    def get_playlist_selector(self, curpage, playlist):
        pass

    def produce_playlist_panel(self, playlist_selector):
        pass

    def get_songfile(self, song):
        pass
