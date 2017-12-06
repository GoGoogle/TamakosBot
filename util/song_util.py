import taglib

import time

import telegram

from config import application
from config.application import CHUNK_SIZE, FILE_TRANSFER_TIMEOUT


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


def progress_download(session, songfile, handle):
    resp = session.get(songfile.file_url, stream=True, timeout=FILE_TRANSFER_TIMEOUT)
    start = time.time()
    length = int(resp.headers.get('content-length'))
    dl = 0
    for chunk in resp.iter_content(CHUNK_SIZE):
        dl += len(chunk)
        songfile.file_stream.write(chunk)
        network_speed = dl / (time.time() - start)
        if network_speed > 1024 * 1024:
            network_speed_status = '{:.2f}M/s'.format(network_speed / (1024 * 1024))
        else:
            network_speed_status = '{:.2f}KB/s'.format(network_speed / 1024)
        # if dl > 1024 * 1024:
        #     dl_status = '{:.2f} MB'.format(dl / (1024 * 1024))
        # else:
        #     dl_status = '{:.0f} KB'.format(dl / 1024)
        # 已下载大小，总大小，已下载的百分比，网速
        # progress = '{0} / {1:.2f} MB ({2:.0f}%) - {3}'.format(dl_status, length / (1024 * 1024),
        #                                                       dl / length * 100,
        #                                                       network_speed_status)
        raw = "»»»»»»»»»»"
        percent = int(10 - 10 * dl / length)
        dl_status = raw.replace("»", ".", percent)[::-1]
        progress = '`[{0:.0f}%] [{1}] [{2}]`'.format(dl / length * 100, dl_status, network_speed_status)
        if handle:
            handle.update(progress)


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
