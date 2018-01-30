import logging
from queue import Queue

from entity.bot_telegram import BotMessage
from module.linkz import link_util


class Link(object):
    m_name = 'my_link'

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.utilz = link_util.Util()
        self.match_group = {}  # 从匹配表中获取，不要从user_data获取。匹配表绑定 userid就可以了。
        self.handout_queue = Queue(1)

    def step_link_pool(self, bot, update, user_data):
        self.logger.debug("step link pool")
        query = update.callback_query
        self.handout_person(bot, query, user_data)

    def handout_person(self, bot, query, user_data):
        my_id = query.from_user["id"]
        if self.match_group.get(my_id):
            user_data["partner_id"] = self.match_group.get(my_id)
            self.match_group.pop(my_id)
            self.utilz.update_mode_board(query, "⦿")
            bot.answerCallbackQuery(query.id, text="Hi", show_alert=False)
        else:
            if self.handout_queue.empty():
                self.handout_queue.put(my_id)
                self.utilz.update_mode_board(query, "~")
                bot.answerCallbackQuery(query.id, text="Analyze", show_alert=False)
            else:
                your_id = self.handout_queue.get()
                if your_id != my_id:
                    self.match_group[your_id] = my_id
                    user_data["partner_id"] = your_id
                    self.utilz.update_mode_board(query, "⦿")
                    bot.answerCallbackQuery(query.id, text="Hi", show_alert=False)
                    self.handout_queue.task_done()
                else:
                    self.utilz.update_mode_board(query, "~")
                    bot.answerCallbackQuery(query.id, text="Analyze", show_alert=False)

    def chat_with_partner(self, bot, update, partner_id):
        self.logger.debug("chat with partner {}".format(partner_id))
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
