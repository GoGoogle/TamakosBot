import logging

import telegram
from telegram import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters

from service import netease

logger = logging.getLogger(__name__)


def start_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='こんにちは')


def help_command(bot, update):
    text = '**使用示例**: ' \
           '查询 => 输入 `音乐 <歌曲名字>` / ' \
           '歌单 => 複製你的歌單鏈接 / ' \
           '排行榜 => 比如 5sing 原创排行榜，输入 `5SING YC TOP`\n'
    bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def netease_command(bot, update, args):
    key_word = ' '.join(args[:])
    netease.search_music(bot, update, key_word)


# @run_async
# def sing5_command(bot, update, args):
#     sing5.search_music(bot, update, args)


def unknown_command(bot, update):
    if update.message.chat.type not in (Chat.GROUP, Chat.SUPERGROUP, Chat.CHANNEL):
        update.message.reply_text(text="肥腸抱歉..暫時不支持該口令")


def handler_commands(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('music', netease_command, pass_args=True))

    # dispatcher.add_handler(CommandHandler('5sing', sing5_command, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
