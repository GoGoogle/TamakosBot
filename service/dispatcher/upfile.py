import logging
import time

import telegram

from database import db_file
from model.file import File

logger = logging.getLogger(__name__)


def upload_file(bot, update):
    audio = update.message.audio
    video = update.message.video
    document = update.message.document
    if audio:
        logger.info('audio:{0}, name:{1}'.format(audio.file_id, audio.title))
        db_file.DBFile().store_file(audio.file_id, audio.title, audio.file_size, audio.mime_type,
                                    update.message.from_user.username, time.time())
    if video:
        logger.info('video:{0}, name:{1}'.format(video.file_id, '佚名'))
        db_file.DBFile().store_file(video.file_id, '佚名', video.file_size, video.mime_type,
                                    update.message.from_user.username, time.time())
    if document:
        logger.info('document:{0}, name:{1}'.format(document.file_id, document.file_name))
        db_file.DBFile().store_file(document.file_id, document.file_name, document.file_size, document.mime_type,
                                    update.message.from_user.username, time.time())


def response_upfile(bot, update):
    file_tuples = db_file.DBFile().select_file()
    file_list = []
    for x in file_tuples:
        file = File(x[0], x[1], x[2], x[3], x[4], x[5])
        file_list.append(file)
    print(file_tuples)
    markdown = '1.hello\n' \
               '2.world\n' \
               '3.tomorrow'.format()
    bot.send_message(chat_id=update.message.chat.id, text=markdown, parse_mode=telegram.ParseMode.MARKDOWN)
