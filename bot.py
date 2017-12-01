import logging
import logging.config
import os

import yaml
from telegram.ext import Updater

from config import application
from handler import commands, messages, monitors


def main():
    updater = Updater(token=application.BOT_TOKEN)
    dp = updater.dispatcher

    router(dp)  # route the handler

    # updater.start_polling(timeout=20)  # 开始轮询
    # updater.idle()
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path='bottoken')
    updater.bot.set_webhook(url='https://telegram.lemo.site/bottoken')


def router(dp):
    commands.Commands().handler_commands(dp)
    messages.handler_messages(dp)
    monitors.Monitors().handler_monitors(dp)
    dp.add_error_handler(error)


def setup_build(path="config/logconfig.yaml"):
    # 日志
    with open(path, "r") as f:
        config = yaml.load(f)
        logging.config.dictConfig(config)
    # 临时目录
    if not os.path.exists(application.TMP_Folder):
        os.mkdir(application.TMP_Folder)


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"', update, err)


if __name__ == '__main__':
    setup_build()
    logger = logging.getLogger("__name__")
    logger.info('bot interface..')
    main()
