import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, RegexHandler, MessageHandler, Filters

from service import netease, admin, sing5, upload_file
from util.util import restricted

logger = logging.getLogger(__name__)


@run_async
def netease_music_selector_callback(bot, update):
    netease.response_single_music(bot, update)


@run_async
def response_netease_playlist(bot, update):
    playlist_id = re.search(r'https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*)', update.message.text).group(4)
    netease.response_playlist(bot, update, playlist_id)


def upload_file(bot, update):
    upload_file.upload_file(bot, update)


def response_upfile(bot, update):
    upload_file.response_upfile(bot, update)


@run_async
def sing5_music_selector_callback(bot, update):
    sing5.response_single_music(bot, update)


@run_async
def response_sing5_toplist(bot, update):
    sing5.response_toplist(bot, update)


@restricted
def manage_bot(bot, update):
    payload = re.search(r'^admin:(\w+)\s?(\w*)', update.message.text).groups()
    admin.manage_bot(bot, update, payload)


def handler_monitors(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(netease_music_selector_callback, pattern='netease'))
    dispatcher.add_handler(
        RegexHandler(r'.*https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*).*', response_netease_playlist))
    dispatcher.add_handler(
        MessageHandler(Filters.audio | Filters.video | Filters.document & (~ Filters.forwarded), upload_file))
    dispatcher.add_handler(
        RegexHandler(r'^show up$', response_upfile))
    dispatcher.add_handler(CallbackQueryHandler(sing5_music_selector_callback, pattern='sing5'))
    dispatcher.add_handler(
        RegexHandler(r'^5sing top$', response_sing5_toplist))
    dispatcher.add_handler(
        RegexHandler(r'^admin:.*', manage_bot))
