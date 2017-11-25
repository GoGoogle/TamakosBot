import logging
import time

import pymysql

from config import application


class DBFile(object):
    """
    使用 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conn = pymysql.connect(*application.SQLITE_DB)

    #
    # def setup_db(self):
    #     self.conn = pymysql.connect(*application.SQLITE_DB)
    #     cursor = self.conn.cursor()
    #     try:
    #         create_tb = 'CREATE TABLE IF NOT EXISTS file (file_id VARCHAR(15) PRIMARY KEY ,' \
    #                     'name VARCHAR(20), size INT(11), ' \
    #                     'mime_type VARCHAR(10), author VARCHAR(20), create_time TIMESTAMP )'
    #         cursor.execute(create_tb)
    #         # cursor.execute('DELETE FROM file')
    #     except:
    #         self.logger.error('setup file table failed', exc_info=True)
    #     finally:
    #         cursor.close()
    #         self.conn.commit()
    #         self.conn.close()

    def check_file(self, conn, f_id):
        cursor = conn.cursor()
        try:
            check_fl = "SELECT * FROM file WHERE file_id=?"

            cursor.execute(check_fl, (f_id,))

            result = cursor.fetchall()
            if result:
                return True
            else:
                return False
        except:
            self.logger.error('store file failed', exc_info=True)
        finally:
            cursor.close()

    def store_file(self, file_id, name, size, mime_type, author, timestamp):
        self.conn = pymysql.connect(*application.SQLITE_DB)
        cursor = self.conn.cursor()
        flag = self.check_file(self.conn, file_id)
        try:
            if not flag:
                store_fl = 'INSERT INTO file VALUES (?, ?, ?, ?, ?, ?)'

                cursor.execute(store_fl, (file_id, name, size, mime_type, author, timestamp))
        except:
            self.logger.error('store file failed', exc_info=True)
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.commit()

    def delete_file(self):
        # TODO
        pass

    def select_file(self, date=time.time()):
        self.conn = pymysql.connect(*application.SQLITE_DB)
        cursor = self.conn.cursor()
        try:
            select_fl = 'SELECT * FROM file WHERE create_time < ?'
            cursor.execute(select_fl, (date,))
            file_tuples = cursor.fetchall()
            return file_tuples
        except:
            self.logger.error('file select_file failed', exc_info=True)
        finally:
            cursor.close()
            self.conn.commit()
