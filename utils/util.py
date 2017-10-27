from functools import wraps
from config import configfile


def only_admin(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        if update.message.from_user.id not in configfile.admins:
            text = "This command is invalid"
            update.message.reply_text(text=text, quote=True)
            return
        return func(bot, update, *args, **kwargs)

    return wrapped
