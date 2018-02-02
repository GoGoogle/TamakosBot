import logging

from entity.bot_mode import Mode
from entity.bot_telegram import ButtonItem
from module.linkz import link
from module.modez import mode_util


class Modez(object):
    m_name = 'mode'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Modez, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.util = mode_util.Util()
        self.my_link = link.Link()

    def show_mode_board(self, bot, update, user_data):
        cur_mode_id = user_data.get(self.m_name)
        if cur_mode_id:
            sel_mode = Mode.get_mode(cur_mode_id)
        else:
            sel_mode = Mode("pear", "选择")
        sel_modelist = self.util.make_modelist()
        panel = self.util.produce_mode_board(self.m_name, sel_mode, sel_modelist)
        bot.send_message(chat_id=update.message.chat.id, text=panel["text"], reply_markup=panel["markup"])

    def toggle_mode(self, bot, update, user_data):
        self.logger.debug('response_toggle_mode..')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_MODE and button_operate == ButtonItem.OPERATE_SEND \
                and user_data.get(self.m_name) != item_id:
            if item_id == self.my_link.m_name:  # unique handle for my link
                user_data[self.m_name] = item_id
                self.my_link.step_link_pool(bot, update)
            else:
                if user_data.get(self.m_name) == self.my_link.m_name:
                    self.my_link.leave_link_pool(bot, update)  # leave the link pool

                sel_mode = Mode.get_mode(item_id)
                sel_modelist = self.util.make_modelist()
                panel = self.util.produce_mode_board(self.m_name, sel_mode, sel_modelist)
                query.message.edit_text(text=panel["text"], reply_markup=panel["markup"])

                user_data[self.m_name] = item_id
                bot.answerCallbackQuery(query.id, text="已切换", show_alert=False)
