import logging
import os

import telegram

from config import application
from service import netease_api, netease_util
from util import util

logger = logging.getLogger(__name__)

tool_proxies = application.TOOL_PROXY


def search_music(bot, update, kw):
    try:
        logger.info('get_music: {}'.format(kw))
        search_musics_dict = netease_api.search_musics_by_keyword_and_pagecode(kw, pagecode=1)

        if search_musics_dict['code'] == 400:
            text = "缺少歌曲名称"
            update.message.reply_text(text=text, parse_mode=telegram.ParseMode.MARKDOWN)

        elif search_musics_dict['result']['songCount'] == 0:
            text = "此歌曲找不到~"
            update.message.reply_text(text=text)
        else:
            music_list_selector = netease_util.produce_single_music_selector(kw, 1,
                                                                             search_musics_dict['result'])
            panel = netease_util.transfer_single_music_selector_to_panel(music_list_selector)
            update.message.reply_text(text=panel['text'], quote=True, reply_markup=panel['reply_markup'])

    except Exception as e:
        logger.error('search music error', exc_info=True)


def response_single_music(bot, update):
    """监听响应的内容，取消、翻页或者下载
    如果为取消，则直接删除选择列表
    如果为翻页，则修改选择列表并进行翻页
    如果为下载，则获取 music_id 并生成 NeteaseMusic。然后，加载-获取歌曲url，发送音乐文件，删除上一条信息
    :return:
    """
    logger.info('netease listen_selector_reply: data={}'.format(update.callback_query.data))
    query = update.callback_query
    index1 = query.data.find('*')
    index2 = query.data.find('+')
    index3 = query.data.find('-')
    index4 = query.data.find('D')
    index5 = query.data.find('U')
    index6 = query.data.find('P')
    if index1 != -1:
        util.selector_cancel(bot, query)
    elif index2 != -1:
        page_code = int(query.data[index2 + 1:]) + 1
        kw = query.data[8:index2 - 1]
        netease_util.selector_page_turning(bot, query, kw, page_code)
    elif index3 != -1:
        page_code = int(query.data[index3 + 1:]) - 1
        kw = query.data[8:index3 - 1]
        netease_util.selector_page_turning(bot, query, kw, page_code)
    elif index4 != -1:
        page_code = int(query.data[index4 + 1:]) + 1
        playlist_id = query.data[8:index4 - 1]
        netease_util.selector_playlist_turning(bot, query, playlist_id, page_code)
    elif index5 != -1:
        page_code = int(query.data[index5 + 1:]) - 1
        playlist_id = query.data[8:index5 - 1]
        # print(page_code, playlist_id, '***************')
        netease_util.selector_playlist_turning(bot, query, playlist_id, page_code)
    elif index6 != -1:
        music_id = query.data[index6 + 1:]
        selector_send_music(bot, query, music_id, False)
    else:
        music_id = query.data[8:]
        selector_send_music(bot, query, music_id, True)


def response_playlist(bot, update, playlist_id):
    try:
        logger.info('response_playlist: playlist_id={}'.format(playlist_id))
        netease_util.selector_playlist_turning(bot, update, playlist_id, cur_pagecode=1)
    except IndexError:
        logger.warning('無法獲取該歌曲單目', exc_info=True)


def selector_send_music(bot, query, music_id, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        util.selector_cancel(bot, query)

    detail = netease_api.get_music_detail_by_musicid(music_id)['songs'][0]

    # 转为对象好处理
    music_obj = netease_util.generate_music_obj(detail,
                                                netease_api.get_music_url_by_musicid(music_id)['data'][0])

    edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                  text="找到歌曲: [{0}]({1})".format(music_obj.name, music_obj.url),
                                  parse_mode=telegram.ParseMode.MARKDOWN,
                                  timeout=application.TIMEOUT)

    full_file_name = r'{0} - {1}.{2}'.format(
        music_obj.name, ' & '.join(v.name for v in music_obj.artists), music_obj.suffix)
    # 字符串进行处理
    full_file_name = full_file_name.replace("/", ":")
    music_file_path = os.path.join(application.TMP_Folder, full_file_name)
    music_file = open(music_file_path, 'wb+')

    try:
        logger.info('163 song url is {}'.format(music_obj.url))

        netease_util.download_continuous(bot, query, music_obj, music_file, edited_msg, tool_proxies)

        # 填写 id3tags
        util.write_id3tags(music_file_path, music_obj.name, list(v.name for v in music_obj.artists),
                           music_obj.album.name)

        music_file.seek(0, os.SEEK_SET)  # 从开始位置开始读

        send_music_file(bot, query, music_file, music_obj, '')

    except:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
        if os.path.exists(music_file_path):
            os.remove(music_file_path)
        if edited_msg:
            edited_msg.delete()


def send_music_file(bot, query, file, music_obj, music_caption):
    logger.info("文件: {} >> 正在发送中".format(music_obj.name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)

    file_msg = None
    try:
        file_msg = bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=music_caption,
                                  duration=music_obj.duration,
                                  title=music_obj.name,
                                  performer=' / '.join(v.name for v in music_obj.artists),
                                  disable_notification=True,
                                  timeout=application.TIMEOUT)

        logger.info("文件: {} 发送成功.".format(music_obj.name))
    except:
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)
