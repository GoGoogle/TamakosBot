from functools import wraps

from config.application import ADMINS


class BotResult:
    def __init__(self, code, msg='', body=None):
        self.code = code
        self.msg = msg
        self.body = body

    def get_status(self):
        return self.code

    def get_msg(self):
        return self.msg

    def get_body(self):
        return self.body


def restricted(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        update = list(filter(lambda x: isinstance(x, Update), args))[0]
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            logger.warning("Unauthorized access denied for {}.".format(user_id))
            return
        return func(*args, **kwargs)

    return wrapped


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()
