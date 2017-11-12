import logging
import os
import time
from io import BytesIO

import requests
import telegram
from telegram.ext import run_async

from config import application
from database import db_audio, db_mv
from service.apis import netease_api
from service.operate import netease_generate

logger = logging.getLogger(__name__)

tool_proxies = application.TOOL_PROXY


def download_continuous(bot, query, true_download_url, file, file_title, edited_msg,
                        false_download_url=''):
    logger.info('{} ..下载中'.format(file_title))
    try:
        if tool_proxies:
            # 代理使用国内服务器转发接口
            r = requests.get(true_download_url, stream=True, timeout=application.TIMEOUT, proxies=tool_proxies)
        else:
            r = requests.get(true_download_url, stream=True, timeout=application.TIMEOUT)

        start = time.time()
        total_length = int(r.headers.get('content-length'))
        dl = 0
        for chunk in r.iter_content(application.CHUNK_SIZE):
            dl += len(chunk)
            file.write(chunk)

            network_speed = dl / (time.time() - start)
            if network_speed > 1024 * 1024:
                network_speed_status = '{:.2f} MB/s'.format(network_speed / (1024 * 1024))
            else:
                network_speed_status = '{:.2f} KB/s'.format(network_speed / 1024)

            if dl > 1024 * 1024:
                dl_status = '{:.2f} MB'.format(dl / (1024 * 1024))
            else:
                dl_status = '{:.0f} KB'.format(dl / 1024)

            # 已下载大小，总大小，已下载的百分比，网速
            progress = '{0} / {1:.2f} MB ({2:.0f}%) - {3}'.format(dl_status,
                                                                  total_length / (1024 * 1024),
                                                                  dl / total_length * 100,
                                                                  network_speed_status)
            progress_status = '163 ️🎵  \n[{0}]({1})\n正在飞速下载\n{2}'.format(file_title, false_download_url, progress)

            bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=edited_msg.message_id,
                text=progress_status,
                disable_web_page_preview=True,
                parse_mode=telegram.ParseMode.MARKDOWN,
                timeout=application.TIMEOUT
            )

    except:
        logger.error('download_continuous failed', exc_info=True)


def send_music_file(bot, query, file, netease_id, file_name, file_duration, file_scheme, file_caption, edited_msg,
                    false_download_url=''):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='163 🎵 \n[{0}]({1})\n在发送的路上~'.format(file_name, false_download_url),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        timeout=application.TIMEOUT
    )

    logger.info("文件: {}/mp4 >> 正在发送中".format(file_name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)

    file_msg = None
    try:
        file_msg = bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=file_caption,
                                  duration=file_duration,
                                  title=file_name[:file_name.rfind('.')],
                                  timeout=application.TIMEOUT)

        # 存储 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
        db_audio.DBAudio().store_file(file_msg.audio.file_id, netease_id, file_name, file_duration,
                                      file_scheme,
                                      time.time())
        logger.info("文件: {}/mp4 发送成功.".format(file_name))
    except:
        # 清除数据库内容
        # TODO
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)


@run_async
def send_movie_file(bot, query, mv_true_url, mv_id, mv_name, mv_duration, mv_quality, file_caption,
                    false_download_url=''):
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


def selector_page_turning(bot, query, kw, page_code):
    logger.info('selector_page_turning: keyword: {0}; page_code={1}'.format(kw, page_code))
    search_musics_dict = netease_api.search_musics_by_keyword_and_pagecode(kw, pagecode=page_code)
    music_list_selector = netease_generate.produce_music_list_selector(kw, page_code, search_musics_dict['result'])
    panel = netease_generate.transfer_music_list_selector_to_panel(music_list_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=application.TIMEOUT)


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="叮~",
                            show_alert=False,
                            timeout=application.TIMEOUT)
    query.message.delete()


def selector_send_music(bot, query, music_id, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        selector_cancel(bot, query)

    edited_msg = bot.send_message(chat_id=query.message.chat.id, text="正在加载，请稍后~",
                                  timeout=application.TIMEOUT)
    detail = netease_api.get_music_detail_by_musicid(music_id)['songs'][0]

    # 转为对象好处理
    music_obj = netease_generate.generate_music_obj(detail,
                                                    netease_api.get_music_url_by_musicid(music_id)['data'][0])

    music_file = BytesIO()
    try:
        music_caption = "曲目: {0}\n演唱: {1}\n格式: {3}\n专辑: {2}".format(
            music_obj.name, ' '.join(v.name for v in music_obj.artists),
            music_obj.album.name, music_obj.scheme
        )
        music_filename = '{0} - {1}.mp3'.format(
            ' / '.join(v.name for v in music_obj.artists), music_obj.name)
        netease_url = 'http://music.163.com/song?id={}'.format(music_obj.mid)

        # 查询数据库 compare the files with the database ,and find the file_Id
        file_id = db_audio.DBAudio().compare_file(music_id, music_filename,
                                                  music_obj.duration,
                                                  music_obj.scheme,
                                                  time.time())
        if file_id:
            send_music_file(bot, query, file_id, music_obj.mid, music_filename, music_obj.duration, music_obj.scheme,
                            music_caption,
                            edited_msg,
                            netease_url)
        else:
            logger.info('163 song url is {}'.format(music_obj.url))

            download_continuous(bot, query, music_obj.url, music_file, music_filename, edited_msg,
                                false_download_url=netease_url)

            music_file = BytesIO(music_file.getvalue())
            music_file.name = music_filename

            send_music_file(bot, query, music_file, music_obj.mid, music_filename, music_obj.duration, music_obj.scheme,
                            music_caption,
                            edited_msg,
                            netease_url)

        if music_obj.mv:
            logger.info('selector download MV: mvid={0}'.format(music_obj.mv.mid))

            mv_file_fullname = '{0} - {1}.mp4'.format(
                music_obj.mv.artist_name, music_obj.mv.name)

            mv_true_url = netease_api.get_mv_true_url_by_mv_url(music_obj.mv.url)  # true url

            time_fmt = '{0}分{1}秒'.format(int(music_obj.mv.duration // 60), int(music_obj.mv.duration % 60))

            mv_caption = "标题: {0}\n演唱: {1}\n时长: {2}\n品质: {3}p".format(
                music_obj.mv.name, music_obj.mv.artist_name, time_fmt,
                music_obj.mv.quality
            )

            send_movie_file(bot, query, mv_true_url, music_obj.mv.mid, mv_file_fullname, music_obj.mv.duration,
                            music_obj.mv.quality, mv_caption, music_obj.mv.url)

    except:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
        if edited_msg:
            edited_msg.delete()


def selector_playlist_turning(bot, update, playlist_id, cur_pagecode=1):
    playlist_dict = netease_api.get_playlist_by_playlist_id(playlist_id)
    playlist_selector = netease_generate.produce_playlist_selector(playlist_dict['playlist'])
    panel = netease_generate.transfer_playlist_selector_to_panel(playlist_selector, cur_pagecode)
    bot.edit_message_text(chat_id=update.message.chat.id,
                          message_id=update.message.message_id,
                          text=panel['text'], quote=True, reply_markup=panel['reply_markup'],
                          disable_web_page_preview=True,
                          parse_mode=telegram.ParseMode.MARKDOWN)


def selector_tracetime_list_turning(bot, update, day, cur_pagecode=1):
    pass
