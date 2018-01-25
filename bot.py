import logging
from configparser import ConfigParser
from logging.config import fileConfig

from telegram.ext import Updater

from handler import boot, monitor


class Bot(object):
    def __init__(self):
        fileConfig('logging.ini')
        self.logger = logging.getLogger("__name__")
        self.commands = boot.Startup()
        self.monitors = monitor.Monitor()

        cfg = ConfigParser()
        cfg.read('custom.ini')
        self.bot_token = cfg.get('base', 'bot_token')
        self.local_host = cfg.get('webhook', 'local_host')
        self.local_path = cfg.get('webhook', 'local_path')
        self.local_port = cfg.get('webhook', 'local_port')
        self.remote_url = cfg.get('webhook', 'remote_url')
        self.remote_timeout = cfg.get('webhook', 'remote_timeout')

    def start_bot(self):
        self.logger.debug('bot start..')
        updater = Updater(token=self.bot_token)
        boot.Startup().handler_startup(updater.dispatcher)
        monitor.Monitor().handler_response(updater.dispatcher)

        updater.dispatcher.add_error_handler(self.error_handler)

        updater.start_webhook(listen=self.local_host, port=self.local_port,
                              url_path=self.local_path)
        updater.bot.set_webhook(url=self.remote_url, timeout=self.remote_timeout)

    def error_handler(self, bot, update, err):
        self.logger.warning('Update "%s" caused error "%s"', update, err)


if __name__ == '__main__':
    Bot().start_bot()
