import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, RegexHandler

from service import netease, admin, sing5, kugou
from util.util import restricted

logger = logging.getLogger(__name__)


def netease_regex(bot, update):
    """网易云命令入口"""
    key_word = re.search(r'^.+\s(.+)$', update.message.text).group(1)
    netease.search_music(bot, update, key_word)


@run_async
def netease_music_selector_callback(bot, update):
    netease.response_single_music(bot, update)


@run_async
def response_netease_playlist(bot, update):
    playlist_id = re.search(r'https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*)', update.message.text).group(4)
    netease.response_playlist(bot, update, playlist_id)


def sing5_regex(bot, update):
    """5sing音乐命令入口"""
    payload = re.search(r'^\w+\s(1|2|3)?\s?(.+)$', update.message.text).groups()
    sing5.search_music(bot, update, payload)


@run_async
def sing5_music_selector_callback(bot, update):
    sing5.response_single_music(bot, update)


@run_async
def response_sing5_toplist(bot, update):
    payload = re.search(r'^TOP\s?(\w*)?$', update.message.text).group(1).lower()
    if payload:
        sing5.response_toplist(bot, update, payload)
    else:
        sing5.response_toplist(bot, update)


def kugou_regex(bot, update):
    """酷狗命令入口"""
    key_word = re.search(r'^\w*\s(\w+)$', update.message.text).group(1)
    kugou.search_music(bot, update, key_word)


@run_async
def kugou_music_selector_callback(bot, update):
    kugou.response_single_music(bot, update)


@restricted
def manage_bot(bot, update):
    payload = re.search(r'^cc:(\w+)\s?(\w*)', update.message.text).groups()
    admin.manage_bot(bot, update, payload)


def handler_monitors(dispatcher):
    dispatcher.add_handler(RegexHandler(r'^(音乐|m)\s(.+)$', netease_regex))
    dispatcher.add_handler(RegexHandler(r'^(5SING|5)\s(1|2|3)?\s?(.+)$', sing5_regex))
    dispatcher.add_handler(CallbackQueryHandler(netease_music_selector_callback, pattern='netease'))
    dispatcher.add_handler(
        RegexHandler(r'.*https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*).*', response_netease_playlist))
    dispatcher.add_handler(CallbackQueryHandler(sing5_music_selector_callback, pattern='sing5'))
    dispatcher.add_handler(
        RegexHandler(r'^TOP(\s\w*)?$', response_sing5_toplist))
    dispatcher.add_handler(
        RegexHandler(r'^(酷狗|k)\s(\w+)$', kugou_regex))
    dispatcher.add_handler(CallbackQueryHandler(kugou_music_selector_callback, pattern='kg'))
    dispatcher.add_handler(
        RegexHandler(r'^cc:.*', manage_bot))
