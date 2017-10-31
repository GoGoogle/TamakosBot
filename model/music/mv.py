import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


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
