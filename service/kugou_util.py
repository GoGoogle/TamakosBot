import logging
import time

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import application
from entity.kugou import Music, MusicListSelector
from service import kugou_api

logger = logging.getLogger(__name__)


def generate_music_obj(detail, hq_detail):
    music_obj = Music(detail['hash'], detail['songName'], detail['url'], detail['extName'],
                      detail['bitRate'], duration=detail['timeLength'], mhash=detail['hash'],
                      singer_name=detail['singerName'])

    return music_obj


def produce_single_music_selector(kw, pagecode, search_musics_result):
    logger.info('generate_music_list_selector: keyword={0}, pagecode={1}'.format(kw, pagecode))
    musics = []
    for song in search_musics_result['info']:
        mhash = song['hash']
        if song['sqhash']:
            mhash = song['sqhash']
        music = Music(song['audio_id'], song['songname'], url='', suffix=song['extname'],
                      bitrate=song['bitrate'], duration=song['duration'], mhash=mhash,
                      singer_name=song['singername'], album_name=song['album_name'])
        musics.append(music)
    total_page_num = (search_musics_result['total'] + 4) // 5
    return MusicListSelector(kw, pagecode, total_page_num, musics)


def transfer_single_music_selector_to_panel(music_list_selector):
    list_text = 'Kg  ️🎵关键字「{0}」p: {1}/{2}'.format(
        music_list_selector.keyword,
        music_list_selector.cur_page_code,
        music_list_selector.total_page_num
    )
    button_list = []
    music_list = music_list_selector.musics
    for x in music_list:
        # 跟 music_obj 无关
        time_fmt = '{0}:{1:0>2d}'.format(int(x.duration // 60), int(x.duration % 60))
        button_list.append([
            InlineKeyboardButton(
                text='[{0}] {1} ({2})'.format(
                    time_fmt, x.name, x.singer_name),
                callback_data='kg:' + str(x.mhash)
            )
        ])

    if music_list_selector.total_page_num == 1:
        # 什么都不做
        pass
    elif music_list_selector.cur_page_code == 1:
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='kg:{0}:+{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            )
        ])
    elif music_list_selector.cur_page_code == music_list_selector.total_page_num:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='kg:{0}:-{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            )
        ])
    else:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='kg:{0}:-{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            ),
            InlineKeyboardButton(
                text='下一页',
                callback_data='kg:{0}:+{1}'.format(music_list_selector.keyword, music_list_selector.cur_page_code)
            )
        ])
    button_list.append([
        InlineKeyboardButton(
            text='取消',
            callback_data='kg:*'
        )
    ])

    return {'text': list_text, 'reply_markup': InlineKeyboardMarkup(button_list)}


def selector_page_turning(bot, query, kw, page_code):
    logger.info('selector_page_turning: keyword: {0}; page_code={1}'.format(kw, page_code))
    search_musics_dict = kugou_api.search_music_by_keyword_and_pagecode(kw, pagecode=page_code)
    music_list_selector = produce_single_music_selector(kw, page_code, search_musics_dict['data'])
    panel = transfer_single_music_selector_to_panel(music_list_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=application.TIMEOUT)


def download_continuous(bot, query, music_obj, music_file, edited_msg, tool_proxies):
    try:
        if tool_proxies:
            r = requests.get(music_obj.url, stream=True, proxies=tool_proxies)
        else:
            r = requests.get(music_obj.url, stream=True)

        logger.info('{} ..持续下载'.format(music_obj.name))

        start = time.time()
        total_length = int(r.headers.get('content-length'))
        dl = 0
        for chunk in r.iter_content(application.CHUNK_SIZE):
            dl += len(chunk)
            music_file.write(chunk)

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
            progress_status = '{1}'.format(music_obj.name, progress)

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
