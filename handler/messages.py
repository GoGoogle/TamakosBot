import logging
import random

from telegram.ext import RegexHandler, CommandHandler, ConversationHandler


class Message(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    INPUT_USERNAME, INPUT_PASSWORD, CHECK_LOGIN_INFO = range(3)

    @staticmethod
    def hi_message(bot, update):
        text = '{0}, {1}'.format(update.message.text, update.message.from_user.first_name)
        bot.send_message(chat_id=update.message.chat_id, text=text)

    @staticmethod
    def bye_message(bot, update):
        text = '我今天算是得罪了你们一下！'
        bot.send_message(chat_id=update.message.chat_id, text=text)

    @staticmethod
    def tks_message(bot, update):
        ha_list = [
            '你们给我搞的这本东西，excited!',
            '这个效率，efficiency',
            '完全没有任何这个意思',
            '我今天算是得罪了你们一下！'
        ]
        text = ha_list[random.randint(0, len(ha_list) - 1)]
        bot.send_message(chat_id=update.message.chat_id, text=text)

    def start_login(self, bot, update):
        pass

    def input_username(self, bot, update):
        pass

    def input_password(self, bot, update):
        pass

    def handle_login_information(self, bot, update):
        pass

    def end_login(self, bot, update):
        pass

    def cancel_conv(self, bot, update):
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

    def handler_messages(self, dispatcher):
        dispatcher.add_handler(RegexHandler(r'.*来了.*', self.hi_message))
        dispatcher.add_handler(RegexHandler(r'.*告辞.*', self.bye_message))
        dispatcher.add_handler(RegexHandler(r'.*(得罪|你们|效率|完全|我).*', self.tks_message))
        dispatcher.add_handler(self.conv_handler)
