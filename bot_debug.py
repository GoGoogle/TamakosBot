import logging
import os
from logging.config import dictConfig

from telegram.ext import Updater

from handler import boot, monitor


class Bot(object):
    def __init__(self):
        self.setup_logger()
        self.logger = logging.getLogger("__name__")
        self.commands = boot.Startup()
        self.monitors = monitor.Monitor()

    @staticmethod
    def setup_logger():
        dictConfig(dict(
            version=1,
            formatters={
                'f': {'format':
                          '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
            },
            handlers={
                'h': {'class': 'logging.StreamHandler',
                      'formatter': 'f',
                      'level': logging.DEBUG}
            },
            root={
                'handlers': ['h'],
                'level': logging.DEBUG,
            },
        ))

    def error_handler(self, bot, update, err):
        self.logger.warning('Update "%s" caused error "%s"', update, err)

    def start_bot(self):
        self.logger.debug('bot start..')
        updater = Updater(token="530204810:AAGSDsy_vkDaaatc0Rnj86ach_rQaDgdPvM")

        updater.dispatcher.add_error_handler(self.error_handler)

        boot.Startup().handler_startup(updater.dispatcher)
        monitor.Monitor().handler_response(updater.dispatcher)

        updater.start_polling(timeout=20)
        updater.idle()


if __name__ == '__main__':
    os.environ['HTTP_PROXY'] = "http://127.0.0.1:8118"
    os.environ['HTTPS_PROXY'] = "http://127.0.0.1:8118"
    os.environ['NO_PROXY'] = "m1.music.126.net,10.*.*.*,192.168.*.*,*.local,localhost,127.0.0.1"
    Bot().start_bot()
