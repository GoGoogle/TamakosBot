import logging

from util import util


class DBAudio(object):
    """
    使用 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # def setup_db(self):
    #     conn = util.get_database_session()
    #     cursor = conn.cursor()
    #     try:
    #         create_tb = 'CREATE TABLE IF NOT EXISTS audio (file_id VARCHAR(15) PRIMARY KEY ,' \
    #                     'platform_id VARCHAR(15), title VARCHAR(20),duration FLOAT(10), ' \
    #                     'scheme VARCHAR(15), create_time TIMESTAMP )'
    #         cursor.execute(create_tb)
    #         # cursor.execute('DELETE FROM audio')
    #     except:
    #         self.logger.error('setup audio table', exc_info=True)
    #     finally:
    #         cursor.close()

    def check_file(self, conn, f_id):
        cursor = conn.cursor()
        try:
            check_fl = "SELECT * FROM audio WHERE file_id=%s"

            cursor.execute(check_fl, (f_id,))

            result = cursor.fetchall()
            if result:
                return True
            else:
                return False
        except:
            self.logger.error('store audio failed', exc_info=True)
        finally:
            cursor.close()

    def store_file(self, file_id, platform_id, title, duration, scheme, timestamp):
        conn = util.get_database_session()
        cursor = conn.cursor()
        flag = self.check_file(conn, file_id)
        try:
            if not flag:
                store_fl = "INSERT INTO audio VALUES (%s, %s, %s, %s, %s, %s)"
                params = (file_id, platform_id, title, duration, scheme, timestamp)
                cursor.execute(store_fl, params)
        except:
            self.logger.error('store audio failed', exc_info=True)
            conn.rollback()
        finally:
            cursor.close()

    def compare_file(self, platform_id, title, duration, scheme, fetch_time):
        conn = util.get_database_session()
        cursor = conn.cursor()
        try:
            search_fl = """SELECT * FROM audio WHERE platform_id=%s AND title=%s AND duration=%s AND scheme=%s"""
            params = (platform_id, title, duration, scheme)
            cursor.execute(search_fl, params)

            file_tuple = cursor.fetchall()

            if file_tuple:
                self.logger.info('file_id: '.format(file_tuple[-1][0]))
                return file_tuple[-1][0]  # 返回 id
            else:
                return ''
        except:
            self.logger.error('audio compare_file failed', exc_info=True)
        finally:
            cursor.close()

    def delete_file(self):
        # TODO
        pass

    def select_file(self, date):
        conn = util.get_database_session()
        cursor = conn.cursor()
        try:
            select_fl = """SELECT * FROM audio"""
            cursor.execute(select_fl)
            file_tuple = cursor.fetchall()
            return file_tuple
        except:
            self.logger.error('audio select_file failed', exc_info=True)
        finally:
            cursor.close()
            conn.close()
