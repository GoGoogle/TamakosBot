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

    def help_info(self, bot, update):
        self.logger.debug("send help info")
        text = "主要模块介绍：\n\n1~3 音乐模块：可以通过发送关键词下载音乐。\n" \
               "网易音乐模块还可以通过发送歌单链接，导入歌单里的曲目。\n\n" \
               "4 动画索引模块：可以通过发送一张动漫图片，识别查询动漫的名字和快照。\n\n" \
               "5 记录模式切换：一般情况下是正常模式，当切换到记录模式时，您可以和机器人对话。"
        bot.send_message(chat_id=update.message.chat.id, text=text)

    @restricted
    def manage_bot(self, bot, update, args):
        self.manage.manage_bot(bot, update, args)

    def handler_startup(self, dispatcher):
        dispatcher.add_handler(CommandHandler(['start', 'mode'], self.start_command, pass_user_data=True))
        dispatcher.add_handler(CommandHandler('help', self.help_info))
        dispatcher.add_handler(CommandHandler('super', self.manage_bot, pass_args=True))
