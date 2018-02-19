import logging

from telegram import ParseMode
from telegram.ext import CommandHandler

from module.modez import mode


class Startup(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
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
        # text = "`我是机器人小玉，我来说明使用方法!\n" \
        #        "::发送关键词搜索并下载音乐" \
        #        "::同上。发送歌单链接，以便导入歌单" \
        #        "::发送一张动漫截图，获取动漫信息" \
        #        "::如果~变成⦿后，就可以回复我呢(否则需要耐心等待哦)。\n`"
        text = "`我是机器人小玉，我来说明使用方法!\n" \
               "::发送关键词搜索并下载音乐\n" \
               "::同上。发送歌单链接，以便导入歌单\n" \
               "::发送一张动漫截图，获取动漫信息\n"
               #  "::如果~变成⦿后，就可以回复我呢(否则需要耐心等待哦)。\n`"
        bot.send_message(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

    def handler_startup(self, dispatcher):
        dispatcher.add_handler(CommandHandler(['start', 'mode'], self.start_command, pass_user_data=True))
        dispatcher.add_handler(CommandHandler('help', self.help_info))
