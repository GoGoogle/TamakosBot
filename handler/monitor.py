import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, MessageHandler, Filters

from module.animez import anime
from module.kugouz import kugou
from module.modez import mode
from module.neteasz import netease
from module.qqz import qq
from module.linkz import link
from utils.tele import is_contain_emoji


class Monitor(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mode = mode.Modez()
        self.netease = netease.Netease()
        self.kugou = kugou.Kugou()
        self.tencent = qq.Qqz()
        self.anime = anime.Anime()
        self.link = link.Link()

    def mode_toggle(self, bot, update, user_data):
        """
        mode
        :param bot:
        :param update:
        :param user_data:
        :return:
        """
        self.mode.toggle_mode(bot, update, user_data)

    def mode_analyze(self, bot, update, user_data):
        if user_data.get(self.mode.m_name):
            mode_value = user_data[self.mode.m_name]
            if update.message.text and not is_contain_emoji(update.message.text):
                if mode_value == self.netease.m_name:
                    if re.match(r'.*https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*).*', update.message.text):
                        playlist_id = re.search(r'https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*)',
                                                update.message.text).group(4)
                        self.netease.response_playlist(bot, update, playlist_id)
                    else:
                        self.netease.search_music(bot, update, update.message.text)
                if mode_value == self.kugou.m_name:
                    self.kugou.search_music(bot, update, update.message.text)
                if mode_value == self.tencent.m_name:
                    self.tencent.search_music(bot, update, update.message.text)
            if update.message.photo:
                if mode_value == anime.Anime.m_name:
                    self.anime.search_anime(bot, update)
            if mode_value == self.link.m_name and user_data.get("partner_id"):
                self.link.chat_with_partner(bot, update, user_data.get("partner_id"))

    @run_async
    def netease_music_selector_callback(self, bot, update):
        self.netease.response_single_music(bot, update)

    @run_async
    def kugou_music_selector_callback(self, bot, update):
        self.kugou.response_single_music(bot, update)

    @run_async
    def qq_music_selector_callback(self, bot, update):
        self.tencent.response_single_music(bot, update)

    def handler_response(self, dispatcher):
        """ 模式入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.mode_toggle, pattern=r"{\"p\":\"" + self.mode.m_name, pass_user_data=True))
        dispatcher.add_handler(
            MessageHandler(~ Filters.command, self.mode_analyze, pass_user_data=True)
        )

        """网易命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.netease_music_selector_callback, pattern=r"{\"p\":\"" + self.netease.m_name),
            group=3
        )

        """酷狗命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.kugou_music_selector_callback, pattern=r"{\"p\":\"" + self.kugou.m_name),
            group=3
        )

        """qq 音乐命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.qq_music_selector_callback, pattern=r"{\"p\":\"" + self.tencent.m_name),
            group=3
        )
