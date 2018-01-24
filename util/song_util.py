import time

from config import application
from config.application import CHUNK_SIZE


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


def progress_download(session, songfile, handle):
    resp = session.get(songfile.file_url, stream=True, timeout=application.FILE_TRANSFER_TIMEOUT)
    start = time.time()
    length = int(resp.headers.get('content-length'))
    dl = 0
    for chunk in resp.iter_content(CHUNK_SIZE):
        dl += len(chunk)
        songfile.file_stream.write(chunk)
        network_speed = dl / (time.time() - start)
        if network_speed > 1024 * 1024:
            network_speed_status = '{:.2f} mb/s'.format(network_speed / (1024 * 1024))
        else:
            network_speed_status = '{:.1f} kb/s'.format(network_speed / 1024)
        # if dl > 1024 * 1024:
        #     dl_status = '{:.2f} MB'.format(dl / (1024 * 1024))
        # else:
        #     dl_status = '{:.0f} KB'.format(dl / 1024)

        # progress = '{0} / {1:.2f} MB ({2:.0f}%) - {3}'.format(dl_status, length / (1024 * 1024),
        #                                                       dl / length * 100,
        #                                                       network_speed_status)

        # progress = 'D {0:.2f} MB / {1:.0%} - {2}'.format(length / (1024 * 1024), dl / length, network_speed_status)
        progress = '🍈 🍈 {:.0%}'.format(dl / length)
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
            timeout=application.FILE_TRANSFER_TIMEOUT
        )
