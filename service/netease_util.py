import logging
import time

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import application
from entity.netease import Mv, Artist, Album, Music, MusicListSelector, PlayListSelector
from service import netease_api

logger = logging.getLogger(__name__)


def generate_music_obj(detail, url):
    ars = []
    if len(detail['ar']) > 0:
        for x in detail['ar']:
            ars.append(Artist(arid=x['id'], name=x['name']))
    al = Album(detail['al']['name'], int(detail['al']['id']))

    music_obj = Music(mid=detail['id'], name=detail['name'], url=url['url'], suffix=url['type'],
                      scheme='{0:.0f}kbps'.format(url['br'] / 1000),
                      artists=ars, duration=detail['dt'] / 1000, album=al
                      )
    #  有问题
    # if detail['mv'] != 0:
    #     mv = generate_mv_obj(detail['mv'])
    #     music_obj.mv = mv
    return music_obj


def generate_mv_obj(mvid):
    mv_detail = netease_api.get_mv_detail_by_mvid(mvid)['data']
    max_key = str(max(map(lambda x: int(x), mv_detail['brs'].keys())))
    return Mv(mv_detail['id'], mv_detail['name'], mv_detail['brs'][max_key],
              mv_detail['artistName'], mv_detail['duration'] / 1000, quality=max_key)


def produce_single_music_selector(kw, pagecode, search_musics_result):
    """
    generate music_list_selector by netease apis
    :param kw: search keyword
    :param pagecode: current page code
    :param search_musics_result: the return value from '/search' apis
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


def transfer_single_music_selector_to_panel(music_list_selector):
    list_text = '163 ️🎵关键字「{0}」p: {1}/{2}'.format(
        music_list_selector.keyword,
        music_list_selector.cur_page_code,
        music_list_selector.total_page_num
    )
    button_list = []
    music_list = music_list_selector.musics
    for x in music_list:
        # 跟 music_obj 无关
        time_fmt = '{0}:{1:0>2d}'.format(int(x.duration / 1000 // 60), int(x.duration / 1000 % 60))
        button_list.append([
            InlineKeyboardButton(
                text='[{0}] {1} ({2})'.format(
                    time_fmt, x.name, ' / '.join(v.name for v in x.artists)),
                callback_data='netease:' + str(x.mid)
            )
        ])

    if music_list_selector.total_page_num == 1:
        # 什么都不做
        pass
    elif music_list_selector.cur_page_code == 1:
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


def produce_playlist_selector(playlist):
    musics = []
    for song in playlist['tracks']:
        ars = []
        if len(song['ar']) > 0:
            for x in song['ar']:
                ars.append(Artist(arid=x['id'], name=x['name']))
        music = Music(song['id'], song['name'], artists=ars, duration=song['dt'])
        musics.append(music)

    total_page_num = (playlist['trackCount'] + 4) // 5

    return PlayListSelector(playlist['id'], playlist['name'], playlist['creator']['nickname'],
                            playlist['trackCount'], total_page_num, musics)


def transfer_playlist_selector_to_panel(playlist_selector, cur_pagecode=1):
    playlist_url = 'http://music.163.com/playlist/{}'.format(playlist_selector.pid)
    list_text = "163 🎵歌单 「[{0}]({1})」\n创建者 {2}\n歌曲数目 {3} 首歌".format(
        playlist_selector.name, playlist_url, playlist_selector.creator_name, playlist_selector.track_count)
    button_list = []
    start = cur_pagecode * 5 - 5
    music_list = playlist_selector.musics[start:start + 5]

    for x in music_list:
        time_fmt = '{0}:{1:0>2d}'.format(int(x.duration / 1000 // 60), int(x.duration / 1000 % 60))
        button_list.append([
            InlineKeyboardButton(
                text='[{0}] {1} ({2})'.format(
                    time_fmt, x.name, ' / '.join(v.name for v in x.artists)),
                callback_data='netease:P' + str(x.mid)
            )
        ])

    if playlist_selector.total_page_num == 1:
        # 什么都不做
        pass
    elif cur_pagecode == 1:
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='netease:{0}:D{1}'.format(playlist_selector.pid, cur_pagecode)
            )
        ])
    elif cur_pagecode == playlist_selector.total_page_num:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='netease:{0}:U{1}'.format(playlist_selector.pid, cur_pagecode)
            )
        ])
    else:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='netease:{0}:U{1}'.format(playlist_selector.pid, cur_pagecode)
            ),
            InlineKeyboardButton(
                text='下一页',
                callback_data='netease:{0}:D{1}'.format(playlist_selector.pid, cur_pagecode)
            )
        ])

    button_list.append([
        InlineKeyboardButton(
            text='撤销显示',
            callback_data='netease:*'
        )
    ])

    return {'text': list_text, 'reply_markup': InlineKeyboardMarkup(button_list)}


def selector_page_turning(bot, query, kw, page_code):
    logger.info('selector_page_turning: keyword: {0}; page_code={1}'.format(kw, page_code))
    search_musics_dict = netease_api.search_musics_by_keyword_and_pagecode(kw, pagecode=page_code)
    music_list_selector = produce_single_music_selector(kw, page_code, search_musics_dict['result'])
    panel = transfer_single_music_selector_to_panel(music_list_selector)
    query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'], timeout=application.TIMEOUT)


def selector_playlist_turning(bot, update, playlist_id, cur_pagecode=1):
    playlist_dict = netease_api.get_playlist_by_playlist_id(playlist_id)
    playlist_selector = produce_playlist_selector(playlist_dict['playlist'])
    panel = transfer_playlist_selector_to_panel(playlist_selector, cur_pagecode)
    bot.edit_message_text(chat_id=update.message.chat.id,
                          message_id=update.message.message_id,
                          text=panel['text'], quote=True, reply_markup=panel['reply_markup'],
                          disable_web_page_preview=True,
                          parse_mode=telegram.ParseMode.MARKDOWN)


def download_continuous(bot, query, music_obj, music_file, edited_msg, tool_proxies):
    try:
        if tool_proxies:
            r = requests.get(music_obj.url, stream=True, timeout=application.TIMEOUT, proxies=tool_proxies)
        else:
            r = requests.get(music_obj.url, stream=True, timeout=application.TIMEOUT)

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
