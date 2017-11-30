import logging
import os
import telegram

from config import application
from module.sing5z import sing5_util, sing5_api
from util import song_util

logger = logging.getLogger(__name__)


class Sing5z(object):
    pass


def search_music(bot, update, args):
    try:
        f_type = 2
        key_word = args[1]

        if len(args) == 2:
            f_type = args[1]
            key_word = args[2]

        logger.info('get_music: {}'.format(key_word))
        musics_dict = sing5_api.search_musics_by_keyword_pagecode_and_filter(key_word, pagecode=1, filter_type=f_type)
        if len(musics_dict['data']['songArray']) == 0:
            text = "此歌曲找不到~"
            update.message.reply_text(text=text)
        else:
            music_list_selector = sing5_util.produce_single_music_selector(key_word, 1,
                                                                           musics_dict['data']['songArray'])
            panel = sing5_util.transfer_single_music_selector_to_panel(music_list_selector)
            update.message.reply_text(text=panel['text'], quote=True, reply_markup=panel['reply_markup'])

    except IndexError:
        text = "缺少歌曲名称"
        update.message.reply_text(text=text)
    except Exception as e:
        logger.error('search music error', exc_info=True)


def response_single_music(bot, update):
    logger.info('sing5 listen_selector_reply: data={}'.format(update.callback_query.data))
    query = update.callback_query
    index1 = query.data.find('*')
    index2 = query.data.find('+')
    index3 = query.data.find('-')
    index4 = query.data.find('t')
    if index1 != -1:
        song_util.selector_cancel(bot, query)
    elif index2 != -1:
        page_code = int(query.data[index2 + 1:]) + 1
        mtype = query.data[6:index2 - 1]
        sing5_util.selector_page_turning(bot, query, mtype, page_code)
    elif index3 != -1:
        page_code = int(query.data[index3 + 1:]) - 1
        mtype = query.data[6:index3 - 1]
        sing5_util.selector_page_turning(bot, query, mtype, page_code)
    else:
        music_id = int(query.data[index4 + 1:])
        mtype = query.data[6:index4 - 1]
        selector_send_music(bot, query, music_id, mtype, False)


def response_toplist(bot, update, payload='yc'):
    try:
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="喵~")
        update.message.message_id = edited_msg.message_id

        musics_result = sing5_api.get_music_top_by_type_pagecode_and_date(mtype=payload, pagecode=1)
        top_selector = sing5_util.produce_music_top_selector(payload, 1, musics_result)
        panel = sing5_util.transfer_music_top_selector_to_panel(top_selector)
        bot.edit_message_text(chat_id=update.message.chat.id,
                              message_id=update.message.message_id,
                              text=panel['text'], quote=True,
                              disable_web_page_preview=True,
                              reply_markup=panel['reply_markup'])
    except Exception as e:
        logger.error('search music error', exc_info=True)


def selector_send_music(bot, query, music_id, mtype, delete):
    logger.info('selector_download_music: music_id={0}'.format(music_id))
    if delete:
        song_util.selector_cancel(bot, query)

    #
    detail = sing5_api.get_music_detail_by_id_and_type(music_id, song_type=mtype)['data']
    url_detail = sing5_api.get_music_url_by_id_and_type(music_id, mtype)['data']

    # 转为对象好处理
    music_obj = sing5_util.generate_music_obj(detail,
                                              url_detail)

    edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                  text="找到歌曲: [{0}]({1})".format(music_obj.name, music_obj.url),
                                  parse_mode=telegram.ParseMode.MARKDOWN)

    # music_caption = "曲目: {0}\n演唱: {1}".format(
    #     music_obj.name, music_obj.singer.name
    # )
    music_caption = ''
    full_file_name = r'{0} - {1}.mp3'.format(
        music_obj.name, music_obj.singer.name)
    # 字符串进行处理
    full_file_name = full_file_name.replace("/", ":")
    music_file_path = os.path.join(application.TMP_Folder, full_file_name)
    music_file = open(music_file_path, 'wb+')

    try:
        sing5_util.download_continuous(bot, query, music_obj, music_file, edited_msg)

        # 填写 id3tags
        song_util.write_id3tags(music_file_path, song_title=music_obj.name,
                                song_artist_list=[music_obj.singer.name], song_album='5sing 音乐')

        music_file.seek(0, os.SEEK_SET)  # 从开始位置开始读

        send_music_file(bot, query, music_file, music_obj, music_caption, edited_msg)
    except:
        logger.error('send file failed', exc_info=True)
    finally:
        if not music_file.closed:
            music_file.close()
        if os.path.exists(music_file_path):
            os.remove(music_file_path)
        if edited_msg:
            edited_msg.delete()


def send_music_file(bot, query, music_file, music_obj, file_caption, edited_msg):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=edited_msg.message_id,
        text='5sing {0} 等待发送'.format(music_obj.name),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

    logger.info("文件: {} >> 正在发送中".format(music_obj.name))
    bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)

    file_msg = None
    try:
        file_msg = bot.send_audio(chat_id=query.message.chat.id, audio=music_file, caption=file_caption,
                                  duration=music_obj.duration,
                                  title=music_obj.name,
                                  performer=music_obj.singer.name,
                                  disable_notification=True,
                                  timeout=application.FILE_TRANSFER_TIMEOUT)

        logger.info("文件: {} 发送成功.".format(music_obj.name))
    except:
        if file_msg:
            file_msg.delete()
        logger.error('send audio file failed', exc_info=True)
