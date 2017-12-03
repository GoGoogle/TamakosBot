import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_telegram import ButtonItem


class Utilz(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def produce_record_panel(self, bot_msg, module_name):
        self.logger.info("produce_record_panel")

        msg_chat = "新消息！\n-------------\n房间:  {0} (chat_id:  {1})\n用户:  {2} (user_id: {3})\n" \
                   "信息:  {4} (msg_id:  {5})".format(bot_msg.bot_chat.chat_title, bot_msg.bot_chat.chat_id,
                                                    bot_msg.bot_user.first_name, bot_msg.bot_user.user_id,
                                                    bot_msg.bot_content.text,
                                                    bot_msg.msg_id
                                                    )
        button_list = [
            [InlineKeyboardButton(
                text='进入房间',
                callback_data=ButtonItem(module_name, ButtonItem.TYPE_DIALOG, ButtonItem.OPERATE_SEND,
                                         bot_msg.bot_chat.chat_id).dump_json()
            )],
            [InlineKeyboardButton(
                text='退出房间',
                callback_data=ButtonItem(module_name, ButtonItem.TYPE_DIALOG, ButtonItem.OPERATE_CANCEL).dump_json()
            )]
        ]
        markup = InlineKeyboardMarkup(button_list, one_time_keyboard=True)

        return {"text": msg_chat, "markup": markup}
