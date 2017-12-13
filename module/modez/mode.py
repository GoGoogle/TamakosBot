import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from config import application
from entity.bot_telegram import ButtonItem
from module.animez import anime
from module.kugouz import kugou
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
        self.netease_module_name = netease.Netease.m_name
        self.kugou_module_name = kugou.Kugou.m_name
        self.qq_module_name = qq.Qqz.m_name
        self.anime_module_name = anime.Anime.m_name
        self.record_module_name = record.Recordz.m_name
        self.common_mode = "common"

    def produce_mode_board(self, bot, update, user_data):
        self.logger.debug("produce_mode_board")

        if update.effective_user.id in application.ADMINS:
            monitor_action = self.record_module_name
        else:
            monitor_action = self.common_mode

        msg_mode = "模式选择"

        button_list = [
            [
                InlineKeyboardButton(
                    text='酷狗音乐',
                    callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.kugou_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text='腾讯音乐',
                    callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.qq_module_name).dump_json()
                )
            ],
            [
                InlineKeyboardButton(
                    text='网易音乐',
                    callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.netease_module_name).dump_json()
                ),
                InlineKeyboardButton(
                    text='动画索引',
                    callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                             self.anime_module_name).dump_json()
                )
            ],
            [InlineKeyboardButton(
                text='回应模式',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         monitor_action).dump_json()
            )]
        ]

        markup = InlineKeyboardMarkup(button_list, one_time_keyboard=True)
        return {"text": msg_mode, "markup": markup}

    def show_mode_board(self, bot, update, user_data):
        panel = self.produce_mode_board(bot, update, user_data)
        update.message.reply_text(text=panel["text"], reply_markup=panel["markup"])

    def toggle_mode(self, bot, update, user_data):
        self.logger.debug('response_toggle_mode..')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_MODE:
            if button_operate == ButtonItem.OPERATE_SEND:
                user_data[self.m_name] = item_id
                bot.answerCallbackQuery(query.id, text="模式已切换", show_alert=False)
            if button_operate == ButtonItem.OPERATE_CANCEL:
                telegram_util.selector_cancel(bot, query)
