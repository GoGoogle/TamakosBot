import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from entity.bot_telegram import ButtonItem
from module.kugouz import kugou
from module.neteasz import netease
from module.qqz import qq
from module.recordz import record
from module.sing5z import sing5
from module.xiamiz import xiami
from util import telegram_util


class Modez(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Modez, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.m_name = 'mode'
        self.netease = netease.Netease()
        self.kugou = kugou.Kugou()
        self.sing5 = sing5.Sing5z()
        self.xiami = xiami.Xiami()
        self.qq = qq.Qqz()
        self.record = record.Recordz()
        self.common_mode = 'common'

    def produce_mode_board(self, user_data):
        self.logger.info("produce_mode_board")

        msg_mode = "模式选择"

        button_list = [
            [InlineKeyboardButton(
                text='酷狗音乐',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.kugou.m_name).dump_json()
            )],
            [InlineKeyboardButton(
                text='腾讯音乐',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.qq.m_name).dump_json()
            )],
            [InlineKeyboardButton(
                text='网易音乐',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.netease.m_name).dump_json()
            )],
            [InlineKeyboardButton(
                text='虾米音乐',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.xiami.m_name).dump_json()
            )],
            [InlineKeyboardButton(
                text='音乐排行',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.sing5.m_name).dump_json()
            )],
            [InlineKeyboardButton(
                text='记录模式',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.record.m_name).dump_json()
            )],
            [InlineKeyboardButton(
                text='普通模式',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_SEND,
                                         self.common_mode).dump_json()
            )],
            [InlineKeyboardButton(
                text='撤销显示',
                callback_data=ButtonItem(self.m_name, ButtonItem.TYPE_MODE, ButtonItem.OPERATE_CANCEL).dump_json()
            )]
        ]

        markup = InlineKeyboardMarkup(button_list, one_time_keyboard=True)
        return {"text": msg_mode, "markup": markup}

    def show_mode_board(self, bot, update, user_data):
        panel = self.produce_mode_board(user_data)
        update.message.reply_text(text=panel["text"], reply_markup=panel["markup"])

    def toggle_mode(self, bot, update, user_data):
        self.logger.info('response_toggle_mode !')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_MODE:
            if button_operate == ButtonItem.OPERATE_SEND:
                if item_id == self.common_mode:
                    if user_data.get(self.m_name):
                        del user_data[self.m_name]
                        user_data.clear()
                        bot.answerCallbackQuery(query.id, text="普通模式切换成功", show_alert=False)
                    bot.answerCallbackQuery(query.id, text="当前模式已为普通模式", show_alert=False)
                if item_id == self.sing5.m_name:
                    user_data[self.m_name] = item_id
                    bot.answerCallbackQuery(query.id, text="排行模式切换成功", show_alert=False)
                    reply_keyboard = [['原创排行', '翻唱排行'], ['新歌推荐', '其它']]
                    markup = ReplyKeyboardMarkup(reply_keyboard)
                    bot.send_message(chat_id=query.message.chat.id, text="请选择分类", reply_markup=markup,
                                     one_time_keyboard=True)
                else:
                    user_data[self.m_name] = item_id
                    bot.answerCallbackQuery(query.id, text="模式已切换", show_alert=False)
            if button_operate == ButtonItem.OPERATE_CANCEL:
                telegram_util.selector_cancel(bot, query)
