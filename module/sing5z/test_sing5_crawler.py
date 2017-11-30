import unittest
from pprint import pprint
from unittest import TestCase

from module.sing5z.sing5_crawler import Crawler

crawler = Crawler()


class TestCrawler(TestCase):
    # def test_get_songtop(self):
    #     bot_result = crawler.get_songtop('yc')
    #     pprint(bot_result.get_body().to_json())

    def test_get_song_detail(self):
        bot_result = crawler.get_song_detail(3458584, 'yc')
        pprint(bot_result.get_body().to_json())


if __name__ == '__main__':
    unittest.main()
