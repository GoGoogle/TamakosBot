import logging
import time

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import application
from entity.sing5 import MusicTopSelector, Song, Singer
from service import sing5_api

logger = logging.getLogger(__name__)
tool_proxies = application.TOOL_PROXY


def generate_music_obj(detail, url_detail):
    url = ''
    size = 0
    false_url = 'http://5sing.kugou.com/{0}/{1}.html'.format(detail['SK'], detail['ID'])
    index1 = detail['squrl']
    index2 = detail['hqurl']
    index3 = detail['lqurl']
    if index1:
        url = index1
        size = detail['sqsize']
    elif index2:
        url = index2
        size = detail['hqsize']
    elif index3:
        url = index3
        size = detail['lqsize']

    music_obj = Song(detail['ID'], detail['SN'], url, Singer(detail['user']['ID'], detail['user']['NN']),
                     mtype=detail['SK'], size=size, falseurl=false_url)
    return music_obj


def produce_single_music_selector(kw, pagecode, musics_result):
    pass


def transfer_single_music_selector_to_panel(music_list_selector):
    pass


def produce_music_top_selector(mtype, pagecode, musics_result):
    logger.info('produce_music_top_selector, mtype:{0}-pagecode:{1}'.format(mtype, pagecode))
    musics = []
    songs = musics_result['data']['songs']
    for x in songs:
        s = Song(x['ID'], x['SN'], singer=Singer(x['user']['ID'], x['user']['NN']), mtype=mtype)
        musics.append(s)

    return MusicTopSelector(musics_result['data']['id'],
                            musics_result['data']['name'],
                            pagecode,
                            musics_result['data']['count'],
                            musics
                            )


def transfer_music_top_selector_to_panel(top_selector):
    caption_text = '️5sing 🎵「{0}」p: {1}/{2}'.format(
        top_selector.title,
        top_selector.cur_page_code,
        top_selector.total_songs_num
    )

    button_list = []
    for x in top_selector.musics:
        button_list.append([
            InlineKeyboardButton(
                text='{0} ({1})'.format(
                    x.name, x.singer.name),
                callback_data='sing5:{0}:t{1}'.format(top_selector.mtype, x.mid)
            )
        ])
    every_page_size = 5
    if top_selector.total_songs_num == 50:
        every_page_size = 50

    if top_selector.total_songs_num <= every_page_size:
        # 什么都不做
        pass
    elif top_selector.cur_page_code == 1:
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='sing5:{0}:+{1}'.format(top_selector.mtype, top_selector.cur_page_code)
            )
        ])
    elif top_selector.cur_page_code == top_selector.total_songs_num:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='sing5:{0}:-{1}'.format(top_selector.mtype, top_selector.cur_page_code)
            )
        ])
    else:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='sing5:{0}:-{1}'.format(top_selector.mtype, top_selector.cur_page_code)
            ),
            InlineKeyboardButton(
                text='下一页',
                callback_data='sing5:{0}:+{1}'.format(top_selector.mtype, top_selector.cur_page_code)
            )
        ])
    button_list.append([
        InlineKeyboardButton(
            text='撤销显示',
            callback_data='sing5:*'
        )
    ])

    return {'text': caption_text, 'reply_markup': InlineKeyboardMarkup(button_list)}


def selector_page_turning(bot, query, mtype, page_code):
    logger.info('selector_page_turning: mtype: {0}; page_code={1}'.format(mtype, page_code))
    musics_result = sing5_api.get_music_top_by_type_pagecode_and_date(mtype=mtype, pagecode=page_code)
    top_selector = produce_music_top_selector(mtype, page_code, musics_result)
    panel = transfer_music_top_selector_to_panel(top_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=application.TIMEOUT)


def download_continuous(bot, query, music_obj, music_file, edited_msg):
    try:
        if tool_proxies:
            # 代理使用国内服务器转发接口
            r = requests.get(music_obj.url, stream=True, proxies=tool_proxies)
        else:
            r = requests.get(music_obj.url, stream=True)

        logger.info('{0} 下载中,url={1}'.format(music_obj.name, music_obj.url))

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
