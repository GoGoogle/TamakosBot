import logging
import re

from telegram.ext import CallbackQueryHandler, run_async, MessageHandler, Filters

from module.kugouz import kugou
from module.modez import mode
from module.neteasz import netease
from module.qqz import qq
from module.recordz import record
from module.sing5z import sing5
from module.xiamiz import xiami


class Monitor(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mode = mode.Modez()
        self.netease = netease.Netease()
        self.kugou = kugou.Kugou()
        self.xiami = xiami.Xiami()
        self.tencent = qq.Qqz()
        self.sing5 = sing5.Sing5z()
        self.record = record.Recordz()

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
            mode_key = user_data[self.mode.m_name]
            if update.message.text:
                if mode_key == self.netease.m_name:
                    if re.match(r'.*https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*).*', update.message.text):
                        playlist_id = re.search(r'https?://music.163.com/?#?/?m?/playlist((/)|(\?id=))(\d*)',
                                                update.message.text).group(4)
                        self.netease.response_playlist(bot, update, playlist_id)
                    else:
                        self.netease.search_music(bot, update, update.message.text)
                if mode_key == self.xiami.m_name:
                    self.xiami.search_music(bot, update, update.message.text)
                if mode_key == self.kugou.m_name:
                    self.kugou.search_music(bot, update, update.message.text)
                if mode_key == self.tencent.m_name:
                    self.tencent.search_music(bot, update, update.message.text)
                if mode_key == self.sing5.m_name:
                    self.sing5.response_toplist(bot, update, update.message.text)
            if mode_key == self.record.m_name:
                self.record.record_msg(bot, update)

    @run_async
    def netease_music_selector_callback(self, bot, update):
        self.netease.response_single_music(bot, update)

    @run_async
    def sing5_music_selector_callback(self, bot, update):
        self.sing5.response_single_music(bot, update)

    @run_async
    def sing5_music_top_category_callback(self, bot, update):
        self.sing5.response_top_category(bot, update)

    @run_async
    def kugou_music_selector_callback(self, bot, update):
        self.kugou.response_single_music(bot, update)

    @run_async
    def xiami_music_selector_callback(self, bot, update):
        self.xiami.response_single_music(bot, update)

    @run_async
    def qq_music_selector_callback(self, bot, update):
        self.tencent.response_single_music(bot, update)

    def record_selector_callback(self, bot, update):
        self.record.response_chat_enter(bot, update)

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

        """5sing命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.sing5_music_top_category_callback, pattern=r"{\"p\":\"" + self.sing5.top_cate),
            group=3
        )
        dispatcher.add_handler(
            CallbackQueryHandler(self.sing5_music_selector_callback, pattern=r"{\"p\":\"" + self.sing5.m_name),
            group=3
        )

        """酷狗命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.kugou_music_selector_callback, pattern=r"{\"p\":\"" + self.kugou.m_name),
            group=3
        )

        """虾米命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.xiami_music_selector_callback, pattern=r"{\"p\":\"" + self.xiami.m_name),
            group=3
        )

        """qq 音乐命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.qq_music_selector_callback, pattern=r"{\"p\":\"" + self.tencent.m_name),
            group=3
        )

        """记录命令入口"""
        dispatcher.add_handler(
            CallbackQueryHandler(self.record_selector_callback, pattern=r"{\"p\":\"" + self.record.m_name),
            group=3
        )
