import logging

from telegram.ext import CommandHandler, MessageHandler, Filters, run_async

from service.dispatcher import netease

logger = logging.getLogger(__name__)


def start_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='你好')


def help_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='无可奉告？')


@run_async
def netease_command(bot, update, args):
    netease.search_music(bot, update, args)


# @run_async
# def sing5_command(bot, update, args):
#     sing5.search_music(bot, update, args)


@run_async
def history_command(bot, update, args):
    netease.trace_music(bot, update, args)


def unknown_command(bot, update):
    update.message.reply_text(text="格子表示无法找到此命令。")


def handler_commands(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('music', netease_command, pass_args=True))
    # dispatcher.add_handler(CommandHandler('5sing', sing5_command, pass_args=True))
    dispatcher.add_handler(CommandHandler('history', history_command, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
