import logging

import requests
import time
import telegram

from common import config
from common.config import TIMEOUT
from entity.music.album import Album
from entity.music.artist import Artist
from entity.music.music import Music
from entity.music.music_list_selector import MusicListSelector
from entity.music.mv import Mv
from io import BytesIO
from service.netease import api
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

proxies = {
    "http": config.TOOL_PROXY,
}


def generate_mv(mvid):
    mv_detail = api.get_mv_detail_by_mvid(mvid)['data']
    max_key = str(max(map(lambda x: int(x), mv_detail['brs'].keys())))
    return Mv(mv_detail['id'], mv_detail['name'], mv_detail['brs'][max_key],
              mv_detail['artistName'], mv_detail['duration'], quality=max_key)


def generate_music_obj(detail, url):
    ars = []
    if len(detail['ar']) > 0:
        for x in detail['ar']:
            ars.append(Artist(arid=x['id'], name=x['name']))
    al = Album(detail['al']['name'], detail['al']['id'])

    music_obj = Music(mid=detail['id'], name=detail['name'], url=url['url'],
                      scheme='{0} {1:.0f}kbps'.format(url['type'], url['br'] / 1000),
                      artists=ars, duration=detail['dt'], album=al
                      )
    if detail['mv'] != 0:
        mv = generate_mv(detail['mv'])
        music_obj.mv = mv
    return music_obj


def produce_music_list_selector(kw, pagecode, search_musics_result):
    """
    generate music_list_selector by netease api
    :param kw: search keyword
    :param pagecode: current page code
    :param search_musics_result: the return value from '/search' api
    :return: music_list_selector
    """
    logger.info('generate_music_list_selector: keyword={0}, pagecode={1}'.format(kw, pagecode))
    musics = []
    for song in search_musics_result['songs']:
        ars = []
        if len(song['artists']) > 0:
            for x in song['artists']:
                ars.append(Artist(arid=x['id'], name=x['name']))

        music = Music(song['id'], song['name'], artists=ars, duration=song['duration'])
        musics.append(music)
    total_page_num = (search_musics_result['songCount'] + 4) // 5
    return MusicListSelector(kw, pagecode, total_page_num, musics)


def transfer_music_list_selector_to_panel(music_list_selector):
    list_text = '☁️🎵关键字「{0}」p: {1}/{2}'.format(
        music_list_selector.keyword,
        music_list_selector.cur_page_code,
        music_list_selector.total_page_num
    )
    button_list = []
    music_list = music_list_selector.musics
    for x in music_list:
        button_list.append([
            InlineKeyboardButton(
                text='[{0:.2f}] {1} ({2})'.format(
                    x.duration / 60000, x.name, ' / '.join(v.name for v in x.artists)),
                callback_data='netease:' + str(x.mid)
            )
        ])
    if music_list_selector.cur_page_code == 1:
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='netease:{0}:+{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            )
        ])
    elif music_list_selector.cur_page_code == music_list_selector.total_page_num:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='netease:{0}:-{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            )
        ])
    else:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='netease:{0}:-{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            ),
            InlineKeyboardButton(
                text='下一页',
                callback_data='netease:{0}:+{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            )
        ])
    button_list.append([
        InlineKeyboardButton(
            text='取消',
            callback_data='netease:*'
        )
    ])

    return {'text': list_text, 'reply_markup': InlineKeyboardMarkup(button_list)}


def selector_page_turning(bot, query, kw, page_code):
    bot.answerCallbackQuery(query.id,
                            text="加载中~",
                            show_alert=False,
                            timeout=TIMEOUT)
    logger.info('selector_page_turning: keyword: {0}; page_code={1}'.format(kw, page_code))
    search_musics_dict = api.search_musics_by_keyword_and_pagecode(kw, pagecode=page_code)
    music_list_selector = produce_music_list_selector(kw, page_code, search_musics_dict['result'])
    panel = transfer_music_list_selector_to_panel(music_list_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=TIMEOUT)


def selector_cancel(bot, query):
    bot.answerCallbackQuery(query.id,
                            text="加载中~",
                            show_alert=False,
                            timeout=TIMEOUT)
    query.message.delete()


def selector_send_music(bot, query, music_id):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    selector_cancel(bot, query)
    require_msg = query.message.reply_text(text="获取中~",
                                           timeout=TIMEOUT,
                                           quote=True,
                                           reply_to_message_id=query.message.reply_to_message.message_id)
    song_detail_dict = api.get_music_detail_by_musicid(music_id)
    song_url_dict = api.get_music_url_by_musicid(music_id)
    music_obj = generate_music_obj(song_detail_dict['songs'][0], song_url_dict['data'][0])

    download_music_file(bot, query, require_msg, music_obj)


