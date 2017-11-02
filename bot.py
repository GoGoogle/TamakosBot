import logging
import logging.config

import yaml
from telegram.ext import Updater

from config import application
from database.db_audio import DBAudio
from handler import commands, messages, listeners


def main():
    updater = Updater(token=application.BOT_TOKEN)
    dp = updater.dispatcher

    router(dp)  # route the handler

    updater.start_polling(timeout=20)  # 开始轮询
    updater.idle()


def router(dp):
    commands.handler_commands(dp)
    messages.handler_messages(dp)
    listeners.handler_listeners(dp)
    dp.add_error_handler(error)


def setup_logging(path="config/logconfig.yaml"):
    with open(path, "r") as f:
        config = yaml.load(f)
        logging.config.dictConfig(config)


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"' % (update, err))


if __name__ == '__main__':
    setup_logging()
    DBAudio().setup_db()
    logger = logging.getLogger("__name__")
    logger.info('bot start..')
    main()
