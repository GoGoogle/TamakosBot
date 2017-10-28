import logging

from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from service.netease import netease

logger = logging.getLogger(__name__)


def start_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='emm..')


def help_command(bot, update):
    update.message.reply_text('Here is the help message:')


def netease_command(bot, update, args):
    netease.get_music(bot, update, args)


def unknown_command(bot, update):
    update.message.reply_text(text="Sorry, I didn't understand that command.")


def handler_commands(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('netease', netease_command, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
