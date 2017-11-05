import logging

from service.apis import sing5_api
from service.operate import sing5_generate

logger = logging.getLogger(__name__)


def search_music(bot, update, args):
    try:
        key_word = args[0]
        logger.info('get_music: {}'.format(key_word))
        musics_dict = sing5_api.search_musics_by_keyword_pagecode_and_filter(key_word, pagecode=1, filter_type=2)
        if len(musics_dict['data']['songArray']) == 0:
            text = "没有搜索到~"
            update.message.reply_text(text=text)
        else:
            music_list_selector = sing5_generate.produce_music_list_selector(key_word, 1,
                                                                             musics_dict['data']['songArray'])
            panel = sing5_generate.transfer_music_list_selector_to_panel(music_list_selector)
            update.message.reply_text(text=panel['text'], quote=True, reply_markup=panel['reply_markup'])

    except IndexError:
        text = "请提供要搜索的音乐的名字"
        update.message.reply_text(text=text)
    except Exception as e:
        logger.error('search music error', exc_info=True)


def listen_selector_reply(bot, update):
    pass


def response_toplist(bot, update):
    try:
        musics_result = sing5_api.get_music_top_by_type_pagecode_and_date()
        panel = sing5_generate.produce_music_top_selector(musics_result)
        update.message.reply_text(text=panel['text'], quote=True, reply_markup=panel['reply_markup'])
    except Exception as e:
        logger.error('search music error', exc_info=True)
