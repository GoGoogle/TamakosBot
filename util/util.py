import logging
import taglib
from functools import wraps

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
                            text="叮~",
                            show_alert=False,
                            timeout=application.TIMEOUT)
    query.message.delete()


def write_id3tags(file_path, song_title, song_artist_list, song_album='', track_num=2):
    song = taglib.File(file_path)
    if song and song.tags:
        song.tags["ARTIST"] = song_artist_list
        song.tags["ALBUM"] = [].append(song_album)
        song.tags["TITLE"] = [].append(song_title)
        song.tags["TRACKNUMBER"] = [].append(track_num)
        song.save()
