import logging

from requests.exceptions import ConnectionError as ConnectionException, RequestException, Timeout, ProxyError

logger = logging.getLogger(__name__)


class SearchNotFound(RequestException):
    """Search api return None."""


class SongNotAvailable(RequestException):
    """Some songs are not available, for example Taylor Swift's songs."""


class GetRequestIllegal(RequestException):
    """Status code is not 200."""


class PostRequestIllegal(RequestException):
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
