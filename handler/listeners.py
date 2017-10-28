import logging

from telegram.ext import CallbackQueryHandler

from service.netease import netease

logger = logging.getLogger(__name__)


def music_selector_callback(bot, update):
    netease.listen_selector_reply(bot, update)


def handler_listeners(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(music_selector_callback, pattern='netease'))
