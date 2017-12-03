import logging
import telegram

from telegram import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters
from module.neteasz import netease
from module.managez import manage
from util.telegram_util import restricted


class Commands(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.netease = netease.Netease()
        self.manage = manage.Adminz()

    @staticmethod
    def start_command(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='你好呀')

    @staticmethod
    def help_command(bot, update):
        text = '暂时无帮助信息。'
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

    def netease_command(self, bot, update, args):
        key_word = ' '.join(args[:])
        self.netease.search_music(bot, update, key_word)

    def unknown_command(self, bot, update):
        if update.message.chat.type not in (Chat.GROUP, Chat.SUPERGROUP, Chat.CHANNEL):
            self.logger.error('Unsupported command!')
            update.message.reply_text(text="肥腸抱歉..暫時不支持該口令")

    @restricted
    def manage_bot(self, bot, update, args):
        self.manage.manage_bot(bot, update, args)

    def handler_commands(self, dispatcher):
        dispatcher.add_handler(CommandHandler('start', self.start_command))
        dispatcher.add_handler(CommandHandler('help', self.help_command))
        dispatcher.add_handler(CommandHandler('music', self.netease_command, pass_args=True))
        dispatcher.add_handler(CommandHandler('super', self.manage_bot, pass_args=True))
        dispatcher.add_handler(MessageHandler(Filters.command, self.unknown_command))
