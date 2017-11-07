import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from entity.sing5 import MusicTopSelector, Song, Singer

logger = logging.getLogger(__name__)


def generate_music_obj(detail, url_detail):
    url = ''
    size = 0
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
                     mtype=detail['SK'], size=size)
    return music_obj


def produce_music_list_selector(kw, pagecode, musics_result):
    pass


def transfer_music_list_selector_to_panel(music_list_selector):
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
                            100,
                            musics
                            )


def transfer_music_top_selector_to_panel(top_selector):
    caption_text = '️5sing 🎵「{0}」p: {1}/{2}'.format(
        top_selector.title,
        top_selector.cur_page_code,
        top_selector.total_page_num
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
    if top_selector.cur_page_code == 1:
        button_list.append([
            InlineKeyboardButton(
                text='下一页',
                callback_data='sing5:{0}:+{1}'.format(top_selector.mtype, top_selector.cur_page_code)
            )
        ])
    elif top_selector.cur_page_code == top_selector.total_page_num:
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
