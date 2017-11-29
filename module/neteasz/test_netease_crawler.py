import unittest
from unittest import TestCase

from entity.bot_telegram import SongFile
from module.neteasz.netease_crawler import Crawler

crawler = Crawler()


class TestCrawler(TestCase):
    # def test_search_song(self):
    #     bot_result = Crawler().search_song('光阴的故事', page=1)
    #     print(bot_result.get_body().to_json())

    # def test_get_playlist_songs(self):
    #     bot_result = Crawler().get_playlist(1990048628)
    #     print(bot_result.get_body().to_json())

    # def test_add_login(self):
    #     bot_result = crawler.login('13625625358', 'iamlg521520')
    #     print(bot_result.get_msg())
    #
    # def test_get_song_url(self):
    #     print(crawler.get_song_url(27808044))

    # def test_get_song_detail(self):
    #     bot_result = Crawler().get_song_detail(27808044)
    #     pprint(bot_result.get_body().to_json())

    def test_write_file(self):
        sonfile = SongFile('lisi.mp3', './',
                           'http://m8c.music.126.net/20171129214958/fbe914ad3ae1677ad5b230e2133093f8/ymusic/6946/6458/714f/fd281f506ef177ed2ba00a207a14e2cb.mp3',
                           open('list.mp3', 'wb+'))
        crawler.write_file(sonfile)
        sonfile.file_stream.close()


if __name__ == '__main__':
    unittest.main()
