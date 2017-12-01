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
    def post_request(self, url, params, custom_session=None):
        pass

    def get_request(self, url, params=None, custom_session=None):
        pass

    def get_song_detail(self, song_id):
        pass
