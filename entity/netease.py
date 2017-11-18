import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Music(object):
    def __init__(self,
                 mid,
                 name,
                 url='',
                 suffix='mp3',
                 scheme='',
                 artists=None,
                 duration=0,
                 album=None,
                 mv=None,
                 quality='',
                 falseurl=''
                 ):
        self.logger = logging.getLogger(__name__)
        self.mid = mid
        self.name = name
        self.url = url
        self.suffix = suffix
        self.scheme = scheme
        self.artists = artists
        self.duration = duration
        self.album = album
        self.mv = mv
        self.quality = quality
        self.falseurl = 'http://music.163.com/song?id={}'.format(self.mid)


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
                 name=''
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
                 artists=None
                 ):
        self.logger = logging.getLogger(__name__)
        self.alid = alid
        self.name = name
        self.artists = artists


class PlayListSelector(object):
    def __init__(self,
                 pid,
                 name,
                 creator_name,
                 track_count,
                 total_page_num,
                 musics
                 ):
        self.logger = logging.getLogger(__name__)
        self.pid = pid
        self.name = name
        self.creator_name = creator_name
        self.track_count = track_count
        self.total_page_num = total_page_num
        self.musics = musics


class TraceFile(object):
    def __init__(self,
                 file_id,
                 platform_id,
                 name,
                 duration,
                 quality,
                 created_time
                 ):
        self.logger = logging.getLogger(__name__)
        self.file_id = file_id
        self.platform_id = platform_id
        self.name = name
        self.duration = duration
        self.quality = quality
        self.created_time = created_time
