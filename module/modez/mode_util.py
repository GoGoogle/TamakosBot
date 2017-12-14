import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_telegram import ButtonItem
from module.animez import anime
from module.kugouz import kugou
from module.neteasz import netease
from module.qqz import qq
from module.recordz import record


class Util(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.netease_module_name = netease.Netease.m_name
        self.kugou_module_name = kugou.Kugou.m_name
        self.qq_module_name = qq.Qqz.m_name
        self.anime_module_name = anime.Anime.m_name
        self.common_module_name = "common_m"
        self.super_module_name = "super_m"
        self.record_module_name = record.Recordz.m_name

    def produce_mode_board(self, last_module, module_name):
        self.logger.debug("produce_mode_board")

        msg_mode = "模式选择"

        button_list = [
            [
                InlineKeyboardButton(
                    text='酷狗音乐',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.kugou_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text='腾讯音乐',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.qq_module_name).dump_json()
                )
            ],
            [
                InlineKeyboardButton(
                    text='网易音乐',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.netease_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text='动画索引',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.anime_module_name).dump_json()
                )
            ]
        ]
        if last_module:
            button_list.append([InlineKeyboardButton(
                text=last_module["title"],
                callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         last_module["name"]).dump_json()
            )])

        markup = InlineKeyboardMarkup(button_list)
        return {"text": msg_mode, "markup": markup}
