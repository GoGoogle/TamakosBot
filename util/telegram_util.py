from functools import wraps

from telegram import Update

from config.application import ADMINS
from util.excep_util import NotAuthorized


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
            raise NotAuthorized("Unauthorized access denied for {}".format(user_id))
        return func(*args, **kwargs)

    return wrapped


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


class DataStore(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataStore, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def del_data(self, key):
        del self.data[key]

    def clear_data(self):
        self.data.clear()

    def is_exist(self, key):
        return True if key in self.data else False
