import logging
import time
from queue import Queue

from pymongo import MongoClient
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_mode import ModeList
from entity.bot_telegram import ButtonItem


class Util(object):

    UnHandle, Waiting, WaitFor, Response, Linking, Unlink = range(6)  # define status style

    def __new__(cls, timeout=120, proxy=None):
        pass
        # if not hasattr(cls, 'instance'):
        #     cls.instance = super(Util, cls).__new__(cls)
        # return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # c = MongoClient()
        # db = c.telebot
        # collection = db["user_link"]
        # self.collection = collection
        # self.task_queue = Queue()  # 通过队列不断处理新任务

    def line_up(self, bot, my_id, my_message_id):
        pass
        # self.update_reply_board(bot, my_id, my_message_id, "~", "在吗")
        # self.add_user(my_id, my_message_id)

    def fetch_box(self, my_id, bot):
        pass
        # user = self.collection.find_one({"status": Util.Waiting})
        # if user:
        #     # 更新状态为等待回应
        #     u_id = user["my_id"]
        #     u_msg_id = user["my_message_id"]
        #     # print(u_id, 111)
        #     # print(my_id, 222)
        #     self.update_status(Util.WaitFor, my_id, u_id, u_msg_id)
        #     self.observer_status(bot)  # 自动更新状态
        # else:
        #     # 更新状态为干等
        #     self.update_status(Util.Waiting, my_id)

    def add_user(self, my_id, my_message_id):
        pass
        # link_user = {
        #     "status": Util.UnHandle,
        #     "my_id": my_id,
        #     "my_message_id": my_message_id,
        #     "your_id": None,
        #     "your_message_id": None,
        #     "updated": None
        # }
        # self.collection.replace_one({"my_id": my_id}, link_user, upsert=True)

    def update_status(self, style, my_id=None, u_id=None, u_msg_id=None):
        pass
        # if style == Util.Waiting:
        #     self.collection.update_one(
        #         {"my_id": my_id}, {"$set": {"status": Util.Waiting, "updated": time.time()}})
        # if style == Util.WaitFor:
        #     self.collection.update_one(
        #         {"my_id": my_id},
        #         {"$set": {
        #                  "status": Util.WaitFor, "your_id": u_id, "your_message_id": u_msg_id, "updated": time.time()
        #         }})
        # if style == Util.Unlink:
        #     _user = self.collection.find_one({"my_id": my_id})
        #     if _user["your_id"]:
        #         self.collection.update_one(
        #             {"my_id": my_id}, {"$set": {"status": Util.Unlink}})
        #         self.collection.update_one(
        #             {"my_id": _user["your_id"]}, {"$set": {"status": Util.Unlink}})
        #     else:
        #         self.collection.update_one(
        #             {"my_id": my_id}, {"$set": {"status": Util.UnHandle}})

    def observer_status(self, bot=None):
        pass
        # for waitFor in self.collection.find({"status": Util.WaitFor}):
        #     self.collection.update_one(
        #         {"my_id": waitFor["your_id"]},
        #         {"$set": {
        #             "status": Util.Response, "your_id": waitFor["my_id"], "your_message_id": waitFor["my_message_id"]
        #         }})
        # for response in self.collection.find({"status": Util.Response}):
        #     self.collection.update_one({"my_id": response["your_id"]}, {"$set": {"status": Util.Linking}})
        #     self.collection.update_one({"my_id": response["my_id"]}, {"$set": {"status": Util.Linking}})

        #     self.update_reply_board(bot, response["my_id"], response["my_message_id"], "⦿", "嗯哼")
        #     self.update_reply_board(bot, response["your_id"], response["your_message_id"], "⦿", "哈罗")
        # for unlink in self.collection.find({"status": Util.Unlink}):
        #     self.collection.update_one(
        #         {"my_id": unlink["my_id"]},
        #         {"$set": {"status": Util.UnHandle, "your_id": None, "your_message_id": None, "updated": None}})
        #     self.update_reply_board(bot, unlink["my_id"], unlink["my_message_id"], "88", "分手")

    def get_status(self, user_id):
        pass
        # user = self.collection.find_one({"my_id": user_id})
        # return user

    @staticmethod
    def update_reply_board(bot, chat_id, message_id, new_mode_nick, new_mode_text):
        pass
        # module_name = "mode"
        # msg_text = "{} 🍐🍐".format(new_mode_text)
        # sel_modelist = ModeList.mode_list
        # button_list = [[InlineKeyboardButton(
        #             text=sel_modelist[0].mode_nick,
        #             callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
        #                                      sel_modelist[0].mode_id).dump_json()
        #         ), InlineKeyboardButton(
        #             text=sel_modelist[1].mode_nick,
        #             callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
        #                                      sel_modelist[1].mode_id).dump_json()
        #         )], [
        #         InlineKeyboardButton(
        #             text=sel_modelist[2].mode_nick,
        #             callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
        #                                      sel_modelist[2].mode_id).dump_json()
        #         ),
        #         InlineKeyboardButton(
        #             text=sel_modelist[3].mode_nick,
        #             callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
        #                                      sel_modelist[3].mode_id).dump_json()
        #         )], [
        #         InlineKeyboardButton(
        #             text=new_mode_nick,
        #             callback_data=ButtonItem(module_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
        #                                      sel_modelist[4].mode_id).dump_json()
        #         )]]
        # markup = InlineKeyboardMarkup(button_list)
        # bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg_text, reply_markup=markup)
