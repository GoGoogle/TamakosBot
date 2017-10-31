import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


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

