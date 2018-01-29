import logging

from entity.bot_mode import Mode
from entity.bot_telegram import ButtonItem
from module.animez import anime
from module.linkz import link
from module.kugouz import kugou
from module.modez import mode_util
from module.neteasz import netease
from module.qqz import qq


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
        self.dialog_module_name = link.Link.m_name

    def show_mode_board(self, bot, update, userdata):
        # TODO acquire from database
        sel_mode = Mode(self.dialog_module_name, "ⓒ")
        sel_modelist = self.util.make_modelist()
        panel = self.util.produce_mode_board(self.m_name, sel_mode, sel_modelist)
        bot.send_message(chat_id=update.message.chat.id, text=panel["text"], reply_markup=panel["markup"])

    def toggle_mode(self, bot, update, user_data):
        self.logger.debug('response_toggle_mode..')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_MODE:
            if button_operate == ButtonItem.OPERATE_SEND:
                sel_mode = Mode.get_mode(item_id)
                sel_modelist = self.util.make_modelist()
                panel = self.util.produce_mode_board(self.m_name, sel_mode, sel_modelist)
                query.message.edit_text(text=panel["text"], reply_markup=panel["markup"])

                user_data[self.m_name] = item_id
                bot.answerCallbackQuery(query.id, text="已切换", show_alert=False)

