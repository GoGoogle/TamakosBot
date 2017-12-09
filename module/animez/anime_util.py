import logging

import requests
from requests import RequestException

from config import application
from util.excep_util import exception_handle, PostRequestIllegal
from util.telegram_util import BotResult

ANIME_HEADER = {
    "Host": "whatanime.ga"
}


class Crawler(object):
    def __init__(self, timeout=220, proxy=None):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}
        self.session = requests.session()

    @exception_handle
    def post_request(self, url, params, custom_session=None):
        """Send a post request.

        :return: a dict or raise Exception.
        """
        if not custom_session:
            resp = self.session.post(url, data=params, timeout=self.timeout,
                                     proxies=self.proxies)
        else:
            resp = custom_session.post(url, data=params, timeout=self.timeout,
                                       proxies=self.proxies)
        result = resp.json()
        if result['code'] != 200:
            self.logger.error('Return %s when try to post %s => %s',
                              result, url, params)
            raise PostRequestIllegal(result)
        else:
            return result

    def get_anime_detail(self, file_content):
        try:
            url = "https://whatanime.ga/api/search?token=" + application.ANIME_TOKEN
            data = {
                "image": file_content
            }
            result = self.post_request(url, data)
            return result
        except (PostRequestIllegal, RequestException) as e:
            self.logger.error(e)
            return BotResult(400, e)
