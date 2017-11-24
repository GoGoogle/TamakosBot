import logging
import random

from telegram.ext import RegexHandler, CommandHandler, ConversationHandler

logger = logging.getLogger(__name__)

INPUT_USERNAME, INPUT_PASSWORD, CHECK_LOGIN_INFO = range(3)


def hi_message(bot, update):
    text = '{0}, {1}'.format(update.message.text, update.message.from_user.first_name)
    logger.info('hi: {}'.format(text))
    bot.send_message(chat_id=update.message.chat_id, text=text)


def bye_message(bot, update):
    text = '拜拜'
    logger.info('bye: {}'.format(text))
    bot.send_message(chat_id=update.message.chat_id, text=text)


def tks_message(bot, update):
    ha_list = [
        '你们给我搞的这本东西，excited!',
        '这个效率，efficiency',
        '完全没有任何这个意思',
        '我今天算是得罪了你们一下！'
    ]
    text = ha_list[random.randint(0, len(ha_list) - 1)]
    logger.info('bye: {}'.format(text))
    bot.send_message(chat_id=update.message.chat_id, text=text)


def start_login(bot, update):
    pass


def input_username(bot, update):
    pass


def input_password(bot, update):
    pass


def handle_login_information(bot, update):
    pass


def end_login(bot, update):
    pass


def cancel_conv(bot, update):
    pass


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('login', start_login)],
    states={
        INPUT_USERNAME: [],
        INPUT_PASSWORD: [],
        # 判断用户密码是否正确？
        CHECK_LOGIN_INFO: []
    },
    fallbacks=[RegexHandler('^cancel$', cancel_conv, pass_user_data=True)]
)


def handler_messages(dispatcher):
    dispatcher.add_handler(RegexHandler(r'^(Hi|你好)$', hi_message))
    dispatcher.add_handler(RegexHandler(r'.*有事$', bye_message))
    dispatcher.add_handler(RegexHandler(r'.*曰..曰.*', tks_message))
    dispatcher.add_handler(conv_handler)
