import logging
import time
from io import BytesIO

import requests
import telegram

from common import application
from common.application import TIMEOUT
from service.apis import netease_api
from service.operate import netease_generate

logger = logging.getLogger(__name__)


def download_continuous(bot, query, true_download_url, file, file_title, edited_msg,
                        false_download_url=''):
    try:
        if application.TOOL_PROXY:
            # 代理使用国内服务器转发接口
            logger.info('**start proxy :: {0}.....'.format(application.TOOL_PROXY['protocol']))
            proxies = {
                application.TOOL_PROXY['protocol']: application.TOOL_PROXY['host'],
            }
            r = requests.get(true_download_url, stream=True, timeout=TIMEOUT, proxies=proxies)
        else:
            r = requests.get(true_download_url, stream=True, timeout=TIMEOUT)

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
            progress_status = '[{0}]({1})  ..下载中\n{2}'.format(file_title, false_download_url, progress)

            bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=edited_msg.message_id,
                text=progress_status,
                disable_web_page_preview=True,
                parse_mode=telegram.ParseMode.MARKDOWN,
                timeout=TIMEOUT
            )

    except Exception as e:
        logger.error('download_continuous failed', exc_info=True)


def send_music_file(bot, query, file, file_name, file_caption, edited_msg, false_download_url=''):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='[{0}]({1}) >> 发送中'.format(file_name, false_download_url),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        timeout=TIMEOUT
    )

    logger.info("文件：{}，>> 正在发送中".format(file_name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)

    bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=file_caption,
                   title=file_name[:file_name.rfind('.')],
                   timeout=TIMEOUT)


def selector_page_turning(bot, query, kw, page_code):
    logger.info('selector_page_turning: keyword: {0}; page_code={1}'.format(kw, page_code))
    search_musics_dict = netease_api.search_musics_by_keyword_and_pagecode(kw, pagecode=page_code)
    music_list_selector = netease_generate.produce_music_list_selector(kw, page_code, search_musics_dict['result'])
    panel = netease_generate.transfer_music_list_selector_to_panel(music_list_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=TIMEOUT)


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text=".",
                            show_alert=False,
                            timeout=TIMEOUT)
    query.message.delete()


def selector_send_music(bot, query, music_id, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        selector_cancel(bot, query)

    edited_msg = bot.send_message(chat_id=query.message.chat.id, text="..获取中",
                                  timeout=TIMEOUT)
    detail = netease_api.get_music_detail_by_musicid(music_id)['songs'][0]
    br = ''
    if 'h' in detail:
        br = detail['h']['br']
    elif 'm' in detail:
        br = detail['m']['br']
    elif 'l' in detail:
        br = detail['l']['br']
    music_obj = netease_generate.generate_music_obj(detail,
                                                    netease_api.get_music_url_by_musicid(music_id)['data'][0])

    music_file = BytesIO()
    try:
        music_caption = "曲目: {0}\n演唱: {1}\n专辑: {2}]\n格式：{3}\n☁️ID: {4}".format(
            music_obj.name, ' '.join(v.name for v in music_obj.artists),
            music_obj.album.name, music_obj.scheme, music_obj.mid
        )
        music_filename = '{0} - {1}.mp3'.format(
            ' / '.join(v.name for v in music_obj.artists), music_obj.name)
        netease_url = 'http://music.163.com/song?id={}'.format(music_obj.mid)

        if query.message.audio and query.message.audio.title == music_filename[:music_filename.rfind('.')]:
            send_music_file(bot, query, query.message.audio, music_filename, music_caption, edited_msg, netease_url)
        else:
            download_continuous(bot, query, music_obj.url, music_file, music_filename, edited_msg,
                                false_download_url=netease_url)

            music_file = BytesIO(music_file.getvalue())
            music_file.name = music_filename

            send_music_file(bot, query, music_file, music_filename, music_caption, edited_msg, netease_url)

        if music_obj.mv:
            logger.info('selector download MV: mvid={0}'.format(music_obj.mv.mid))

            mv_caption = "标题: {0}\n演唱: {1}\n品质: {2}p\n☁️ID: {3}".format(
                music_obj.mv.name, music_obj.mv.artist_name,
                music_obj.mv.quality, music_obj.mv.mid
            )

            mv_file_fullname = '{0} - {1}.mp4'.format(
                music_obj.mv.artist_name, music_obj.mv.name)

            mv_true_url = netease_api.get_mv_true_url_by_mv_url(music_obj.mv.url)  # true url
            message_text = '[{0}]({1}) MV 已发送~\n{2}'.format(mv_file_fullname, mv_true_url, mv_caption)

            bot.send_message(chat_id=query.message.chat.id, text=message_text, parse_mode=telegram.ParseMode.MARKDOWN)

    except Exception as e:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
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
