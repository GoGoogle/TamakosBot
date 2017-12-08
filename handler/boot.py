import logging

from telegram.ext import CommandHandler

from module.managez import manage
from module.modez import mode
from util.telegram_util import restricted


class Startup(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.manage = manage.Adminz()
        self.mode = mode.Modez()

    def start_command(self, bot, update, user_data):
        """
        Show the setting page board
        :param bot:
        :param update:
        :param user_data: store the user config info
        :return:
        """
        self.mode.show_mode_board(bot, update, user_data)

    @restricted
    def manage_bot(self, bot, update, args):
        self.manage.manage_bot(bot, update, args)

    def handler_startup(self, dispatcher):
        dispatcher.add_handler(CommandHandler(['start', 'mode', 'help'], self.start_command, pass_user_data=True))
        dispatcher.add_handler(CommandHandler('super', self.manage_bot, pass_args=True))
