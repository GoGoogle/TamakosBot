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
from io import BytesIO
from service.netease import api
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


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
                                           reply_to_message_id=query.message.reply_to_message.message_id)
    music_detail_dict = api.get_music_detail_by_musicid(music_id)
    music_url_dict = api.get_music_url_by_musicid(music_id)

    music_obj = generate_music_obj(music_detail_dict['songs'][0], music_url_dict['data'][0])
    download_music_file(bot, query, require_msg, music_obj)


def download_music_file(bot, query, require_msg, music_obj):
    netease_url = 'http://music.163.com/song?id={}'.format(music_obj.mid)
    file = BytesIO()
    try:
        r = requests.get(music_obj.url, stream=True, timeout=TIMEOUT)
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
            progress_status = '{0}\n{1}\n{2}'.format(netease_url, 'mp3下载中~', progress)

            bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=require_msg.message_id,
                text=progress_status,
                reply_to_message_id=query.message.reply_to_message.message_id,
                caption='',
                disable_notification=True,
                timeout=TIMEOUT
            )

    except Exception as e:
        logger.error('download file error: {}'.format(e))

    file = BytesIO(file.getvalue())
    file.name = '{0} - {1}'.format(
        ' / '.join(v.name for v in music_obj.artists), music_obj.name)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=require_msg.message_id,
        text='{}\nmp3发送中~'.format(netease_url),
        reply_to_message_id=query.message.reply_to_message.message_id,
        caption='',
        disable_notification=True,
        timeout=TIMEOUT
    )

    caption = "标题: {0}\n艺术家: #{1}\n专辑: {2}\n格式: {3}\n☁️ID: {4}".format(
        music_obj.name, ' #'.join(v.name for v in music_obj.artists),
        music_obj.album.name, music_obj.scheme, music_obj.mid
    )
    try:
        bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO, timeout=TIMEOUT)
        logger.info("文件：{}，正在发送中~".format(file.name))
        bot.send_audio(chat_id=query.message.chat.id, audio=file, caption=caption,
                       title=file.name,
                       reply_to_message_id=query.message.reply_to_message.message_id,
                       timeout=TIMEOUT)
    except Exception as e:
        logger.error('send file error: {}'.format(e))
    finally:
        if not file.closed:
            file.close()
        require_msg.delete()
