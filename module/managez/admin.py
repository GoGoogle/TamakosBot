import logging
import os

from telegram.error import BadRequest, ChatMigrated, TelegramError, Unauthorized

from config import application

logger = logging.getLogger(__name__)


def manage_bot(bot, update, payload):
    command = payload[0]
    params = payload[1:]
    try:
        command_analyzing(bot, update, command, params)
    except BadRequest and ChatMigrated as e:
        logger.error('命令提交错误', exc_info=True)
    except TelegramError and Unauthorized as e:
        logger.error('telegram 出错', exc_info=True)


def command_analyzing(bot, update, command, params):
    if command == 'log':
        log_path = os.path.join(os.getcwd(), application.LOG_FILE)
        print(log_path)
        bot.send_document(chat_id=update.message.chat.id,
                          document=open(log_path, 'rb'))
    elif command == 'leaveChat':
        payload = params[0]
        result = None
        try:
            result = bot.leave_chat(chat_id=payload)
            bot.send_message(chat_id=update.message.chat.id, text="退出该群成功")
        except TelegramError:
            logger.error('levaeChat failed, error is %s', result)
            bot.send_message(chat_id=update.message.chat.id, text="退出该群失败")

    else:
        text = "你的命令无效.你的命令是 {0}, 该命令的参数是 {1}".format(command, params)
        bot.send_message(chat_id=update.message.from_user.id,
                         text=text)
