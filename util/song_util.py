import logging
import taglib
from abc import abstractmethod

import requests
import telegram
from config import application


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


def write_id3tags(file_path, song_title, song_artist_list, song_album=None, track_num='01/10'):
    song = taglib.File(file_path)
    if song:
        song.tags["ARTIST"] = song_artist_list
        song.tags["ALBUM"] = [song_album]
        song.tags["TITLE"] = [song_title]
        song.tags["TRACKNUMBER"] = [track_num]
        song.save()


class Crawlerz(object):
    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Crawlerz, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120, proxy=None):
        self.session = requests.Session()
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}
        self.logger = logging.getLogger(__name__)

    def search(self, search_content, search_type, page):
        pass

    @abstractmethod
    def search_song(self, song_name, page=1):
        pass

    def get_playlist(self, playlist_id, page=1):
        pass

    @abstractmethod
    def get_song_detail(self, song_id):
        pass

    def get_song_url(self, song_id):
        pass

    @abstractmethod
    def write_file(self, songfile, handle=None):
        pass

    def login(self, username, password):
        pass


class ProgressHandle(object):
    def __init__(self, bot, query, msg_id):
        self.bot = bot
        self.query = query
        self.msg_id = msg_id

    def update(self, progress_status):
        self.bot.edit_message_text(
            chat_id=self.query.message.chat.id,
            message_id=self.msg_id,
            text=progress_status,
            disable_web_page_preview=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
            timeout=application.FILE_TRANSFER_TIMEOUT
        )
