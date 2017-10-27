import logging

from telegram.ext import Updater

from utils import error
from config import configfile
from handler import commands, messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    updater = Updater(token=configfile.bot_token)
    dp = updater.dispatcher

    router(dp)  # route the handler

    updater.start_polling()  # 开始轮询
    updater.idle()


def router(dp):
    commands.handler_commands(dp)
    messages.handler_messages(dp)
    error.handler_errors(dp)


if __name__ == '__main__':
    logger.info('bot start..')
    main()
