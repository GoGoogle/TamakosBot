import logging

import requests
from requests import RequestException

from entity.bot_anime import AnimeFile
from others import bot_telegram
from others.bot_telegram import exception_handle, PostRequestIllegal, BotResult

ANIME_HEADER = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "whatanime.ga"
}


class Crawler(object):
    def __init__(self, timeout=220, proxy=None):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}
        self.session = requests.session()

        cfg = bot_telegram.get_config()
        self.anime_token = cfg.get('api', 'anime_token')

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
        return result

    def get_anime_detail(self, file_content):
        try:
            url = "https://whatanime.ga/api/search?token={}".format(self.anime_token)
            data = {
                "image": file_content
            }
            result = self.post_request(url, data)
            if not result.get("docs"):
                return BotResult(404, "anime not found: {}".format(result))
            else:
                episode_num = result["docs"][0]["episode"]
                if not episode_num:
                    episode_num = 0
                anilist_id, filename, anime_name, season, episode, timeline, similarity = \
                    result["docs"][0]["anilist_id"], result["docs"][0]["filename"], result["docs"][0]["anime"], \
                    result["docs"][0]["season"], episode_num, result["docs"][0]["at"], result["docs"][0]["similarity"]
                tokenthumb = result["docs"][0]["tokenthumb"] if result["docs"][0].get("tokenthumb") else None
                anime = AnimeFile(anilist_id, filename, anime_name, season, episode, timeline, similarity,
                                  tokenthumb=tokenthumb)
                return BotResult(200, body=anime)
        except (PostRequestIllegal, RequestException) as e:
            self.logger.error(e)
            return BotResult(400, "图片识别错误{}".format(e))

    def get_lvideo_url(self, anime_file):
        url = "https://whatanime.ga/preview.php"
        params = {
            "season": anime_file.season,
            "anime": anime_file.anime_name,
            "file": anime_file.filename,
            "t": anime_file.timeline,
            "token": anime_file.tokenthumb
        }
        resp = self.session.get(url, params=params, timeout=self.timeout, proxies=self.proxies)
        return resp.content
