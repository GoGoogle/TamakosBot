import logging
import time

from pymongo import MongoClient
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_mode import ModeList
from entity.bot_telegram import ButtonItem


class Util(object):

    UnHandle, Waiting, WaitFor, Response, Linking = range(5)  # define status style

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        c = MongoClient()
        db = c.telebot
        collection = db["user_link"]
        self.collection = collection
        self.box = []

    def update_reply_board(self, bot, chat_id, message_id, new_mode_nick):
        self.logger.debug("update_reply_board")
        module_name = "mode"
        msg_text = "分析 🍐🍐"
        sel_modelist = ModeList.mode_list
        button_list = [[InlineKeyboardButton(
                    text=sel_modelist[0].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[0].mode_id).dump_json()
                ), InlineKeyboardButton(
                    text=sel_modelist[1].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[1].mode_id).dump_json()
                )], [
                InlineKeyboardButton(
                    text=sel_modelist[2].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[2].mode_id).dump_json()
                ),
                InlineKeyboardButton(
                    text=sel_modelist[3].mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[3].mode_id).dump_json()
                )], [
                InlineKeyboardButton(
                    text=new_mode_nick,
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             sel_modelist[4].mode_id).dump_json()
                )]]
        markup = InlineKeyboardMarkup(button_list)
        bot.editMessageText(chat_id=chat_id, message_id=message_id, text=msg_text, reply_markup=markup)

    def add_user(self, my_id, my_message_id):
        link_user = {
            "my_id": my_id,
            "my_message_id": my_message_id,
            "updated": time.time()
        }
        self.collection.insert(link_user)

    def get_status(self, user_id):
        pass

    def update_status(self, style, my_id=None, my_msg=None, u_id=None, u_msg=None):
        pass

    def line_up(self, my_id, my_message_id):
        self.add_user(my_id, my_message_id)
        # TODO clean box

    def fetch_box(self, my_id):
        if len(self.box) != 0:
            u_id = self.box.pop()
        else:
            self.box.append(my_id)

