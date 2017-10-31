import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


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

