import logging
from functools import wraps

import eyed3

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


def write_id3tags(file_path, song_title, song_artist, album_artist='', song_album='', track_num=2):
    audiofile = eyed3.load(file_path)
    if audiofile:
        audiofile.tag.artist = song_artist
        audiofile.tag.album = song_album
        audiofile.tag.album_artist = album_artist
        audiofile.tag.title = song_title
        audiofile.tag.track_num = track_num

        audiofile.tag.save()
