import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from model.music import Mv, Artist, Album, Music, MusicListSelector, PlayListSelector
from service.apis import netease_api

logger = logging.getLogger(__name__)


def generate_mv(mvid):
    mv_detail = netease_api.get_mv_detail_by_mvid(mvid)['data']
    max_key = str(max(map(lambda x: int(x), mv_detail['brs'].keys())))
    return Mv(mv_detail['id'], mv_detail['name'], mv_detail['brs'][max_key],
              mv_detail['artistName'], mv_detail['duration'] / 60000, quality=max_key)


def generate_music_obj(detail, url):
    ars = []
    if len(detail['ar']) > 0:
        for x in detail['ar']:
            ars.append(Artist(arid=x['id'], name=x['name']))
    al = Album(detail['al']['name'], int(detail['al']['id']))

    music_obj = Music(mid=detail['id'], name=detail['name'], url=url['url'],
                      scheme='{0} {1:.0f}kbps'.format(url['type'], url['br'] / 1000),
                      artists=ars, duration=detail['dt'] / 1000, album=al
                      )
    if detail['mv'] != 0:
        mv = generate_mv(detail['mv'])
        music_obj.mv = mv
    return music_obj


def produce_music_list_selector(kw, pagecode, search_musics_result):
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

        music = Music(song['id'], song['name'], artists=ars, duration=song['duration'] / 60000)
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
                    x.duration, x.name, ' / '.join(v.name for v in x.artists)),
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


def produce_playlist_selector(playlist):
    musics = []
    for song in playlist['tracks']:
        ars = []
        if len(song['ar']) > 0:
            for x in song['ar']:
                ars.append(Artist(arid=x['id'], name=x['name']))
        music = Music(song['id'], song['name'], artists=ars, duration=song['dt'] / 60000)
        musics.append(music)

    total_page_num = (playlist['trackCount'] + 4) // 5

    return PlayListSelector(playlist['id'], playlist['name'], playlist['creator']['nickname'],
                            playlist['trackCount'], total_page_num, musics)


def transfer_playlist_selector_to_panel(playlist_selector, cur_pagecode=1):
    playlist_url = 'http://music.163.com/playlist/{}'.format(playlist_selector.pid)
    list_text = "☁️🎵歌单 「[{0}]({1})」\n创建者 {2}\n歌曲数目 {3} 首歌".format(
        playlist_selector.name, playlist_url, playlist_selector.creator_name, playlist_selector.track_count)
    button_list = []
    start = cur_pagecode * 5 - 5
    music_list = playlist_selector.musics[start:start + 5]

    for x in music_list:
        button_list.append([
            InlineKeyboardButton(
                text='[{0:.2f}] {1} ({2})'.format(
                    x.duration, x.name, ' / '.join(v.name for v in x.artists)),
                callback_data='netease:P' + str(x.mid)
            )
        ])

    if cur_pagecode == 1:
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
