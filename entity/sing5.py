import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Song(object):
    def __init__(self,
                 mid,
                 name,
                 url='',
                 singer=None,
                 mtype='fc',
                 size=0,
                 popularity=0,
                 falseurl=''
                 ):
        self.logger = logging.getLogger(__name__)
        self.mid = mid
        self.name = name
        self.url = url
        self.singer = singer
        self.mtype = mtype
        self.size = size
        self.popularity = popularity
        self.falseurl = falseurl


class Singer(object):
    def __init__(self, sid, name):
        self.logger = logging.getLogger(__name__)
        self.sid = sid
        self.name = name


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


class MusicTopSelector(object):
    def __init__(self,
                 mtype,
                 title,
                 cur_page_code,
                 total_page_num,
                 musics
                 ):
        self.logger = logging.getLogger(__name__)
        self.mtype = mtype
        self.title = title
        self.cur_page_code = cur_page_code
        self.total_page_num = total_page_num
        self.musics = musics
