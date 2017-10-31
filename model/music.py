import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Music(object):
    def __init__(self,
                 mid,
                 name,
                 url='',
                 scheme='',
                 artists=None,
                 duration=0,
                 album=None,
                 mv=None,
                 quality=''
                 ):
        self.logger = logging.getLogger(__name__)
        self.mid = mid
        self.name = name
        self.url = url
        self.scheme = scheme
        self.artists = artists
        self.duration = duration
        self.album = album
        self.mv = mv
        self.quality = quality


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


class Mv(object):
    def __init__(self,
                 mid,
                 name,
                 url='',
                 artist_name=None,
                 duration=0,
                 quality=''
                 ):
        self.logger = logging.getLogger(__name__)
        self.mid = mid
        self.name = name
        self.url = url
        self.artist_name = artist_name
        self.duration = duration
        self.quality = quality


class Artist(object):
    def __init__(self,
                 arid=0,
                 name=None
                 ):
        self.logger = logging.getLogger(__name__)
        self.arid = arid
        self.name = name

    def __str__(self) -> str:
        return 'arid: {0}, name: {1}'.format(self.arid, self.name)


class Album(object):
    def __init__(self,
                 name,
                 alid,
                 artist=None
                 ):
        self.logger = logging.getLogger(__name__)
        self.alid = alid
        self.name = name
        self.artist = artist
