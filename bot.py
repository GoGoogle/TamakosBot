import logging
import logging.config
import os

import yaml
from telegram.ext import Updater

from config import application
from database import db_audio, db_mv, db_file
from handler import commands, messages, monitors


def main():
    updater = Updater(token=application.BOT_TOKEN)
    dp = updater.dispatcher

    router(dp)  # route the handler

    # updater.start_polling(timeout=20)  # 开始轮询
    # updater.idle()
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path='bottoken')
    updater.bot.set_webhook(url='https://www.lemo.site/bottoken')


def router(dp):
    commands.handler_commands(dp)
    messages.handler_messages(dp)
    monitors.handler_monitors(dp)
    dp.add_error_handler(error)


def setup_logging(path="config/logconfig.yaml"):
    with open(path, "r") as f:
        config = yaml.load(f)
        logging.config.dictConfig(config)


def db_init():
    db_audio.DBAudio().setup_db()
    db_mv.DBMv().setup_db()
    db_file.DBFile().setup_db()


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"' % (update, err))


def mk_tmp_dir(tmp):
    if not os.path.exists(tmp):
        os.mkdir(tmp)


if __name__ == '__main__':
    setup_logging()
    mk_tmp_dir(application.TMP_Folder)
    db_init()
    logger = logging.getLogger("__name__")
    logger.info('bot start..')
    main()