def download_music_file(bot, query, last_msg, music_obj):
    music_file = BytesIO()
    mv_file = BytesIO()
    try:
        # download music
        netease_url = 'http://music.163.com/song?id={}'.format(music_obj.mid)
        memory1 = BytesIO()

        music_caption = "标题: {0}\n艺术家: #{1}\n专辑: {2}\n格式: {3}\n☁️ID: {4}".format(
            music_obj.name, ' #'.join(v.name for v in music_obj.artists),
            music_obj.album.name, music_obj.scheme, music_obj.mid
        )
        file_fullname = '{0} - {1}.mp3'.format(
            ' / '.join(v.name for v in music_obj.artists), music_obj.name)

        if query.message.audio and query.message.audio.title == file_fullname[:-4]:
            logger.info('****************query.message.audio.title={0}, file_id ={1}', query.message.audio.title,
                        query.message.audio.file_id)
            send_file(bot, query, last_msg, query.message.audio, file_fullname, 'mp3',
                      telegram.ChatAction.UPLOAD_AUDIO,
                      music_caption, netease_url)
        else:

            download_continue(bot, query, music_obj.url, memory1,
                              last_msg, 'mp3', false_download_url=netease_url)

            music_file = BytesIO(memory1.getvalue())
            music_file.name = file_fullname

            send_file(bot, query, last_msg, music_file, file_fullname, 'mp3', telegram.ChatAction.UPLOAD_AUDIO,
                      music_caption, netease_url)

        # download mv
        logger.info('selector_download_music: mvid={0}'.format(music_obj.mv.mid))
        if music_obj.mv:
            logger.info('download mv={} start...'.format(music_obj.mv.mid))

            memory2 = BytesIO()

            mv_caption = "标题: {0}\n艺术家: #{1}\n品质: {2}\n☁️ID: {3}".format(
                music_obj.mv.name, music_obj.mv.artist_name,
                music_obj.mv.quality, music_obj.mv.mid
            )

            mv_file_fullname = '{0} - {1}.mp4'.format(
                music_obj.mv.artist_name, music_obj.mv.name)

            if query.message.video and query.message.video.title == mv_file_fullname[:-4]:
                logger.info('****************query.message.video.title={0}, file_id ={1}', query.message.video.title,
                            query.message.video.file_id)
                send_file(bot, query, last_msg, query.message.video, mv_file_fullname, 'mp4',
                          telegram.ChatAction.UPLOAD_VIDEO,
                          mv_caption, music_obj.mv.url)
            else:
                # true url
                mv_true_url = api.get_mv_true_url_by_mv_url(music_obj.mv.url)
                download_continue(bot, query, mv_true_url, memory2,
                                  last_msg, 'mp4', false_download_url=music_obj.mv.url)

                mv_file = BytesIO(memory2.getvalue())
                mv_file.name = mv_file_fullname
                send_file(bot, query, last_msg, mv_file, mv_file_fullname, 'mp4', telegram.ChatAction.UPLOAD_VIDEO,
                          mv_caption, music_obj.mv.url)

    except Exception as e:
        logger.error('send file error: {}'.format(e))
    finally:
        if not music_file.closed:
            music_file.close()
        if not mv_file.closed:
            mv_file.close()
        last_msg.delete()


def download_continue(bot, query, true_download_url, file, last_msg, file_type='document', false_download_url=''):
    try:
        # 代理使用国内服务器转发接口
        logger.info('***********************true_download_url={0}'.format(true_download_url))
        if proxies['http']:
            r = requests.get(true_download_url, stream=True, timeout=TIMEOUT, proxies=proxies)
        else:
            r = requests.get(true_download_url, stream=True, timeout=TIMEOUT)
        start = time.time()
        total_length = int(r.headers.get('content-length'))
        dl = 0
        for chunk in r.iter_content(config.CHUNK_SIZE):
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
            progress_status = '{0}\n{1}下载中~\n{2}'.format(false_download_url, file_type, progress)

            bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=last_msg.message_id,
                text=progress_status,
                quote=True,
                reply_to_message_id=query.message.reply_to_message.message_id,
                caption='',
                disable_web_page_preview=True,
                timeout=TIMEOUT
            )

    except Exception as e:
        logger.error('download file error: {}'.format(e))


def send_file(bot, query, last_msg, file, file_name, file_suffix, telegram_action, file_caption, false_download_url=''):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=last_msg.message_id,
        text='{0}\n{1} 发送中~'.format(false_download_url, file_suffix),
        quote=True,
        reply_to_message_id=query.message.reply_to_message.message_id,
        caption='',
        disable_web_page_preview=True,
        timeout=TIMEOUT
    )

    logger.info("文件：{}，正在发送中~".format(file_name))
    bot.send_chat_action(query.message.chat.id, action=telegram_action)

    suffix_length = len(file_suffix) + 1
    if file_suffix in ['mp3', 'audio']:
        bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=file_caption,
                       title=file_name[:-suffix_length],
                       quote=True,
                       reply_to_message_id=query.message.reply_to_message.message_id,
                       timeout=TIMEOUT)

    if file_suffix in ['mp4', 'video']:
        bot.send_video(chat_id=query.message.chat.id, video=file, caption=file_caption,
                       title=file_name[:-suffix_length],
                       quote=True,
                       reply_to_message_id=query.message.reply_to_message.message_id,
                       timeout=TIMEOUT)
