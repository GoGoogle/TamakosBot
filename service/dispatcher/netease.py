import logging

from config.application import TIMEOUT
from service.apis import netease_api
from service.operate import netease_selector, netease_generate

logger = logging.getLogger(__name__)


def search_music(bot, update, args):
    try:
        key_word = args[0]
        logger.info('get_music: {}'.format(key_word))
        search_musics_dict = netease_api.search_musics_by_keyword_and_pagecode(key_word, pagecode=1)
        if search_musics_dict['result']['songCount'] == 0:
            text = "没有搜索到~"
            update.message.reply_text(text=text)
        else:
            music_list_selector = netease_generate.produce_music_list_selector(key_word, 1,
                                                                               search_musics_dict['result'])
            panel = netease_generate.transfer_music_list_selector_to_panel(music_list_selector)
            update.message.reply_text(text=panel['text'], quote=True, reply_markup=panel['reply_markup'])

    except IndexError:
        text = "请提供要搜索的音乐的名字"
        update.message.reply_text(text=text)
    except Exception as e:
        logger.error('search music error', exc_info=True)


def listen_selector_reply(bot, update):
    """监听响应的内容，取消、翻页或者下载
    如果为取消，则直接删除选择列表
    如果为翻页，则修改选择列表并进行翻页
    如果为下载，则获取 music_id 并生成 NeteaseMusic。然后，加载-获取歌曲url，发送音乐文件，删除上一条信息
    :return:
    """
    logger.info('listen_selector_reply: data={}'.format(update.callback_query.data))
    query = update.callback_query
    index1 = query.data.find('*')
    index2 = query.data.find('+')
    index3 = query.data.find('-')
    index4 = query.data.find('D')
    index5 = query.data.find('U')
    index6 = query.data.find('P')
    if index1 != -1:
        netease_selector.selector_cancel(bot, query)
    elif index2 != -1:
        page_code = int(query.data[index2 + 1:]) + 1
        kw = query.data[8:index2 - 1]
        netease_selector.selector_page_turning(bot, query, kw, page_code)
    elif index3 != -1:
        page_code = int(query.data[index3 + 1:]) - 1
        kw = query.data[8:index3 - 1]
        netease_selector.selector_page_turning(bot, query, kw, page_code)
    elif index4 != -1:
        page_code = int(query.data[index4 + 1:]) + 1
        playlist_id = query.data[8:index4 - 1]
        netease_selector.selector_playlist_turning(bot, query, playlist_id, page_code)
    elif index5 != -1:
        page_code = int(query.data[index5 + 1:]) - 1
        playlist_id = query.data[8:index5 - 1]
        # print(page_code, playlist_id, '***************')
        netease_selector.selector_playlist_turning(bot, query, playlist_id, page_code)
    elif index6 != -1:
        music_id = query.data[index6 + 1:]
        netease_selector.selector_send_music(bot, query, music_id, False)
    else:
        music_id = query.data[8:]
        netease_selector.selector_send_music(bot, query, music_id, True)


def response_playlist(bot, update, playlist_id):
    try:
        logger.info('response_playlist: playlist_id={}'.format(playlist_id))
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="..歌单导入中",
                                      timeout=TIMEOUT)
        update.message.message_id = edited_msg.message_id
        netease_selector.selector_playlist_turning(bot, update, playlist_id, cur_pagecode=1)
    except IndexError:
        logger.warning('获取歌单失败', exc_info=True)


def trace_music(bot, update, args):
    try:
        day = 0
        if len(args) != 0:
            day = args[0]
        netease_selector.selector_tracetime_list_turning(bot, update, day, cur_pagecode=1)
    except Exception as e:
        logger.error('trace music error', exc_info=True)
