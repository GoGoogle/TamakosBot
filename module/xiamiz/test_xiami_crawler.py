import unittest
from unittest import TestCase

from module.xiamiz.xiami_crawler import Crawler

crawler = Crawler()


class TestCrawler(TestCase):
    def test_search_song(self):
        crawler.search_song("1111")


if __name__ == '__main__':
    unittest.main()
