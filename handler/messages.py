import logging
import random

from telegram.ext import RegexHandler

logger = logging.getLogger(__name__)


def hi_message(bot, update):
    text = '{0}, {1}'.format(update.message.text, update.message.from_user.first_name)
    logger.info('hi: {}'.format(text))
    bot.send_message(chat_id=update.message.chat_id, text=text)


def bye_message(bot, update):
    text = '很惭愧，就做了一点微小的工作，谢谢大家'
    logger.info('bye: {}'.format(text))
    bot.send_message(chat_id=update.message.chat_id, text=text)


def tks_message(bot, update):
    ha_list = [
        '你们给我搞的这本东西，excited!',
        '我说另请高明吧！我实在也不是谦虚',
        '这个效率，efficiency',
        '我今天是作为一个长者来跟你们讲的',
        '我有必要告诉你们一点人参的经验',
    ]
    text = ha_list[random.randint(0, len(ha_list) - 1)]
    logger.info('bye: {}'.format(text))
    bot.send_message(chat_id=update.message.chat_id, text=text)


def handler_messages(dispatcher):
    dispatcher.add_handler(RegexHandler(r'^(Hi|你好)$', hi_message))
    dispatcher.add_handler(RegexHandler(r'.*bye$', bye_message))
    dispatcher.add_handler(RegexHandler(r'.*naive.*', tks_message))
