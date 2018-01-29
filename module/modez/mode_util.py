import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_mode import ModeList
from entity.bot_telegram import ButtonItem


class Util(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def make_modelist(self, index=None, mode=None):
        self.logger.debug("make mode list")
        mlist = ModeList.mode_list
        if index:
            mlist[index] = mode
        return mlist

    def produce_mode_board(self, module_name, sel_mode, sel_modelist):
        self.logger.debug("produce_mode_board")
        if sel_mode.mode_nick == "ⓒ" or sel_mode.mode_nick == "⦿":
            msg_text = "分析 🍐🍐"
        else:
            msg_text = "{0} 🍐🍐".format(sel_mode.mode_nick)

        button_list = [
            [
                InlineKeyboardButton(
                    text=sel_modelist[0].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[0].mode_id).dump_json()
                ),
                InlineKeyboardButton(
                    text=sel_modelist[1].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[1].mode_id).dump_json()
                )
            ],
            [
                InlineKeyboardButton(
                    text=sel_modelist[2].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[2].mode_id).dump_json()
                ),
                InlineKeyboardButton(
                    text=sel_modelist[3].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[3].mode_id).dump_json()
                )
            ],
            [
                InlineKeyboardButton(
                    text=sel_modelist[4].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[4].mode_id).dump_json()
                )
            ]
        ]

        markup = InlineKeyboardMarkup(button_list)
        return {"text": msg_text, "markup": markup}
