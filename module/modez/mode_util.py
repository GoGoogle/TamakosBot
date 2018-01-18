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
        self.center_module_name = "center_m"
        self.record_module_name = record.Recordz.m_name

    def produce_mode_board(self, cur_module_name, last_module, module_name):
        self.logger.debug("produce_mode_board")
        module_obj = {
            self.common_module_name: "普通",
            self.center_module_name: "回复",
            self.record_module_name: "对话",
            self.kugou_module_name: "酷狗",
            self.qq_module_name: "腾讯",
            self.netease_module_name: "网易",
            self.anime_module_name: "动画"
        }
        msg_mode = "🍭 {0}".format(module_obj.get(cur_module_name))

        button_list = [
            [
                InlineKeyboardButton(
                    text=module_obj[self.kugou_module_name],
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.kugou_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text=module_obj[self.qq_module_name],
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.qq_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text=module_obj[self.netease_module_name],
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.netease_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text=module_obj[self.anime_module_name],
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
