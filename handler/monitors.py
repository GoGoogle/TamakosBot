import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, RegexHandler

from service import netease, admin, sing5
from util.util import restricted

logger = logging.getLogger(__name__)


def netease_regex(bot, update):
    key_word = re.search(r'^音乐\s+(.+)$', update.message.text).group(1)
    netease.search_music(bot, update, key_word)


@run_async
def netease_music_selector_callback(bot, update):
    netease.response_single_music(bot, update)


@run_async
def response_netease_playlist(bot, update):
    playlist_id = re.search(r'https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*)', update.message.text).group(4)
    netease.response_playlist(bot, update, playlist_id)


@run_async
def sing5_music_selector_callback(bot, update):
    sing5.response_single_music(bot, update)


@run_async
def response_sing5_toplist(bot, update):
    payload = re.search(r'^5SING\s?(\w*)\s?TOP$', update.message.text).group(1).lower()
    if payload:
        sing5.response_toplist(bot, update, payload)
    else:
        sing5.response_toplist(bot, update)


@restricted
def manage_bot(bot, update):
    payload = re.search(r'^cc:(\w+)\s?(\w*)', update.message.text).groups()
    admin.manage_bot(bot, update, payload)


def handler_monitors(dispatcher):
    dispatcher.add_handler(RegexHandler(r'^音乐\s+(.+)$', netease_regex))
    dispatcher.add_handler(CallbackQueryHandler(netease_music_selector_callback, pattern='netease'))
    dispatcher.add_handler(
        RegexHandler(r'.*https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*).*', response_netease_playlist))
    # dispatcher.add_handler(
    #     MessageHandler(Filters.audio | Filters.video | Filters.document & (~ Filters.forwarded), upload_file))
    dispatcher.add_handler(CallbackQueryHandler(sing5_music_selector_callback, pattern='sing5'))
    dispatcher.add_handler(
        RegexHandler(r'^5SING\s?\w*\s?TOP$', response_sing5_toplist))
    dispatcher.add_handler(
        RegexHandler(r'^cc:.*', manage_bot))
