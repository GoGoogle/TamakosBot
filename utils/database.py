from pymongo import MongoClient


class DB(object):
    def __init__(self):
        self.conn = MongoClient('localhost', 27017, maxPoolSize=30, maxIdleTime=50000)

    def new_conn(self):
        return self.conn
