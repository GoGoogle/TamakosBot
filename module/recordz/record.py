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
            panel = self.util.produce_record_panel(bot_msg, self.m_name)
            plain_msg = bot.send_message(chat_id=application.ADMINS[0], text=panel["text"],
                                         reply_markup=panel["markup"])
            if bot_msg.bot_content.picture.sticker_id:
                bot.send_sticker(chat_id=application.ADMINS[0], sticker=bot_msg.bot_content.picture.sticker,
                                 reply_to_message_id=plain_msg.message_id)
        else:
            if self.m_name in user_data:
                if bot_msg.bot_content.text:
                    bot.send_message(chat_id=user_data.get(self.m_name), text=bot_msg.bot_content.text)
                if bot_msg.bot_content.picture.sticker:
                    bot.send_sticker(chat_id=user_data.get(self.m_name), sticker=bot_msg.bot_content.picture.sticker)
                if bot_msg.bot_content.photo:
                    bot.send_photo(chat_id=user_data.get(self.m_name), photo=bot_msg.bot_content.photo)
                if bot_msg.bot_content.audio:
                    bot.send_audio(chat_id=user_data.get(self.m_name), audio=bot_msg.bot_content.audio)
                if bot_msg.bot_content.video:
                    bot.send_video(chat_id=user_data.get(self.m_name), video=bot_msg.bot_content.video)
                if bot_msg.bot_content.document:
                    bot.send_document(chat_id=user_data.get(self.m_name), document=bot_msg.bot_content.document)

    def response_chat_enter(self, bot, update, user_data):
        self.logger.info('response_chat_enter !')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item, user_data)

    def handle_callback(self, bot, query, button_item, user_data):
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_DIALOG:
            if button_operate == ButtonItem.OPERATE_CANCEL:
                self.end_conversation(bot, query, user_data)
                telegram_util.selector_cancel(bot, query)
            if button_operate == ButtonItem.OPERATE_SEND:
                self.start_conversation(bot, query, item_id, user_data)

    def start_conversation(self, bot, query, room_id, user_data):
        user_data[self.m_name] = room_id
        text = "进入房间: {}".format(room_id)
        query.message.reply_text(text)

    def end_conversation(self, bot, update, user_data):
        self.logger.info("退出房间")

        if self.m_name in user_data:
            self.logger.info("退出房间: %s", user_data[self.m_name])
            text = "退出房间: {}".format(user_data[self.m_name])
            update.message.reply_text(text)
            del user_data[self.m_name]
        user_data.clear()
