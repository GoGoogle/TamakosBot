import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, RegexHandler, MessageHandler, Filters

from service.dispatcher import netease, upfile, sing5

logger = logging.getLogger(__name__)


@run_async
def netease_music_selector_callback(bot, update):
    netease.listen_selector_reply(bot, update)


@run_async
def response_netease_playlist(bot, update):
    playlist_id = re.search(r'https?://music.163.com/?.?/playlist((/)|(\?id=))(\d*)', update.message.text).group(4)
    netease.response_playlist(bot, update, playlist_id)


def upload_file(bot, update):
    upfile.upload_file(bot, update)


def response_upfile(bot, update):
    upfile.response_upfile(bot, update)


@run_async
def sing5_music_selector_callback(bot, update):
    sing5.listen_selector_reply(bot, update)


@run_async
def response_sing5_toplist(bot, update):
    sing5.response_toplist(bot, update)


def handler_monitors(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(netease_music_selector_callback, pattern='netease'))
    dispatcher.add_handler(
        RegexHandler(r'.*https?://music.163.com/?.?/playlist((/)|(\?id=))(\d*).*', response_netease_playlist))
    dispatcher.add_handler(
        MessageHandler(Filters.audio | Filters.video | Filters.document & (~ Filters.forwarded), upload_file))
    dispatcher.add_handler(
        RegexHandler(r'^show up$', response_upfile))
    dispatcher.add_handler(CallbackQueryHandler(sing5_music_selector_callback, pattern='sing5'))
    dispatcher.add_handler(
        RegexHandler(r'^5sing top$', response_upfile))
