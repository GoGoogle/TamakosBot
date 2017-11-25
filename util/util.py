import logging
import taglib
from functools import wraps

import pymysql

from config import application

logger = logging.getLogger(__name__)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in application.ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)

    return wrapped


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False,
                            timeout=application.TIMEOUT)
    query.message.delete()


def write_id3tags(file_path, song_title, song_artist_list, song_album='', track_num='01/10'):
    song = taglib.File(file_path)
    if song:
        song.tags["ARTIST"] = song_artist_list
        song.tags["ALBUM"] = [song_album]
        song.tags["TITLE"] = [song_title]
        song.tags["TRACKNUMBER"] = [track_num]
        song.save()


def get_database_session():
    conn = pymysql.connect(*application.SQLITE_DB, use_unicode=True, charset='utf8')
    conn.autocommit(True)
    return conn
