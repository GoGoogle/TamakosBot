import logging

logger = logging.getLogger(__name__)


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"' % (update, err))


def handler_errors(dispatcher):
    dispatcher.add_error_handler(error)
