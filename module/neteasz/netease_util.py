import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import application
from entity.bot_telegram import SongListSelector, PlayListSelector, SongFile, ButtonItem
from interface.util import UtilZ


class Util(UtilZ):
    def __init__(self):
        super().__init__()

    def get_songlist_selector(self, curpage, songlist):
        """
        生成可供选择的歌曲选择器
        :param curpage: 当前页数
        :param songlist: 歌曲列表🎵
        :return: 歌曲列表选择器
        """
        self.logger.info('get_songlist_selector: keyword={0}, pagecode={1}'.format(songlist.keyword, curpage))
        total_page = (songlist.track_count + 4) // 5
        title = '163 ️🎵 关键字「{0}」p: {1}/{2}'.format(songlist.keyword, curpage, total_page)
        return SongListSelector(title, curpage, total_page, songlist)

    def produce_songlist_panel(self, module_name, songlist_selector):
        button_list = []
        # 由于 tg 对 callback_data 字数限制，必须对关键词进行切片
        songlist_selector.songlist.keyword = songlist_selector.songlist.keyword[:16]

        for x in songlist_selector.songlist.songs:
            time_fmt = '{0}:{1:0>2d}'.format(int(x.song_duration / 1000 // 60), int(x.song_duration / 1000 % 60))
            button_list.append([
                InlineKeyboardButton(
                    text='[{0}] {1} ({2})'.format(
                        time_fmt, x.song_name, ' / '.join(v.artist_name for v in x.artists)),
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_SEND,
                                             x.song_id).dump_json()
                )
            ])

        if songlist_selector.total_page == 1:
            # 什么都不做
            pass
        elif songlist_selector.cur_page == 1:
            button_list.append([
                InlineKeyboardButton(
                    text='下一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_PAGE_DOWN,
                                             songlist_selector.songlist.keyword,
                                             songlist_selector.cur_page).dump_json()
                )
            ])
        elif songlist_selector.cur_page == songlist_selector.total_page:
            button_list.append([
                InlineKeyboardButton(
                    text='上一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_PAGE_UP,
                                             songlist_selector.songlist.keyword,
                                             songlist_selector.cur_page).dump_json()
                )
            ])
        else:
            button_list.append([
                InlineKeyboardButton(
                    text='上一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_PAGE_UP,
                                             songlist_selector.songlist.keyword,
                                             songlist_selector.cur_page).dump_json()
                ),
                InlineKeyboardButton(
                    text='下一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_PAGE_DOWN,
                                             songlist_selector.songlist.keyword,
                                             songlist_selector.cur_page).dump_json()
                )
            ])
        button_list.append([
            InlineKeyboardButton(
                text='取消',
                callback_data=ButtonItem(module_name, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_CANCEL).dump_json()
            )
        ])

        return {'text': songlist_selector.title, 'reply_markup': InlineKeyboardMarkup(button_list)}

    def get_playlist_selector(self, curpage, playlist):
        self.logger.info('get_playlist_selector: keyword={0}, pagecode={1}'.format(playlist.playlist_name, curpage))

        total_page = (playlist.track_count + 4) // 5
        title = '163 🎵歌单 「{0}」\n创建者 {1} ({2} 首歌)'.format(
            playlist.playlist_name, playlist.creator.user_name, playlist.track_count)

        # 分页处理
        start = curpage * 5 - 5
        playlist.songs = playlist.songs[start:start + 5]

        return PlayListSelector(title, curpage, total_page, playlist)

    def produce_playlist_panel(self, module_name, playlist_selector):
        button_list = []

        for x in playlist_selector.playlist.songs:
            time_fmt = '{0}:{1:0>2d}'.format(int(x.song_duration / 1000 // 60), int(x.song_duration / 1000 % 60))
            button_list.append([
                InlineKeyboardButton(
                    text='[{0}] {1} ({2})'.format(
                        time_fmt, x.song_name, ' / '.join(v.artist_name for v in x.artists)),
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_SEND,
                                             x.song_id).dump_json()
                )
            ])

        if playlist_selector.total_page == 1:
            # 什么都不做
            pass
        elif playlist_selector.cur_page == 1:
            button_list.append([
                InlineKeyboardButton(
                    text='下一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_PAGE_DOWN,
                                             playlist_selector.playlist.playlist_id,
                                             playlist_selector.cur_page).dump_json()
                )
            ])
        elif playlist_selector.cur_page == playlist_selector.total_page:
            button_list.append([
                InlineKeyboardButton(
                    text='上一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_PAGE_UP,
                                             playlist_selector.playlist.playlist_id,
                                             playlist_selector.cur_page).dump_json()
                )
            ])
        else:
            button_list.append([
                InlineKeyboardButton(
                    text='上一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_PAGE_UP,
                                             playlist_selector.playlist.playlist_id,
                                             playlist_selector.cur_page).dump_json()
                ),
                InlineKeyboardButton(
                    text='下一页',
                    callback_data=ButtonItem(module_name, ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_PAGE_DOWN,
                                             playlist_selector.playlist.playlist_id,
                                             playlist_selector.cur_page).dump_json()
                )
            ])

        button_list.append([
            InlineKeyboardButton(
                text='撤销显示',
                callback_data=ButtonItem(module_name, ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_CANCEL).dump_json()
            )
        ])

        return {'text': playlist_selector.title, 'reply_markup': InlineKeyboardMarkup(button_list)}

    def get_songfile(self, song):
        # 对文件名程度限制一般性处理，特殊情况不予考虑
        if isinstance(song.song_name, str) and len(song.song_name.encode('utf-8')) > 200:
            song.song_name = song.song_name[:66]

        file_name = r'{0} - {1}{2}'.format(
            song.song_name, ' & '.join(v.artist_name for v in song.artists), os.path.splitext(song.song_url)[1])
        file_name = file_name.replace("/", ":")
        file_path = os.path.join(application.TMP_Folder, file_name)
        file_url = song.song_url
        file_stream = open(file_path, 'wb+')
        song = song
        return SongFile(file_name, file_path, file_url, file_stream, song)
