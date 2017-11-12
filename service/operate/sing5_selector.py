import logging
import time
from io import BytesIO

import requests
import telegram

from config import application
from database import db_audio
from service.apis import sing5_api
from service.operate import sing5_generate

logger = logging.getLogger(__name__)

tool_proxies = application.TOOL_PROXY


def download_continuous(bot, query, true_download_url, file, file_title, edited_msg,
                        false_download_url=''):
    logger.info('{0} 下载中,url={1}'.format(file_title, true_download_url))
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
            progress_status = '5sing ️🎵  \n[{0}]({1})\n正在飞速下载\n{2}'.format(file_title, false_download_url, progress)

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


def send_music_file(bot, query, file, sing5_id, file_name, file_caption, edited_msg,
                    false_download_url=''):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='5sing 🎵 \n[{0}]({1})\n在发送的路上~'.format(file_name, false_download_url),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        timeout=application.TIMEOUT
    )

    logger.info("文件: {}/mp4 >> 正在发送中".format(file_name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)

    file_msg = None
    try:
        file_msg = bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=file_caption,
                                  title=file_name[:file_name.rfind('.')],
                                  timeout=application.TIMEOUT)

        # 存储 database store file_id, title, duration, file_scheme and timestamp which is in 3 minutes
        db_audio.DBAudio().store_file(file_msg.audio.file_id, sing5_id, file_name, 0,
                                      '',
                                      time.time())
        logger.info("文件: {}/mp4 发送成功.".format(file_name))
    except:
        # 清除数据库内容
        # TODO
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="叮~",
                            show_alert=False,
                            timeout=application.TIMEOUT)
    query.message.delete()


def selector_page_turning(bot, query, mtype, page_code):
    logger.info('selector_page_turning: mtype: {0}; page_code={1}'.format(mtype, page_code))
    musics_result = sing5_api.get_music_top_by_type_pagecode_and_date(mtype='fc', pagecode=page_code)
    top_selector = sing5_generate.produce_music_top_selector(mtype, page_code, musics_result)
    panel = sing5_generate.transfer_music_top_selector_to_panel(top_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=application.TIMEOUT)


def selector_send_music(bot, query, music_id, mtype, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        selector_cancel(bot, query)

    edited_msg = bot.send_message(chat_id=query.message.chat.id, text="正在加载，请稍后~",
                                  timeout=application.TIMEOUT)
    #
    detail = sing5_api.get_music_detail_by_id_and_type(music_id, song_type=mtype)['data']
    url_detail = sing5_api.get_music_url_by_id_and_type(music_id, mtype)['data']

    # 转为对象好处理
    music_obj = sing5_generate.generate_music_obj(detail,
                                                  url_detail)

    music_file = BytesIO()
    try:
        music_caption = "曲目: {0}\n演唱: {1}".format(
            music_obj.name, music_obj.singer.name
        )
        music_filename = '{0} - {1}.mp3'.format(
            music_obj.singer.name, music_obj.name)
        sing5_url = 'http://5sing.kugou.com/{0}/{1}.html'.format(music_obj.mtype, music_obj.mid)

        # 查询数据库 compare the files with the database ,and find the file_Id
        file_id = db_audio.DBAudio().compare_file(music_id, music_filename, 0, '', time.time())
        if file_id:
            send_music_file(bot, query, file_id, music_obj.mid, music_filename, music_caption,
                            edited_msg,
                            sing5_url)
        else:
            download_continuous(bot, query, music_obj.url, music_file, music_filename, edited_msg,
                                false_download_url=sing5_url)

            music_file = BytesIO(music_file.getvalue())
            music_file.name = music_filename

            send_music_file(bot, query, music_file, music_obj.mid, music_filename, music_caption,
                            edited_msg,
                            sing5_url)


    except:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
        if edited_msg:
            edited_msg.delete()
