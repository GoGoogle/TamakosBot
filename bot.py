import logging
import os
from logging.config import fileConfig

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater

from handler import boot, monitor
from utils import tele


class Bot(object):
    def __init__(self):
        fileConfig('config/logging.ini')
        self.logger = logging.getLogger("__name__")
        self.commands = boot.Startup()
        self.monitors = monitor.Monitor()

        cfg = tele.get_config()
        self.bot_token = cfg.get('base', 'bot_token')
        self.local_host = cfg.get('webhook', 'local_host')
        self.local_path = cfg.get('webhook', 'local_path')
        self.local_port = int(cfg.get('webhook', 'local_port'))
        self.remote_url = cfg.get('webhook', 'remote_url')
        self.remote_timeout = int(cfg.get('webhook', 'remote_timeout'))

        self.tmp_path = cfg.get('file', 'tmp_path')
        self.cookie_path = cfg.get('file', 'cookie_path')

    def build_directory(self):
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)
        if not os.path.exists(self.cookie_path):
            os.makedirs(self.cookie_path)

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

    def start_bot(self):
        self.build_directory()
        updater = Updater(token=self.bot_token)
        boot.Startup().handler_startup(updater.dispatcher)
        monitor.Monitor().handler_response(updater.dispatcher)

        updater.dispatcher.add_error_handler(self.error_callback)

        updater.start_webhook(listen=self.local_host, port=self.local_port,
                              url_path=self.local_path)
        updater.bot.set_webhook(url=self.remote_url, timeout=self.remote_timeout)


if __name__ == '__main__':
    Bot().start_bot()
