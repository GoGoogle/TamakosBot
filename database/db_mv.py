import logging

import pymysql

from config import application


class DBMv(object):
    """
    使用 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conn = pymysql.connect(*application.SQLITE_DB)

    def setup_db(self):
        self.conn = pymysql.connect(*application.SQLITE_DB)
        cursor = self.conn.cursor()
        try:
            create_tb = 'CREATE TABLE IF NOT EXISTS mv (file_id VARCHAR(15) PRIMARY KEY ,' \
                        'platform_id VARCHAR(15), title VARCHAR(20), duration FLOAT(10), ' \
                        'quality VARCHAR(10), create_time TIMESTAMP )'
            cursor.execute(create_tb)
            # cursor.execute('DELETE FROM mv')
        except:
            self.logger.error('setup mv table', exc_info=True)
        finally:
            cursor.close()
            self.conn.commit()
            self.conn.close()

    def check_file(self, conn, f_id):
        cursor = conn.cursor()
        try:
            check_fl = "SELECT * FROM mv WHERE file_id=?"

            cursor.execute(check_fl, (f_id,))

            result = cursor.fetchall()
            if result:
                return True
            else:
                return False
        except:
            self.logger.error('store mv failed', exc_info=True)
        finally:
            cursor.close()

    def store_file(self, file_id, platform_id, title, duration, quality, timestamp):
        self.conn = pymysql.connect(*application.SQLITE_DB)
        cursor = self.conn.cursor()
        flag = self.check_file(self.conn, file_id)
        try:
            if not flag:
                store_fl = 'INSERT INTO mv VALUES (?, ?, ?, ?, ?, ?)'

                cursor.execute(store_fl, (file_id, platform_id, title, duration, quality,
                                          timestamp))
        except:
            self.logger.error('store mv failed', exc_info=True)
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.commit()

    def compare_file(self, platform_id, title, duration, quality, fetch_time):
        self.conn = pymysql.connect(*application.SQLITE_DB)
        cursor = self.conn.cursor()
        try:
            search_fl = 'SELECT * FROM mv WHERE' \
                        ' platform_id = ? AND title=? AND duration=? AND quality=? AND create_time>?'

            cursor.execute(search_fl, (platform_id, title, duration, quality, fetch_time - 5284000000))

            file_tuple = cursor.fetchall()

            if file_tuple:
                self.logger.info('file_id: '.format(file_tuple[-1][0]))
                return file_tuple[-1][0]  # 返回 id
            else:
                return ''
        except:
            self.logger.error('mv compare_file failed', exc_info=True)
        finally:
            cursor.close()
            self.conn.commit()

    def delete_file(self):
        # TODO
        pass

    def select_file(self, date):
        self.conn = pymysql.connect(*application.SQLITE_DB)
        cursor = self.conn.cursor()
        try:
            select_fl = 'SELECT * FROM mv'
            cursor.execute(select_fl)
            file_tuple = cursor.fetchall()
            return file_tuple
        except:
            self.logger.error('mv select_file failed', exc_info=True)
        finally:
            cursor.close()
            self.conn.commit()
