import logging
from configparser import ConfigParser
from functools import wraps

import emoji
from requests.exceptions import ConnectionError as ConnectionException, RequestException, Timeout, ProxyError
from telegram import TelegramError
from telegram import Update


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
    query.message.delete()


def is_contain_zh(content):
    for x in content:
        return u'\u4e00' <= x <= u'\u9fa5'


def is_contain_emoji(content):
    for x in content:
        return x in emoji.UNICODE_EMOJI


logger = logging.getLogger(__name__)


class SearchNotFound(RequestException):
    """Search api return None."""


class SongNotAvailable(RequestException):
    """Some songs are not available, for example Taylor Swift's songs."""


class GetRequestIllegal(RequestException):
    """Status code is not 200."""


class PostRequestIllegal(RequestException):
    """Status code is not 200."""


class NotAuthorized(TelegramError):
    """Status code is not 200."""


def exception_handle(method):
    """Handle exceptions raised by requests library."""

    def wrapper(*args, **kwargs):
        try:
            result = method(*args, **kwargs)
            return result
        except ProxyError:
            logger.exception('ProxyError when try to get %s.', args)
            raise ProxyError('A proxy error occurred.')
        except ConnectionException:
            logger.exception('ConnectionError when try to get %s.', args)
            raise ConnectionException('DNS failure, refused connection, etc.')
        except Timeout:
            logger.exception('Timeout when try to get %s', args)
            raise Timeout('The request timed out.')
        except GetRequestIllegal:
            logger.exception('RequestException when try to get %s.', args)
            raise GetRequestIllegal('Please check out your network.')
        except RequestException:
            logger.exception('RequestException when try to get %s.', args)
            raise RequestException('Please check out your network.')

    return wrapper
