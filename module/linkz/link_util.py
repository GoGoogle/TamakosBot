import logging
import time
from queue import Queue

from pymongo import MongoClient
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_mode import ModeList
from entity.bot_telegram import ButtonItem


class Util(object):

    UnHandle, Waiting, WaitFor, Response, Linking, Unlink = range(6)  # define status style
    BOT = None

    def __new__(cls, timeout=120, proxy=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Util, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        c = MongoClient()
        db = c.telebot
        collection = db["user_link"]
        self.collection = collection
        self.task_queue = Queue()  # 通过队列不断处理新任务

    def line_up(self, bot, my_id, my_message_id):
        Util.BOT = bot
        self.update_reply_board(bot, my_id, my_message_id, "~")
        self.add_user(my_id, my_message_id)
        self.task_queue.put(100)

    def fetch_box(self, my_id):
        _user = self.collection.find_one({"status": Util.Waiting})
        if _user:
            # 更新状态为等待回应
            u_id = _user.my_id
            self.update_status(Util.WaitFor, my_id, u_id)
        else:
            # 更新状态为干等
            self.update_status(Util.Waiting, my_id)

    def add_user(self, my_id, my_message_id):
        link_user = {
            "status": Util.UnHandle,
            "my_id": my_id,
            "my_message_id": my_message_id,
            "your_id": None,
            "your_message_id": None,
            "updated": None
        }
        self.collection.insert_one(link_user)

    def update_status(self, style, my_id=None, u_id=None):
        if style == Util.Waiting:
            self.collection.update_one(
                {"my_id": my_id}, {"$set": {"status": Util.Waiting, "updated": time.time()}})
        if style == Util.WaitFor:
            self.collection.update_one(
                {"my_id": my_id}, {"$set": {"status": Util.WaitFor, "your_id": u_id}})
        if style == Util.Unlink:
            self.collection.update_one(
                {"my_id": my_id}, {"$set": {"status": Util.Unlink}})

    def observer_status(self):
        for waitFor in self.collection.find({"status": Util.WaitFor}):
            self.collection.update_one(
                {"your_id": waitFor.your_id},
                {"$set": {"status": Util.Response, "your_id": waitFor.my_id, "your_message_id": waitFor.my_message_id}})
        for response in self.collection.find({"status": Util.Response}):
            self.collection.update_one({"my_id": response.your_id}, {"$set": {"status": Util.Linking}})
            self.collection.update_one({"my_id": response.my_id}, {"$set": {"status": Util.Linking}})

            self.update_reply_board(Util.BOT, response.my_id, response.my_message_id, "⦿")
            self.update_reply_board(Util.BOT, response.your_id, response.your_message_id, "⦿")
        for unlink in self.collection.find({"status": Util.Unlink}):
            self.collection.update_one(
                {"my_id": unlink.my_id},
                {"$set": {"status": Util.UnHandle, "your_id": None, "your_message_id": None, "updated": None}})
            self.collection.update_one(
                {"my_id": unlink.your_id},
                {"$set": {"status": Util.UnHandle, "your_id": None, "your_message_id": None, "updated": None}})
            self.update_reply_board(Util.BOT, unlink.my_id, unlink.my_message_id, "ⓒ")
            self.update_reply_board(Util.BOT, unlink.your_id, unlink.your_message_id, "ⓒ")

    def get_status(self, user_id):
        user = self.collection.find_one({"my_id": user_id})
        return user

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


