import logging

from entity.bot_telegram import BotMessage
from module.linkz import link_util


class Link(object):
    m_name = 'my_link'
    name = "⦿"
    y_name = "ⓒ"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.utilz = link_util.Util()

    def step_link_pool(self, bot, update):
        query = update.callback_query
        self.logger.debug("{} has stepped into link pool".format(query.from_user))

        my_id = query.from_user.id
        my_message_id = query.message.message_id

        self.utilz.line_up(bot, my_id, my_message_id)

        self.utilz.fetch_box(my_id, bot)

    def leave_link_pool(self, bot, update):
        query = update.callback_query
        self.utilz.update_status(self.utilz.Unlink, query.from_user.id)
        self.utilz.observer_status(bot)  # 自动更新状态

    def chat_with_partner(self, bot, update):
        user = self.utilz.get_status(update.message.from_user.id)
        if user and user["status"] == self.utilz.Linking:
            partner_id = user["your_id"]
            bot_msg = BotMessage.get_botmsg(update['message'])
            if bot_msg.bot_content.text:
                bot.send_message(chat_id=partner_id, text=bot_msg.bot_content.text)
            if bot_msg.bot_content.picture.sticker:
                bot.send_sticker(chat_id=partner_id, sticker=bot_msg.bot_content.picture.sticker)
            if bot_msg.bot_content.photo:
                bot.send_photo(chat_id=partner_id, photo=bot_msg.bot_content.photo)
            if bot_msg.bot_content.audio:
                bot.send_audio(chat_id=partner_id, audio=bot_msg.bot_content.audio)
            if bot_msg.bot_content.video:
                bot.send_video(chat_id=partner_id, video=bot_msg.bot_content.video)
            if bot_msg.bot_content.document:
                bot.send_document(chat_id=partner_id, document=bot_msg.bot_content.document)
