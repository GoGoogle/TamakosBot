import logging
from telegram.ext import Updater
from common import application, log
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


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"' % (update, err))


if __name__ == '__main__':
    log.setup_logging()
    logger = logging.getLogger("__name__")
    logger.info('bot start..')
    main()
