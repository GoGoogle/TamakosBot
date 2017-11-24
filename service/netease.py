import logging
import os
import time

import requests
import telegram
from telegram.ext import run_async

from config import application
from database import db_audio, db_mv
from service import netease_api, netease_util
from util import util

logger = logging.getLogger(__name__)

tool_proxies = application.TOOL_PROXY


def search_music(bot, update, kw):
    try:
        logger.info('get_music: {}'.format(kw))
        search_musics_dict = netease_api.search_musics_by_keyword_and_pagecode(kw, pagecode=1)

        if search_musics_dict['code'] == 400:
            text = "該命令項錯誤！"
            update.message.reply_text(text=text, parse_mode=telegram.ParseMode.MARKDOWN)

        elif search_musics_dict['result']['songCount'] == 0:
            text = "無結果值！"
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
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="喵~",
                                      timeout=application.TIMEOUT)
        update.message.message_id = edited_msg.message_id
        netease_util.selector_playlist_turning(bot, update, playlist_id, cur_pagecode=1)
    except IndexError:
        logger.warning('無法獲取該歌曲單目', exc_info=True)


def selector_send_music(bot, query, music_id, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        util.selector_cancel(bot, query)

    edited_msg = bot.send_message(chat_id=query.message.chat.id, text="開始搜索",
                                  timeout=application.TIMEOUT)
    detail = netease_api.get_music_detail_by_musicid(music_id)['songs'][0]

    # 转为对象好处理
    music_obj = netease_util.generate_music_obj(detail,
                                                netease_api.get_music_url_by_musicid(music_id)['data'][0])

    # music_caption = "曲目: {0}\n演唱: {1}\n格式: {3}\n专辑: {2}".format(
    #     music_obj.name, ' / '.join(v.name for v in music_obj.artists),
    #     music_obj.album.name, music_obj.scheme
    # )
    music_caption = ""

    full_file_name = r'{0} - {1}.{2}'.format(
        music_obj.name, ' & '.join(v.name for v in music_obj.artists), music_obj.suffix)
    # 字符串进行处理
    full_file_name = full_file_name.replace("/", ":")
    music_file_path = os.path.join(application.TMP_Folder, full_file_name)
    music_file = open(music_file_path, 'wb+')

    try:
        # 查询数据库 compare the files with the database ,and find the file_Id
        file_id = db_audio.DBAudio().compare_file(music_id, music_obj.name,
                                                  music_obj.duration,
                                                  music_obj.scheme,
                                                  time.time())
        if file_id:
            send_music_file(bot, query, file_id, music_obj, music_caption, edited_msg)
        else:
            logger.info('163 song url is {}'.format(music_obj.url))

            netease_util.download_continuous(bot, query, music_obj, music_file, edited_msg, tool_proxies)

            # 填写 id3tags
            util.write_id3tags(music_file_path, music_obj.name, list(v.name for v in music_obj.artists),
                               music_obj.album.name)

            music_file.seek(0, os.SEEK_SET)  # 从开始位置开始读

            send_music_file(bot, query, music_file, music_obj, music_caption, edited_msg)

            # if music_obj.mv:
            #     logger.info('selector download MV: mvid={0}'.format(music_obj.mv.mid))
            #
            #     mv_file_fullname = '{0} - {1}.mp4'.format(
            #         music_obj.mv.artist_name, music_obj.mv.name)
            #
            #     mv_true_url = netease_api.get_mv_true_url_by_mv_url(music_obj.mv.url)  # true url
            #
            #     time_fmt = '{0}分{1}秒'.format(int(music_obj.mv.duration // 60), int(music_obj.mv.duration % 60))
            #
            #     mv_caption = "标题: {0}\n演唱: {1}\n时长: {2}\n品质: {3}p".format(
            #         music_obj.mv.name, music_obj.mv.artist_name, time_fmt,
            #         music_obj.mv.quality
            #     )
            #
            #     send_movie_file(bot, query, mv_true_url, music_obj.mv.mid, mv_file_fullname, music_obj.mv.duration,
            #                     music_obj.mv.quality, mv_caption, music_obj.mv.url)

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
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='163 🎵{0} 媒體開始傳送'.format(music_obj.name),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        timeout=application.TIMEOUT
    )

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

        # 存储 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
        db_audio.DBAudio().store_file(file_msg.audio.file_id, music_obj.mid, music_obj.name, music_obj.duration,
                                      music_obj.scheme,
                                      time.time())
        logger.info("文件: {} 发送成功.".format(music_obj.name))
    except:
        # 清除数据库内容
        # TODO
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)


@run_async
def send_movie_file(bot, query, mv_true_url, mv_id, mv_name, mv_duration, mv_quality, file_caption):
    logger.info("文件: {0}， ..准备下载中\n地址为: {1}".format(mv_name, mv_true_url))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_VIDEO)

    file_path = os.path.join(application.TMP_Folder, mv_name)

    # 查询数据库 compare the files with the database ,and find the file_Id
    logger.info(
        'compare follow to database: {0}|{1}|{2}|{3}|{4}'.format(mv_id, mv_name, mv_duration,
                                                                 mv_quality,
                                                                 time.time()))
    file_id = db_mv.DBMv().compare_file(mv_id, mv_name[:mv_name.rfind('.')], mv_duration,
                                        mv_quality,
                                        time.time())
    video_msg = None

    try:
        if file_id:
            logger.info("文件: {}， >> 正在发送中".format(mv_name))
            video_msg = bot.send_video(chat_id=query.message.chat.id, video=file_id,
                                       caption=file_caption,
                                       duration=mv_duration,
                                       title=mv_name,
                                       timeout=application.TIMEOUT)
        else:
            logger.info('{} ..下载中'.format(mv_name))
            if tool_proxies:
                # 代理使用国内服务器转发接口
                r = requests.get(mv_true_url, stream=True, timeout=application.TIMEOUT, proxies=tool_proxies)
            else:
                r = requests.get(mv_true_url, stream=True, timeout=application.TIMEOUT)

            with open(file_path, 'wb') as fd:
                for chunk in r.iter_content(application.CHUNK_SIZE):
                    fd.write(chunk)

            logger.info("文件: {}， >> 正在发送中".format(mv_name))
            video_msg = bot.send_video(chat_id=query.message.chat.id, video=open(file_path, 'rb'),
                                       caption=file_caption,
                                       duration=mv_duration,
                                       title=mv_name[:mv_name.rfind('.')],
                                       timeout=application.TIMEOUT)

            # 存储 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
            db_mv.DBMv().store_file(video_msg.video.file_id, mv_id, mv_name[:mv_name.rfind('.')], mv_duration,
                                    mv_quality, time.time())
    except:
        logger.error('downloading mv failed', exc_info=True)
        # 清楚数据库内容
        # TODO
        if video_msg:
            video_msg.delete()
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.info('{} has finished downloading'.format(file_path))
