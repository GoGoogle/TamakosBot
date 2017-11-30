import logging
import telegram

from telegram import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters
from module.neteasz import netease


class Commands(object):
    def __init__(self):
        self.netease = netease.Netease()
        self.logger = logging.getLogger(__name__)

    def start_command(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='你好呀')

    def help_command(self, bot, update):
        text = '暂时无帮助信息。'
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

    def netease_command(self, bot, update, args):
        key_word = ' '.join(args[:])
        self.netease.search_music(bot, update, key_word)

    # @run_async
    # def sing5_command(bot, update, args):
    #     sing5.search_music(bot, update, args)

    def unknown_command(self, bot, update):
        if update.message.chat.type not in (Chat.GROUP, Chat.SUPERGROUP, Chat.CHANNEL):
            self.logger.error('Unsupported command!')
            update.message.reply_text(text="肥腸抱歉..暫時不支持該口令")

    def handler_commands(self, dispatcher):
        dispatcher.add_handler(CommandHandler('entrance', self.start_command))
        dispatcher.add_handler(CommandHandler('help', self.help_command))
        dispatcher.add_handler(CommandHandler('music', self.netease_command, pass_args=True))

        # dispatcher.add_handler(CommandHandler('5sing', sing5_command, pass_args=True))
        dispatcher.add_handler(MessageHandler(Filters.command, self.unknown_command))
