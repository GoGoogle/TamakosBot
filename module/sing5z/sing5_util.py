import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import application
from entity.bot_telegram import TopListSelector, ButtonItem, SongFile
from interface.song.util import UtilZ


class Util(UtilZ):
    def __init__(self):
        super().__init__()

    def get_toplist_selector(self, curpage, toplist):
        self.logger.debug('get_toplist_selector: keyword={0}, pagecode={1}'.format(toplist.top_name, curpage))

        total_page = (toplist.track_count + 4) // 5
        title = '🍏 榜单 「{0}」p: {1}/{2}'.format(
            toplist.top_name, curpage, total_page)

        return TopListSelector(title, curpage, total_page, toplist)

    def produce_toplist_panel(self, module_name, toplist_selector):
        button_list = []

        for x in toplist_selector.toplist.songs:
            """ButtonItem 这里用 search_type 指代原 page属性"""
            time_fmt = '{0}:{1:0>2d}'.format(int(x.song_duration // 60), int(x.song_duration % 60))
            button_list.append([
                InlineKeyboardButton(
                    text='[{0}] {1} ({2})'.format(
                        time_fmt, x.song_name, ' / '.join(v.artist_name for v in x.artists)),
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_SEND,
                                             x.song_id, toplist_selector.toplist.top_id).dump_json()
                )
            ])

        if toplist_selector.total_page == 1 or toplist_selector.total_page == 10:
            # 什么都不做
            pass
        elif toplist_selector.cur_page == 1:
            button_list.append([
                InlineKeyboardButton(
                    text='下一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_PAGE_DOWN,
                                             toplist_selector.toplist.top_id,
                                             toplist_selector.cur_page).dump_json()
                )
            ])
        elif toplist_selector.cur_page == toplist_selector.total_page:
            button_list.append([
                InlineKeyboardButton(
                    text='上一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_PAGE_UP,
                                             toplist_selector.toplist.top_id,
                                             toplist_selector.cur_page).dump_json()
                )
            ])
        else:
            button_list.append([
                InlineKeyboardButton(
                    text='上一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_PAGE_UP,
                                             toplist_selector.toplist.top_id,
                                             toplist_selector.cur_page).dump_json()
                ),
                InlineKeyboardButton(
                    text='下一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_PAGE_DOWN,
                                             toplist_selector.toplist.top_id,
                                             toplist_selector.cur_page).dump_json()
                )
            ])

        button_list.append([
            InlineKeyboardButton(
                text='撤销显示',
                callback_data=ButtonItem(module_name, ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_CANCEL).dump_json()
            )
        ])

        return {'text': toplist_selector.title, 'reply_markup': InlineKeyboardMarkup(button_list)}

    def get_songfile(self, song):
        file_name = r'{0} - {1}{2}'.format(
            song.song_name, ' & '.join(v.artist_name for v in song.artists), os.path.splitext(song.song_url)[1])
        file_name = file_name.replace("/", ":")
        file_path = os.path.join(application.TMP_Folder, file_name)
        file_url = song.song_url
        file_stream = open(file_path, 'wb+')
        song = song
        return SongFile(file_name, file_path, file_url, file_stream, song)
