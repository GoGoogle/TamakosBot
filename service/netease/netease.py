import logging

from service.netease import api, tool

logger = logging.getLogger(__name__)


def get_music(bot, update, args):
    try:
        key_word = args[0]
        logger.info('get_music: {}'.format(key_word))

        # 1.展示`关键字`歌曲选择列表
        show_select_music_list(bot, update, key_word)

        # 2.监听响应的内容，取消、翻页或者下载
        listen_select_reply()

    except IndexError:
        text = "请提供要搜索的音乐的名字"
        update.message.reply_text(text=text)


def show_select_music_list(bot, update, kw, pagecode=1):
    logger.info('show_select_music_list: keyword={}'.format(kw))
    search_musics_dict = api.search_musics_by_keyword_and_pagecode(kw, pagecode=pagecode)
    if search_musics_dict['code'] != 200:
        logger.error('api search_musics_by_keyword_and_pagecode error: code is {}'
                     .format(search_musics_dict['code']))
    else:
        if search_musics_dict['result']['songCount'] == 0:
            logger.debug('show_select_music_list: keyword={0}, the result is null', kw)
            text = "搜索结果为空值"
            update.message.reply_text(text=text)
        else:
            music_list_selector = tool.produce_music_list_selector(kw, pagecode, search_musics_dict['result'])
            panel = tool.transfer_music_list_selector_to_panel(music_list_selector)
            update.message.reply_text(text=panel['text'], reply_markup=panel['reply_markup'])


def listen_select_reply():
    """监听响应的内容，取消、翻页或者下载
    如果为取消，则直接删除选择列表
    如果为翻页，则修改选择列表并进行翻页
    如果为下载，则获取 music_id 并生成 NeteaseMusic。然后，加载-获取歌曲url，发送音乐文件，删除上一条信息
    :return:
    """
    pass
