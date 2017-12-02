import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, RegexHandler
from module.kugouz import kugou
from module.managez import admin
from module.neteasz import netease
from module.sing5z import sing5
from util.telegram_util import restricted


class Monitors(object):
    def __init__(self):
        self.netease = netease.Netease()
        self.kugou = kugou.Kugou()
        self.sing5 = sing5.Sing5z()
        self.admin = admin.Adminz()
        self.logger = logging.getLogger(__name__)

    def netease_regex(self, bot, update):
        """网易云命令入口"""
        key_word = re.search(r'^.+\s(.+)$', update.message.text).group(1)
        self.netease.search_music(bot, update, key_word)

    @run_async
    def netease_music_selector_callback(self, bot, update):
        self.netease.response_single_music(bot, update)

    @run_async
    def response_netease_playlist(self, bot, update):
        playlist_id = re.search(r'https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*)',
                                update.message.text).group(4)
        self.netease.response_playlist(bot, update, playlist_id)

    def sing5_regex(self, bot, update):
        """5sing音乐命令入口"""
        payload = re.search(r'^\w+\s([123])?\s?(.+)$', update.message.text).groups()
        self.sing5.search_music(bot, update, payload)

    @run_async
    def sing5_music_selector_callback(self, bot, update):
        self.sing5.response_single_music(bot, update)

    @run_async
    def response_sing5_toplist(self, bot, update):
        payload = re.search(r'^TOP\s?(\w*)?\s(五婶|5)$', update.message.text).group(1).lower()
        if payload:
            self.sing5.response_toplist(bot, update, payload)
        else:
            self.sing5.response_toplist(bot, update)

    def kugou_regex(self, bot, update, user_data):
        """酷狗命令入口"""
        key_word = re.search(r'^\w*\s(\w+)$', update.message.text).group(1)
        self.kugou.search_music(bot, update, key_word, user_data)

    @run_async
    def kugou_music_selector_callback(self, bot, update, user_data):
        self.kugou.response_single_music(bot, update, user_data)

    @restricted
    def manage_bot(self, bot, update):
        payload = re.search(r'^cc:(\w+)\s?(\w*)', update.message.text).groups()
        self.admin.manage_bot(bot, update, payload)

    def handler_monitors(self, dispatcher):
        dispatcher.add_handler(RegexHandler(r'^(音乐|m)\s(.+)$', self.netease_regex))
        dispatcher.add_handler(RegexHandler(r'^(五婶|5)\s(1|2|3)?\s?(.+)$', self.sing5_regex))
        dispatcher.add_handler(CallbackQueryHandler(self.netease_music_selector_callback,
                                                    pattern=r"{\"p\":\"" + self.netease.m_name))
        dispatcher.add_handler(
            RegexHandler(r'.*https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*).*',
                         self.response_netease_playlist))
        dispatcher.add_handler(
            CallbackQueryHandler(self.sing5_music_selector_callback, pattern=r"{\"p\":\"" + self.sing5.m_name))
        dispatcher.add_handler(
            RegexHandler(r'^TOP(\s\w*)?\s(五婶|5)$', self.response_sing5_toplist))
        dispatcher.add_handler(
            RegexHandler(r'^(酷狗|k)\s(\w+)$', self.kugou_regex, pass_user_data=True))
        dispatcher.add_handler(
            CallbackQueryHandler(self.kugou_music_selector_callback, pattern=r"{\"p\":\"" + self.kugou.m_name,
                                 pass_user_data=True))
        dispatcher.add_handler(
            RegexHandler(r'^cc:.*', self.manage_bot))
