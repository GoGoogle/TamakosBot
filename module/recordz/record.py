import logging

from config import application
from entity.bot_telegram import BotMessage, ButtonItem
from module.recordz import record_util
from util import telegram_util


class Recordz(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.m_name = "recordz"
        self.util = record_util.Utilz()

    def record_msg(self, bot, update, user_data):
        bot_msg = BotMessage.get_botmsg(update['message'])

        if bot_msg.bot_chat.chat_id != application.ADMINS[0]:
            self.logger.info('msg send success!')
            panel = self.util.produce_record_panel(bot_msg, self.m_name, user_data)
            plain_msg = bot.send_message(chat_id=application.ADMINS[0], text=panel["text"],
                                         reply_markup=panel["markup"])
            if bot_msg.bot_content.picture.sticker:
                bot.send_sticker(chat_id=application.ADMINS[0], sticker=bot_msg.bot_content.picture.sticker,
                                 reply_to_message_id=plain_msg.message_id)
        else:
            try:
                if ButtonItem.OPERATE_REPLY in user_data:
                    reply_to_msg_id = user_data.get(ButtonItem.OPERATE_REPLY)
                else:
                    reply_to_msg_id = None
                if ButtonItem.OPERATE_ENTER in user_data:
                    if bot_msg.bot_content.text:
                        bot.send_message(chat_id=user_data.get(ButtonItem.OPERATE_ENTER),
                                         text=bot_msg.bot_content.text,
                                         reply_to_message_id=reply_to_msg_id)
                    if bot_msg.bot_content.picture.sticker:
                        bot.send_sticker(chat_id=user_data.get(ButtonItem.OPERATE_ENTER),
                                         sticker=bot_msg.bot_content.picture.sticker,
                                         reply_to_message_id=reply_to_msg_id)
                    if bot_msg.bot_content.photo:
                        bot.send_photo(chat_id=user_data.get(ButtonItem.OPERATE_ENTER),
                                       photo=bot_msg.bot_content.photo,
                                       reply_to_message_id=reply_to_msg_id)
                    if bot_msg.bot_content.audio:
                        bot.send_audio(chat_id=user_data.get(ButtonItem.OPERATE_ENTER),
                                       audio=bot_msg.bot_content.audio,
                                       reply_to_message_id=reply_to_msg_id)
                    if bot_msg.bot_content.video:
                        bot.send_video(chat_id=user_data.get(ButtonItem.OPERATE_ENTER),
                                       video=bot_msg.bot_content.video,
                                       reply_to_message_id=reply_to_msg_id)
                    if bot_msg.bot_content.document:
                        bot.send_document(chat_id=user_data.get(ButtonItem.OPERATE_ENTER),
                                          document=bot_msg.bot_content.document,
                                          reply_to_message_id=reply_to_msg_id)
            finally:
                if ButtonItem.OPERATE_REPLY in user_data:
                    self.end_message(bot, update, user_data)

    def response_chat_enter(self, bot, update, user_data):
        self.logger.info('response_chat_enter !')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item, user_data)

    def handle_callback(self, bot, query, button_item, user_data):
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_DIALOG:
            if button_operate == ButtonItem.OPERATE_EXIT:
                self.end_conversation(bot, query, user_data)
            if button_operate == ButtonItem.OPERATE_ENTER:
                self.start_conversation(bot, query, item_id, user_data)
            if button_operate == ButtonItem.OPERATE_REPLY:
                self.reply_message(bot, query, item_id, user_data)

    def start_conversation(self, bot, query, room_id, user_data):
        """
        Here use ButtonItem.OPERATE_ENTER as the key of user_data
        :param bot:
        :param query:
        :param room_id:
        :param user_data:
        :return:
        """
        user_data[ButtonItem.OPERATE_ENTER] = room_id
        text = "进入房间: {}".format(room_id)
        bot.send_message(chat_id=application.ADMINS[0], text=text)

    def end_conversation(self, bot, update, user_data):
        if ButtonItem.OPERATE_ENTER in user_data:
            self.logger.info("退出房间: %s", user_data[ButtonItem.OPERATE_ENTER])
            text = "退出房间: {}".format(user_data[ButtonItem.OPERATE_ENTER])
            bot.send_message(chat_id=application.ADMINS[0], text=text)
            del user_data[ButtonItem.OPERATE_ENTER]
        user_data.clear()

    def reply_message(self, bot, query, msg_id, user_data):
        user_data[ButtonItem.OPERATE_REPLY] = msg_id
        text = "回复消息: {}".format(msg_id)
        bot.send_message(chat_id=application.ADMINS[0], text=text)

    def end_message(self, bot, update, user_data):
        self.logger.info("结束回复: %s", user_data[ButtonItem.OPERATE_REPLY])
        del user_data[ButtonItem.OPERATE_REPLY]
