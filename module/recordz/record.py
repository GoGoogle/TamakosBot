import logging

from config import application
from entity.bot_telegram import BotMessage, ButtonItem
from module.recordz import record_util
from util import telegram_util


class Recordz(object):
    m_name = "recordz"

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Recordz, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.util = record_util.Utilz()
        self.store = telegram_util.DataStore()

    @staticmethod
    def get_module_name(self):
        return self.m_name

    def record_msg(self, bot, update):
        """
        判断聊天室是否为"东方情报部门" 聊天室
        :param bot:
        :param update:
        :return:
        """
        bot_msg = BotMessage.get_botmsg(update['message'])
        self.logger.debug('msg send success!')
        panel = self.util.produce_record_panel(bot_msg, self.m_name, self.store)
        bot.send_message(chat_id=application.ADMINS[0], text=panel["text"],
                         reply_markup=panel["markup"])
        if bot_msg.bot_content.picture.sticker:
            bot.send_sticker(chat_id=application.ADMINS[0], sticker=bot_msg.bot_content.picture.sticker)
        if bot_msg.bot_content.photo:
            bot.send_photo(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                           photo=bot_msg.bot_content.photo)

    def record_reply(self, bot, update):
        try:
            bot_msg = BotMessage.get_botmsg(update['message'])
            if self.store.is_exist(ButtonItem.OPERATE_REPLY):
                reply_to_msg_id = self.store.get(ButtonItem.OPERATE_REPLY)
            else:
                reply_to_msg_id = None
            if self.store.is_exist(ButtonItem.OPERATE_ENTER):
                if bot_msg.bot_content.text:
                    bot.send_message(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                     text=bot_msg.bot_content.text,
                                     reply_to_message_id=reply_to_msg_id)
                if bot_msg.bot_content.picture.sticker:
                    bot.send_sticker(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                     sticker=bot_msg.bot_content.picture.sticker,
                                     reply_to_message_id=reply_to_msg_id)
                if bot_msg.bot_content.photo:
                    bot.send_photo(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                   photo=bot_msg.bot_content.photo,
                                   reply_to_message_id=reply_to_msg_id)
                if bot_msg.bot_content.audio:
                    bot.send_audio(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                   audio=bot_msg.bot_content.audio,
                                   reply_to_message_id=reply_to_msg_id)
                if bot_msg.bot_content.video:
                    bot.send_video(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                   video=bot_msg.bot_content.video,
                                   reply_to_message_id=reply_to_msg_id)
                if bot_msg.bot_content.document:
                    bot.send_document(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                      document=bot_msg.bot_content.document,
                                      reply_to_message_id=reply_to_msg_id)
        finally:
            if self.store.is_exist(ButtonItem.OPERATE_REPLY):
                self.end_message(bot, update)

    def response_chat_enter(self, bot, update):
        self.logger.debug('response_chat_enter !')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item)

    def handle_callback(self, bot, query, button_item):
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_DIALOG:
            if button_operate == ButtonItem.OPERATE_EXIT:
                self.end_conversation(bot, query)
            if button_operate == ButtonItem.OPERATE_ENTER:
                self.start_conversation(bot, query, item_id)
            if button_operate == ButtonItem.OPERATE_REPLY:
                self.reply_message(bot, query, item_id)

    def start_conversation(self, bot, query, room_id):
        """
        Here use ButtonItem.OPERATE_ENTER as the key of chat_data
        :param bot:
        :param query:
        :param room_id:
        :param chat_data:
        :return:
        """
        self.store.set(ButtonItem.OPERATE_ENTER, room_id)
        text = "进入房间: {}".format(room_id)
        bot.send_message(chat_id=application.ADMINS[0], text=text)

    def end_conversation(self, bot, update):
        if self.store.is_exist(ButtonItem.OPERATE_ENTER):
            self.logger.debug("退出房间: %s", self.store.get(ButtonItem.OPERATE_ENTER))
            text = "退出房间: {}".format(self.store.get(ButtonItem.OPERATE_ENTER))
            bot.send_message(chat_id=application.ADMINS[0], text=text)
            self.store.del_data(ButtonItem.OPERATE_ENTER)
        else:
            text = "已退出全部房间"
            bot.send_message(chat_id=application.ADMINS[0], text=text)
        self.store.clear_data()

    def reply_message(self, bot, query, msg_id):
        self.store.set(ButtonItem.OPERATE_REPLY, msg_id)
        text = "回复消息: {}".format(msg_id)
        bot.send_message(chat_id=application.ADMINS[0], text=text)

    def end_message(self, bot, update):
        self.logger.debug("结束回复: %s", self.store.get(ButtonItem.OPERATE_REPLY))
        text = "结束回复: {}".format(self.store.get(ButtonItem.OPERATE_REPLY))
        bot.send_message(chat_id=application.ADMINS[0], text=text)
        self.store.del_data(ButtonItem.OPERATE_REPLY)
