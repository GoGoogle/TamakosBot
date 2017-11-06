import logging

from config import application
from service.apis import sing5_api
from service.operate import sing5_generate, sing5_selector

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
    logger.info('sing5 listen_selector_reply: data={}'.format(update.callback_query.data))
    query = update.callback_query
    index1 = query.data.find('*')
    index2 = query.data.find('+')
    index3 = query.data.find('-')
    index4 = query.data.find('t')
    if index1 != -1:
        sing5_selector.selector_cancel(bot, query)
    elif index2 != -1:
        page_code = int(query.data[index2 + 1:]) + 1
        mtype = query.data[6:index2 - 1]
        sing5_selector.selector_page_turning(bot, query, mtype, page_code)
    elif index3 != -1:
        page_code = int(query.data[index3 + 1:]) - 1
        mtype = query.data[6:index3 - 1]
        sing5_selector.selector_page_turning(bot, query, mtype, page_code)
    else:
        music_id = int(query.data[index4 + 1:])
        mtype = query.data[6:index4 - 1]
        sing5_selector.selector_send_music(bot, query, music_id, mtype, False)


def response_toplist(bot, update):
    try:
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="..排行榜导入中",
                                      timeout=application.TIMEOUT)
        update.message.message_id = edited_msg.message_id

        musics_result = sing5_api.get_music_top_by_type_pagecode_and_date(mtype='fc', pagecode=1)
        top_selector = sing5_generate.produce_music_top_selector('fc', 1, musics_result)
        panel = sing5_generate.transfer_music_top_selector_to_panel(top_selector)
        bot.edit_message_text(chat_id=update.message.chat.id,
                              message_id=update.message.message_id,
                              text=panel['text'], quote=True,
                              disable_web_page_preview=True,
                              reply_markup=panel['reply_markup'])
    except Exception as e:
        logger.error('search music error', exc_info=True)
