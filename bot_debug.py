import logging
import logging.config
import os

import yaml
from telegram.ext import Updater

from config import application
from handler import boot, monitor


class Bot(object):
    def __init__(self, log_config="config/logconfig_debug.yaml"):
        self.commands = boot.Startup()
        self.monitors = monitor.Monitor()
        self.setup_build(log_config)
        self.logger = logging.getLogger("__name__")

    @staticmethod
    def setup_build(path):
        with open(path, "r") as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
        if not os.path.exists(application.TMP_Folder):
            os.mkdir(application.TMP_Folder)

    def error_handler(self, bot, update, err):
        self.logger.warning('Update "%s" caused error "%s"', update, err)

    def distribute(self, dispatcher):
        boot.Startup().handler_startup(dispatcher)
        monitor.Monitor().handler_response(dispatcher)
        dispatcher.add_error_handler(self.error_handler)

    def start_bot(self):
        self.logger.debug('bot start..')
        updater = Updater(token=application.BOT_TOKEN_DEBUG)
        self.distribute(updater.dispatcher)

        updater.start_polling(timeout=20)
        updater.idle()


if __name__ == '__main__':
    os.environ['HTTP_PROXY'] = "http://127.0.0.1:8118"
    os.environ['HTTPS_PROXY'] = "http://127.0.0.1:8118"
    os.environ['NO_PROXY'] = "m1.music.126.net,10.*.*.*,192.168.*.*,*.local,localhost,127.0.0.1"
    Bot().start_bot()
