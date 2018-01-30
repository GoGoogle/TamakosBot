import logging
import os

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater

from handler import boot, monitor
from utils import tele


class Bot(object):
    def __init__(self):
        self.setup_logger()
        self.logger = logging.getLogger("__name__")
        self.commands = boot.Startup()
        self.monitors = monitor.Monitor()

        cfg = tele.get_config()
        self.tmp_path = cfg.get('file', 'tmp_path')
        self.cookie_path = cfg.get('file', 'cookie_path')

    @staticmethod
    def setup_logger():
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

    def error_callback(self, bot, update, error):
        try:
            raise error
        except Unauthorized:
            # remove update.message.chat_id from conversation list
            self.logger.warning('Update "%s" caused error Unauthorized', update)
        except BadRequest:
            # handle malformed requests - read more below!
            self.logger.warning('Update "%s" caused error BadRequest', update)
        except TimedOut:
            # handle slow connection problems
            self.logger.warning('Update "%s" caused error TimedOut', update)
        except NetworkError:
            # handle other connection problems
            self.logger.warning('Update "%s" caused error NetworkError', update)
        except ChatMigrated as e:
            # the chat_id of a group has changed, use e.new_chat_id instead
            self.logger.warning('Update "%s" caused error "%s"', update, e)
        except TelegramError as err:
            self.logger.warning('Update "%s" caused error "%s"', update, err)

    def build_directory(self):
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)
        if not os.path.exists(self.cookie_path):
            os.makedirs(self.cookie_path)

    def start_bot(self):
        self.build_directory()

        updater = Updater(token="530204810:AAGSDsy_vkDaaatc0Rnj86ach_rQaDgdPvM")

        boot.Startup().handler_startup(updater.dispatcher)
        monitor.Monitor().handler_response(updater.dispatcher)
        updater.dispatcher.add_error_handler(self.error_callback)

        updater.start_polling(timeout=20)
        updater.idle()


if __name__ == '__main__':
    os.environ['HTTP_PROXY'] = "http://127.0.0.1:8118"
    os.environ['HTTPS_PROXY'] = "http://127.0.0.1:8118"
    os.environ['NO_PROXY'] = "m1.music.126.net,10.*.*.*,192.168.*.*,*.local,localhost,127.0.0.1"
    Bot().start_bot()
