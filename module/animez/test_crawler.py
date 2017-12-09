import unittest
from unittest import TestCase

from module.animez import anime_util

crawler = anime_util.Crawler()


class TestCrawler(TestCase):
    def test_get_anime_detail(self):
        crawler.get_anime_detail()


if __name__ == '__main__':
    unittest.main()
