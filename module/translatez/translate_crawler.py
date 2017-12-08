import json
import logging

import requests

from config import application
from util.telegram_util import BotResult


class TranslateApi(object):
    def __init__(self, timeout=220, proxy=None):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}
        self.token = application.TRANSLATE_TOKEN
        self.session = requests.session()

    def post_translate(self, content, options):
        url = "http://api.yeekit.com/dotranslate.php"
        params = {
            "from": options["from"],
            "to": options["to"],
            "app_kid": self.token["app_kid"],
            "app_key": self.token["app_key"],
            "text": content
        }
        resp = self.session.post(url, data=params, timeout=self.timeout,
                                 proxies=self.proxies)
        res_content = resp.content[78:].decode("utf-8-sig")
        if res_content.find("error") != -1:
            return BotResult(400, res_content)
        else:
            result = json.loads(res_content)
            return BotResult(200, body=result)
