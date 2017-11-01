import logging

from telegram.ext import CallbackQueryHandler, run_async

from service.dispatcher import netease

logger = logging.getLogger(__name__)


@run_async
def music_selector_callback(bot, update):
    netease.listen_selector_reply(bot, update)


def handler_listeners(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(music_selector_callback, pattern='netease'))
