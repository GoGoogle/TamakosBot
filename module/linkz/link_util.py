import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_mode import Mode, ModeList
from entity.bot_telegram import ButtonItem


class Util(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_mode_board(self, query, new_mode_nick):
        self.logger.debug("update_mode_board")
        module_name = "mode"
        msg_text = "分析 🍐🍐"

        sel_modelist = ModeList.mode_list

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
                    text=new_mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[4].mode_id).dump_json()
                )
            ]
        ]

        markup = InlineKeyboardMarkup(button_list)
        query.message.edit_text(text=msg_text, reply_markup=markup)
