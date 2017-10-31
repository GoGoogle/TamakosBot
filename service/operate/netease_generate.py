import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from model.music.album import Album
from model.music.artist import Artist
from model.music.music import Music
from model.music.musics_selector import MusicListSelector
from model.music.mv import Mv
from service.apis import netease_api

logger = logging.getLogger(__name__)


def generate_mv(mvid):
    mv_detail = netease_api.get_mv_detail_by_mvid(mvid)['data']
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
