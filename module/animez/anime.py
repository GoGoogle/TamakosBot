import base64
import logging
import os
import time
from io import BytesIO

from telegram import TelegramError, ParseMode

from module.animez import anime_crawler


class Anime(object):
    m_name = 'anime'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Anime, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.crawler = anime_crawler.Crawler()

    def search_anime(self, bot, update):
        self.logger.debug("search anime start..")
        try:
            get_file = bot.get_file(update.message.photo[-1].file_id, timeout=self.timeout)
            download_path = "{}.jpg".format(get_file.file_id)
            bot_result = self.file_download(get_file, download_path)
            if bot_result.get_status() == 400:
                self.logger.error(bot_result.get_msg())
            if bot_result.get_status() == 404:
                self.logger.warning(bot_result.get_msg())
            if bot_result.get_status() == 200:
                anime_file = bot_result.get_body()
                self.show_anime_info(bot, update, anime_file)
                self.send_preview_video(bot, update, anime_file)
        except (ValueError, TelegramError) as e:
            self.logger.error(e)

    def file_download(self, get_file, download_path):
        download_file = None
        try:
            get_file.download(custom_path=download_path, timeout=self.timeout)
            download_file = open(download_path, "rb")
            image_base64 = base64.b64encode(download_file.read())
            bot_result = self.crawler.get_anime_detail(image_base64)
            return bot_result
        except (IOError, ValueError) as e:
            self.logger.error(e)
        finally:
            if download_file and not download_file.closed:
                download_file.close()
            if download_path and os.path.exists(download_path):
                os.remove(download_path)

    def show_anime_info(self, bot, update, anime):
        self.logger.debug("show anime preview..")

        time_format = time.strftime("%H:%M:%S", time.gmtime(anime.timeline))
        text = "`{0}\n{1:0>2d}#{2}\n{3:.1%}`".format(
            anime.anime_name, anime.episode, time_format, anime.similarity)
        bot.send_message(update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

    def send_preview_video(self, bot, update, anime_file):
        content = self.crawler.get_lvideo_url(anime_file)
        with BytesIO(content) as f:
            bot.send_video(update.message.chat.id, f)
