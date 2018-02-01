import logging
from queue import Queue

from entity.bot_telegram import BotMessage
from module.linkz import link_util


class Link(object):
    m_name = 'my_link'
    name = "⦿"
    y_name = "ⓒ"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.utilz = link_util.Util()
        self.handout_queue = Queue()
        self.direct_queue = Queue()

    def step_link_pool(self, bot, update, user_data):
        self.logger.info("step link pool")
        query = update.callback_query

        my_id = query.from_user.id
        my_message_id = query.message.message_id

        self.utilz.update_reply_board(bot, my_id, my_message_id, "~")

        # 初始化；排队
        self.utilz.line_up(my_id, my_message_id)

        # 从箱子里取票
        self.utilz.fetch_box(my_id)

    def chat_with_partner(self, bot, update):
        self.logger.debug("chat_with_partner")
        partner_id = 2323
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
