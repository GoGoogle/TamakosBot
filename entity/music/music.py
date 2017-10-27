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
        self.quality = quality

    def __str__(self) -> str:
        return 'mid: {0}, name: {1}, url: {2},' \
               ' scheme: {3}, artists: {4}, duration: {5},' \
               ' album: {6}, quality: {7}'.format(self.mid, self.name, self.url,
                                                  self.scheme, self.artists, self.duration,
                                                  self.album, self.quality)
