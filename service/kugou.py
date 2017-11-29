import logging
import os

import telegram

from config import application
from service import kugou_api, kugou_util
from util import mtil

logger = logging.getLogger(__name__)

def search_music(bot, update, kw):
    try:
        logger.info('get_music: {}'.format(kw))
        search_musics_dict = kugou_api.search_music_by_keyword_and_pagecode(kw, pagecode=1)

        if search_musics_dict['errcode'] != 0:
            text = "缺少歌曲名称"
            update.message.reply_text(text=text, parse_mode=telegram.ParseMode.MARKDOWN)

        elif search_musics_dict['data']['total'] == 0:
            text = "此歌曲找不到~"
            update.message.reply_text(text=text)
        else:
            music_list_selector = kugou_util.produce_single_music_selector(kw, 1,
                                                                           search_musics_dict['data'])
            panel = kugou_util.transfer_single_music_selector_to_panel(music_list_selector)
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
    if index1 != -1:
        mtil.selector_cancel(bot, query)
    elif index2 != -1:
        page_code = int(query.data[index2 + 1:]) + 1
        kw = query.data[3:index2 - 1]
        kugou_util.selector_page_turning(bot, query, kw, page_code)
    elif index3 != -1:
        page_code = int(query.data[index3 + 1:]) - 1
        kw = query.data[3:index3 - 1]
        kugou_util.selector_page_turning(bot, query, kw, page_code)
    else:
        music_id = query.data[3:]
        selector_send_music(bot, query, music_id, True)


def selector_send_music(bot, query, hash, delete):
    logger.info('selector_download_music: music_id={0}'.format(hash))
    if delete:
        mtil.selector_cancel(bot, query)

    detail = kugou_api.get_music_detail_by_musicid(hash)
    hq_detail = kugou_api.get_hqmusic_detail_by_musicid(hash)

    # 转为对象好处理
    music_obj = kugou_util.generate_music_obj(detail, hq_detail)

    edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                  text="找到歌曲: [{0}]({1})".format(music_obj.name, music_obj.url),
                                  parse_mode=telegram.ParseMode.MARKDOWN)

    full_file_name = r'{0} - {1}.{2}'.format(
        music_obj.name, music_obj.singer_name, music_obj.suffix)
    # 字符串进行处理
    full_file_name = full_file_name.replace("/", ":")
    music_file_path = os.path.join(application.TMP_Folder, full_file_name)
    music_file = open(music_file_path, 'wb+')

    try:
        logger.info('kugou song url is {}'.format(music_obj.url))

        kugou_util.download_continuous(bot, query, music_obj, music_file, edited_msg)

        # 填写 id3tags
        mtil.write_id3tags(music_file_path, music_obj.name, list(music_obj.singer_name),
                           music_obj.album_name)

        music_file.seek(0, os.SEEK_SET)  # 从开始位置开始读

        send_music_file(bot, query, music_file, music_obj, music_caption='', edited_msg=edited_msg)

    except:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
        if os.path.exists(music_file_path):
            os.remove(music_file_path)
        if edited_msg:
            edited_msg.delete()


def send_music_file(bot, query, file, music_obj, music_caption, edited_msg):
    logger.info("文件: {} >> 正在发送中".format(music_obj.name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='kg {0} 等待发送'.format(music_obj.name),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )

    file_msg = None
    try:
        file_msg = bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=music_caption,
                                  duration=music_obj.duration,
                                  title=music_obj.name,
                                  performer=music_obj.singer_name,
                                  disable_notification=True)

        logger.info("文件: {} 发送成功.".format(music_obj.name))
    except:
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)
