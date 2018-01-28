import logging
import os

import telegram
from telegram.error import BadRequest, ChatMigrated, TelegramError, Unauthorized

from utils import telegram


class Adminz(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Adminz, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def manage_bot(self, bot, update, payload):
        command = payload[0]
        params = payload[1:]
        self.logger.debug("command %s, params %s", command, params)
        try:
            self.command_analyzing(bot, update, command, params)
        except BadRequest and ChatMigrated:
            self.logger.error('命令提交错误', exc_info=True)
        except TelegramError and Unauthorized:
            self.logger.error('telegram 出错', exc_info=True)

    @staticmethod
    def command_analyzing(bot, update, command, params):
        if command == "add_listen":
            pass
        if command == "close_listen":
            pass
        if command == "delete_msg":
            bot.delete_message(chat_id=params[0], message_id=params[1])
        if command == "edit_msg":
            bot.edit_message_text(chat_id=params[0], message_id=params[1], text=params[2])
        if command == "exit":
            flag = bot.leave_chat(chat_id=params[0])
            if flag:
                update.message.reply_text("退出成功！")
            else:
                update.message.reply_text("退出失败！")
        if command == "log":
            cfg = ConfigParser()
            cfg.read('config/custom.ini')
            log_file = cfg.get('other', 'log_file')

            log_path = os.path.join(os.getcwd(), log_file)
            bot.send_document(chat_id=update.message.chat.id,
                              document=open(log_path, 'rb'))
        if command == "help":
            update.message.reply_text(
                "命令列表:\n`add_listen, close_listen,\n"
                "delete_msg(chat_id, message_id),\n"
                "edit_msg(chat_id, message_id, text)\n"
                "exit(chat_id)` ",
                parse_mode=telegram.ParseMode.MARKDOWN)
