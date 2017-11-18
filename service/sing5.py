import logging
import os
import time

import telegram

from config import application
from database import db_audio
from service import sing5_util, sing5_api
from util import util

logger = logging.getLogger(__name__)
tool_proxies = application.TOOL_PROXY


def search_music(bot, update, args):
    try:
        key_word = args[0]
        logger.info('get_music: {}'.format(key_word))
        musics_dict = sing5_api.search_musics_by_keyword_pagecode_and_filter(key_word, pagecode=1, filter_type=2)
        if len(musics_dict['data']['songArray']) == 0:
            text = "没有搜索到~"
            update.message.reply_text(text=text)
        else:
            music_list_selector = sing5_util.produce_single_music_selector(key_word, 1,
                                                                           musics_dict['data']['songArray'])
            panel = sing5_util.transfer_single_music_selector_to_panel(music_list_selector)
            update.message.reply_text(text=panel['text'], quote=True, reply_markup=panel['reply_markup'])

    except IndexError:
        text = "请提供要搜索的音乐的名字"
        update.message.reply_text(text=text)
    except Exception as e:
        logger.error('search music error', exc_info=True)


def response_single_music(bot, update):
    logger.info('sing5 listen_selector_reply: data={}'.format(update.callback_query.data))
    query = update.callback_query
    index1 = query.data.find('*')
    index2 = query.data.find('+')
    index3 = query.data.find('-')
    index4 = query.data.find('t')
    if index1 != -1:
        util.selector_cancel(bot, query)
    elif index2 != -1:
        page_code = int(query.data[index2 + 1:]) + 1
        mtype = query.data[6:index2 - 1]
        sing5_util.selector_page_turning(bot, query, mtype, page_code)
    elif index3 != -1:
        page_code = int(query.data[index3 + 1:]) - 1
        mtype = query.data[6:index3 - 1]
        sing5_util.selector_page_turning(bot, query, mtype, page_code)
    else:
        music_id = int(query.data[index4 + 1:])
        mtype = query.data[6:index4 - 1]
        selector_send_music(bot, query, music_id, mtype, False)


def response_toplist(bot, update):
    try:
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="..排行榜导入中",
                                      timeout=application.TIMEOUT)
        update.message.message_id = edited_msg.message_id

        musics_result = sing5_api.get_music_top_by_type_pagecode_and_date(mtype='fc', pagecode=1)
        top_selector = sing5_util.produce_music_top_selector('fc', 1, musics_result)
        panel = sing5_util.transfer_music_top_selector_to_panel(top_selector)
        bot.edit_message_text(chat_id=update.message.chat.id,
                              message_id=update.message.message_id,
                              text=panel['text'], quote=True,
                              disable_web_page_preview=True,
                              reply_markup=panel['reply_markup'])
    except Exception as e:
        logger.error('search music error', exc_info=True)


def selector_send_music(bot, query, music_id, mtype, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        util.selector_cancel(bot, query)

    edited_msg = bot.send_message(chat_id=query.message.chat.id, text="正在加载，请稍后~",
                                  timeout=application.TIMEOUT)
    #
    detail = sing5_api.get_music_detail_by_id_and_type(music_id, song_type=mtype)['data']
    url_detail = sing5_api.get_music_url_by_id_and_type(music_id, mtype)['data']

    # 转为对象好处理
    music_obj = sing5_util.generate_music_obj(detail,
                                              url_detail)
    # music_caption = "曲目: {0}\n演唱: {1}".format(
    #     music_obj.name, music_obj.singer.name
    # )
    music_caption = ''
    full_file_name = '{0} - {1}.mp3'.format(
        music_obj.singer.name, music_obj.name)

    music_file_path = os.path.join(application.TMP_Folder, full_file_name)
    music_file = open(music_file_path, 'wb+')

    try:
        # 查询数据库 compare the files with the database ,and find the file_Id
        file_id = db_audio.DBAudio().compare_file(music_id, music_obj.name, 0, '', time.time())
        if file_id:
            send_music_file(bot, query, file_id, music_obj, music_caption,
                            edited_msg)
        else:
            sing5_util.download_continuous(bot, query, music_obj, music_file, edited_msg)

            # 填写 id3tags
            util.write_id3tags(music_file_path, song_title=music_obj.name,
                               song_artist_list=[].append(music_obj.singer.name))

            music_file.seek(0, os.SEEK_SET)  # 从开始位置开始读

            send_music_file(bot, query, music_file, music_obj, music_caption, edited_msg)
    except:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
        if os.path.exists(music_file_path):
            os.remove(music_file_path)
        if edited_msg:
            edited_msg.delete()


def send_music_file(bot, query, music_file, music_obj, file_caption, edited_msg):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='5sing 🎵 \n[{0}]({1})\n在发送的路上~'.format(music_obj.name, music_obj.falseurl),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        timeout=application.TIMEOUT
    )

    logger.info("文件: {} >> 正在发送中".format(music_obj.name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)

    file_msg = None
    try:
        file_msg = bot.send_audio(chat_id=query.message.chat.id, audio=music_file, caption=file_caption,
                                  title=music_obj.name,
                                  performer=music_obj.singer.name,
                                  disable_notification=True,
                                  timeout=application.TIMEOUT)

        # 存储 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
        db_audio.DBAudio().store_file(file_msg.audio.file_id, music_obj.mid, music_obj.name, 0,
                                      '',
                                      time.time())
        logger.info("文件: {}/mp4 发送成功.".format(music_obj.name))
    except:
        # 清除数据库内容
        # TODO
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)
