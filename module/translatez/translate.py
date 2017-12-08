import logging

from module.translatez import translate_crawler


class Translate(object):
    m_name = "translate"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crawler = translate_crawler.TranslateApi()

    def request_translate(self, bot, update, source, option):
        if option == 1:
            options = {'from': 'zh', 'to': 'en'}
        else:
            options = {'from': 'en', 'to': 'zh'}
        bot_result = self.crawler.post_translate(source, options)
        if bot_result.get_status() == 200:
            result = bot_result.get_body()['translation'][0]['translated'][0]['text']
            bot.send_message(chat_id=update.message.chat.id, text=result)
        if bot_result.get_status() == 400:
            self.logger.error(bot_result.get_msg())
            text = "It's a pity! Here occurred some errors that I could not translate it."
            bot.send_message(chat_id=update.message.chat.id, text=text)
