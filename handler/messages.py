import logging
import re

from telegram.ext import RegexHandler

from service.dispatcher import netease

logger = logging.getLogger(__name__)


def hi_message(bot, update):
    text = '{0}, {1}'.format(update.message.text, update.message.from_user.first_name)
    logger.info('hi: {}'.format(text))
    update.message.reply_text(text=text)


def bye_message(bot, update):
    text = '白白'
    logger.info('bye: {}'.format(text))
    update.message.reply_text(text=text)


def response_netease_playlist(bot, update):
    playlist_id = re.search(r'http://music.163.com(/#)?/playlist/(\d*)', update.message.text).group(2)
    netease.response_playlist(bot, update, playlist_id)


def handler_messages(dispatcher):
    dispatcher.add_handler(RegexHandler(r'^(Hi|你好)$', hi_message))
    dispatcher.add_handler(RegexHandler(r'.*bye$', bye_message))
    dispatcher.add_handler(RegexHandler(r'.*http://music.163.com(/#)?/playlist/\d*.*', response_netease_playlist))
