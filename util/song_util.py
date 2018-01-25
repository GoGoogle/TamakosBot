from configparser import ConfigParser


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


def progress_download(session, songfile, handle):
    resp = session.get(songfile.file_url, stream=True, timeout=500)
    length = int(resp.headers.get('content-length'))
    dl = 0

    cfg = ConfigParser()
    cfg.read('custom.ini')
    chunk_size = cfg.get('file', 'chunk_size')

    for chunk in resp.iter_content(chunk_size):
        dl += len(chunk)
        songfile.file_stream.write(chunk)
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
            timeout=500
        )
