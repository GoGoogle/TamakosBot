import logging
import taglib

from requests.exceptions import ConnectionError as ConnectionException, RequestException, Timeout, ProxyError

logger = logging.getLogger(__name__)


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中",
                            show_alert=False)
    query.message.delete()


def write_id3tags(file_path, song_title, song_artist_list, song_album=None, track_num='01/10'):
    song = taglib.File(file_path)
    if song:
        song.tags["ARTIST"] = song_artist_list
        song.tags["ALBUM"] = [song_album]
        song.tags["TITLE"] = [song_title]
        song.tags["TRACKNUMBER"] = [track_num]
        song.save()


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
        except RequestException:
            logger.exception('RequestException when try to get %s.', args)
            raise RequestException('Please check out your network.')

    return wrapper
