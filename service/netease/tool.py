import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from entity.music.artist import Artist
from entity.music.music import Music
from entity.music.music_list_selector import MusicListSelector

logger = logging.getLogger(__name__)


def produce_music_list_selector(kw, pagecode, search_musics_result):
    """
    generate music_list_selector by netease api
    :param search_musics_result: the return value from '/search' api
    :return: music_list_selector
    """
    logger.debug('generate_music_list_selector: keyword={0}, pagecode={1}'.format(kw, pagecode))
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
                callback_data=x.mid
            )
        ])
    if music_list_selector.cur_page_code == 1:
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='+{}'.format(music_list_selector.cur_page_code)
            )
        ])
    elif music_list_selector.cur_page_code == music_list_selector.total_page_num:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='-{}'.format(music_list_selector.cur_page_code)
            )
        ])
    else:
        button_list.append([
            InlineKeyboardButton(
                text='上一页',
                callback_data='-{}'.format(music_list_selector.cur_page_code)
            )
        ])
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='+{}'.format(music_list_selector.cur_page_code)
            )
        ])

    return {'text': list_text, 'reply_markup': InlineKeyboardMarkup(button_list)}
