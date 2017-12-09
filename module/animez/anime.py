import base64
import logging
import os
import uuid

from config import application
from module.animez import anime_util


class Anime(object):
    m_name = 'anime'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Anime, cls).__new__(cls)
        return cls.instance

    def __init__(self, timeout=120):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.crawler = anime_util.Crawler()

    def search_anime(self, bot, update):
        self.logger.debug("search anime start..")
        file_path = ""
        server_file = None
        try:
            file_id = update.message.photo[0]
            random_str = str(uuid.uuid4())
            filename = "{0}{1}.{2}".format(file_id, random_str, "png")
            file_path = os.path.join(application.TMP_Folder, filename)
            file = bot.get_file(file_id, timeout=self.timeout)
            server_file = open(file_path, "w+")
            file.download(out=server_file, timeout=self.timeout)
            image_base64 = base64.b64encode(server_file.read())
            bot_result = self.crawler.get_anime_detail(image_base64)
            if bot_result.get_status() == 400:
                pass
            if bot_result.get_status() == 200:
                pass
        except (IOError, ValueError) as e:
            self.logger.error(e)
        finally:
            if not server_file.closed:
                server_file.close()
            if server_file:
                os.remove(file_path)
