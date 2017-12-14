import logging

from config.application import ADMINS
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

    def show_mode_board(self, bot, update, user_data):
        last_module = {"title": "正常模式", "name": self.common_module_name}
        user_data[self.m_name] = last_module["name"]
        panel = self.util.produce_mode_board(last_module, self.m_name)
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
                if item_id in [self.common_module_name, self.record_module_name, self.center_module_name]:
                    last_module = None
                    chat_id = update.effective_chat.id
                    # Judge weather use_id  in Admins Chat
                    if chat_id != ADMINS[0]:
                        if item_id == self.common_module_name:
                            last_module = {"title": "⦿ 记录模式", "name": self.record_module_name}
                        if item_id == self.record_module_name:
                            last_module = {"title": "正常模式", "name": self.common_module_name}
                    else:
                        if item_id == self.common_module_name:
                            last_module = {"title": "⦿ 回复模式", "name": self.center_module_name}
                        if item_id == self.center_module_name:
                            last_module = {"title": "正常模式", "name": self.common_module_name}
                    user_data[self.m_name] = last_module["name"]
                    panel = self.util.produce_mode_board(last_module, self.m_name)
                    query.message.edit_text(text=panel['text'], reply_markup=panel['markup'])
                else:
                    last_module = {"title": "正常模式", "name": self.common_module_name}
                    panel = self.util.produce_mode_board(last_module, self.m_name)
                    query.message.edit_text(text=panel['text'], reply_markup=panel['markup'])

                    user_data[self.m_name] = item_id
                    bot.answerCallbackQuery(query.id, text="模式已切换", show_alert=False)
