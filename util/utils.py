from functools import wraps
from config import application


def only_admin(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in application.ADMINS:
            update.message.reply_text(text="Unauthorized access denied for {}.".format(user_id), quote=True)
            return
        return func(bot, update, *args, **kwargs)

    return wrapped
