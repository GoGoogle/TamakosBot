import logging
from util import telegram_util

from telegram import TelegramError

from entity.bot_telegram import ButtonItem
from module.animez import anime
from module.kugouz import kugou
from module.modez import mode_util
from module.neteasz import netease
from module.qqz import qq
from module.recordz import record
from util import telegram_util


class Modez(object):
    m_name = 'mode'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Modez, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.util = mode_util.Util()
        self.netease_module_name = netease.Netease.m_name
        self.kugou_module_name = kugou.Kugou.m_name
        self.qq_module_name = qq.Qqz.m_name
        self.anime_module_name = anime.Anime.m_name
        self.common_module_name = "common_m"
        self.center_module_name = "center_m"
        self.record_module_name = record.Recordz.m_name
        self.record_store = record.Recordz.store

        cfg = telegram_util.get_config()
        self.admin_room = cfg.get('base', 'admin_room')

    def show_mode_board(self, bot, update, user_data):
        last_module = {"title": "ⓒ 普通", "name": self.common_module_name}
        user_data[self.m_name] = last_module["name"]
        panel = self.util.produce_mode_board(last_module["name"], last_module, self.m_name)
        bot.send_message(chat_id=update.message.chat.id, text=panel["text"], reply_markup=panel["markup"])

    def toggle_mode(self, bot, update, user_data):
        self.logger.debug('response_toggle_mode..')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_MODE:
            if button_operate == ButtonItem.OPERATE_CANCEL:
                telegram_util.selector_cancel(bot, query)
            if button_operate == ButtonItem.OPERATE_SEND:
                try:
                    if item_id in [self.common_module_name, self.record_module_name, self.center_module_name]:
                        last_module = None
                        chat_id = update.effective_chat.id
                        # Judge weather use_id  in Admins Chat
                        if chat_id != self.admin_room:
                            if item_id == self.common_module_name:
                                last_module = {"title": "⦿ 对话", "name": self.record_module_name}
                            if item_id == self.record_module_name:
                                last_module = {"title": "ⓒ 普通", "name": self.common_module_name}
                                self.exit_chatroom(bot, update)
                        else:
                            if item_id == self.common_module_name:
                                last_module = {"title": "⦿ 回复", "name": self.center_module_name}
                            if item_id == self.center_module_name:
                                last_module = {"title": "ⓒ 普通", "name": self.common_module_name}
                                self.exit_chatroom(bot, update)
                        user_data[self.m_name] = last_module["name"]
                        panel = self.util.produce_mode_board(last_module["name"], last_module, self.m_name)
                        query.message.edit_text(text=panel['text'], reply_markup=panel['markup'])
                    else:
                        if user_data.get(self.m_name) != item_id:
                            if user_data.get(self.m_name) in [self.record_module_name, self.center_module_name]:
                                self.exit_chatroom(bot, update)
                            last_module = {"title": "ⓒ 普通", "name": self.common_module_name}
                            panel = self.util.produce_mode_board(item_id, last_module, self.m_name)
                            query.message.edit_text(text=panel['text'], reply_markup=panel['markup'])
                        user_data[self.m_name] = item_id
                        bot.answerCallbackQuery(query.id, text="已切换", show_alert=False)
                except TelegramError as e:
                    self.logger.debug("This often happen when it has different sessions")

    def exit_chatroom(self, bot, update):
        query = update.callback_query

        if self.record_store.get(ButtonItem.OPERATE_ENTER):
            self.record_store.clear_data()
            text = "已中断对话"
            bot.answer_callback_query(query.id, text=text, show_alert=False)

            chat_id = update.effective_chat.id
            if chat_id != self.admin_room:
                text = "对方已经手动中断当前对话"
                bot.send_message(chat_id=self.admin_room, text=text)
