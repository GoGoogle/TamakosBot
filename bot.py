import logging

from telegram.ext import Updater

from common import config
from handler import commands, messages, listeners

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"' % (update, err))


def main():
    updater = Updater(token=config.BOT_TOKEN)
    dp = updater.dispatcher

    router(dp)  # route the handler

    updater.start_polling()  # 开始轮询
    updater.idle()


def router(dp):
    commands.handler_commands(dp)
    messages.handler_messages(dp)
    listeners.handler_listeners(dp)
    dp.add_error_handler(error)


if __name__ == '__main__':
    logger.info('bot start..')
    main()
