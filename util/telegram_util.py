from configparser import ConfigParser
from functools import wraps

import emoji
from telegram import Update

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


class DataStore(object):
    """
    The data will be stored in common, not single chatroom or user, so we can not use "chat_data" or "user_data".
    That is the Significance of this object. And it likes a database in fact.
    """

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


def get_config():
    cfg = ConfigParser()
    cfg.read('config/custom.ini')
    return cfg


def restricted(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        update = list(filter(lambda x: isinstance(x, Update), args))[0]
        user_id = update.effective_user.id

        cfg = get_config()
        admin_group = [cfg.get('base', 'admin_room'), cfg.get('base', 'admin')]

        if user_id not in admin_group:
            raise NotAuthorized("Unauthorized access denied for {}".format(user_id))
        return func(*args, **kwargs)

    return wrapped


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


def is_contain_zh(content):
    for x in content:
        return u'\u4e00' <= x <= u'\u9fa5'


def is_contain_emoji(content):
    for x in content:
        return x in emoji.UNICODE_EMOJI
