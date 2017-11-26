import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Music(object):
    def __init__(self,
                 mid,
                 name,
                 url='',
                 suffix='mp3',
                 bitrate='',
                 duration=0,
                 mhash='',
                 singer_name='',
                 album_name='酷狗音乐',
                 ):
        self.logger = logging.getLogger(__name__)
        self.mid = mid
        self.name = name
        self.url = url
        self.suffix = suffix
        self.bitrate = bitrate
        self.duration = duration
        self.mhash = mhash
        self.singer_name = singer_name
        self.album_name = album_name
        self.falseurl = 'http://www.kugou.com/song/#hash={0}&album_id={1}'.format(self.mhash, self.mid)


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
