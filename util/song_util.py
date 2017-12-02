import taglib

import telegram

from config import application


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


def write_id3tags(file_path, song_title, song_artist_list, song_album=None, track_num='01/10'):
    song = taglib.File(file_path)
    if song:
        song.tags["ARTIST"] = song_artist_list
        song.tags["ALBUM"] = [song_album]
        song.tags["TITLE"] = [song_title]
        song.tags["TRACKNUMBER"] = [track_num]
        song.save()


class ProgressHandle(object):
    def __init__(self, bot, query, msg_id):
        self.bot = bot
        self.query = query
        self.msg_id = msg_id

    def update(self, progress_status):
        self.bot.edit_message_text(
            chat_id=self.query.message.chat.id,
            message_id=self.msg_id,
            text=progress_status,
            disable_web_page_preview=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
            timeout=application.FILE_TRANSFER_TIMEOUT
        )
