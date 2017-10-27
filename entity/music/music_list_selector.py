import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


class MusicListSelector(object):
    def __init__(self,
                 keyword,
                 cur_page_code,
                 total_page_num,
                 musics
                 ):
        self.logger = logging.getLogger(__name__)
        self.keyword = keyword
        self.cur_page_code = cur_page_code
        self.total_page_num = total_page_num
        self.musics = musics

    def __str__(self) -> str:
        return 'keyword: {0}, cur_page_code: {1}, total_page_num: {2}, musics: {3}'.format(
            self.keyword, self.cur_page_code, self.total_page_num, self.musics)
