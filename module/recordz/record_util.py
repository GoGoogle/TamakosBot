import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from entity.bot_telegram import ButtonItem


class Utilz(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def produce_record_panel(self, bot_msg, module_name, chat_data):
        self.logger.info("produce_record_panel")

        if chat_data.get(ButtonItem.OPERATE_ENTER):
            msg_chat = "新消息！ 当前房间: `{0}` \n-------------\n房间:  {1} (chat_id:  {2})\n用户:  {3} (user_id: {4})\n" \
                       "信息:  {5} (msg_id:  {6})".format(chat_data.get(ButtonItem.OPERATE_ENTER),
                                                        bot_msg.bot_chat.chat_title, bot_msg.bot_chat.chat_id,
                                                        bot_msg.bot_user.first_name, bot_msg.bot_user.user_id,
                                                        bot_msg.bot_content.text,
                                                        bot_msg.msg_id
                                                        )
            button_list = [
                [InlineKeyboardButton(
                    text='回复信息',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_DIALOG, ButtonItem.OPERATE_REPLY,
                                             bot_msg.msg_id).dump_json()
                )],
                [InlineKeyboardButton(
                    text='退出当前',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_DIALOG, ButtonItem.OPERATE_EXIT).dump_json()
                )]
            ]
        else:
            msg_chat = "新消息{0}！\n-------------\n房间:  {1} (chat_id:  {2})\n用户:  {3} (user_id: {4})\n" \
                       "信息:  {5} (msg_id:  {6})".format('', bot_msg.bot_chat.chat_title, bot_msg.bot_chat.chat_id,
                                                        bot_msg.bot_user.first_name, bot_msg.bot_user.user_id,
                                                        bot_msg.bot_content.text,
                                                        bot_msg.msg_id
                                                        )
            button_list = [
                [InlineKeyboardButton(
                    text='进入房间',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_DIALOG, ButtonItem.OPERATE_ENTER,
                                             bot_msg.bot_chat.chat_id).dump_json()
                )],
                [InlineKeyboardButton(
                    text='退出房间',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_DIALOG, ButtonItem.OPERATE_EXIT).dump_json()
                )]
            ]
        markup = InlineKeyboardMarkup(button_list, one_time_keyboard=True)

        return {"text": msg_chat, "markup": markup}
