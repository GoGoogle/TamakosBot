import logging

from telegram.ext import RegexHandler

logger = logging.getLogger(__name__)


def hi_message(bot, update):
    text = '{0}, {1}'.format(update.message.text, update.message.from_user.first_name)
    logger.info('hi: {}'.format(text))
    update.message.reply_text(text=text)


def bye_message(bot, update):
    text = 'Bye, Hope to see you around again!'
    logger.info('bye: {}'.format(text))
    update.message.reply_text(text=text)


def handler_messages(dispatcher):
    dispatcher.add_handler(RegexHandler(r'^(Hi|你好)$', hi_message))
    dispatcher.add_handler(RegexHandler(r'.*bye$', bye_message))
