import logging
import os
import telegram
from telegram import TelegramError
from config import application
from entity.bot_telegram import ButtonItem
from interface.main import MainZ
from module.sing5z import sing5_util, sing5_crawler
from util import song_util

logger = logging.getLogger(__name__)


class Sing5z(MainZ):
    def __init__(self):
        super().__init__(timeout=application.FILE_TRANSFER_TIMEOUT)
        self.m_name = 'sing5'
        self.crawler = sing5_crawler.Crawler(timeout=self.timeout)
        self.utilz = sing5_util.Util()

    def search_music(self, bot, update, args):
        if len(args) == 2:
            search_type, search_content = args[1], args[2]
        else:
            search_type, search_content = 2, args[1]

        logger.info('search_music: {}'.format(search_content))
        bot_result = self.crawler.search(search_content, search_type)
        if bot_result.get_status() == 400:
            text = "缺少歌曲名称"
            update.message.reply_text(text=text)
        elif bot_result.get_status() == 200:
            pass

    def response_single_music(self, bot, update):
        """监听响应的内容，取消、翻页或者下载
        如果为取消，则直接删除选择列表
        如果为翻页，则修改选择列表并进行翻页
        如果为下载，则获取 music_id 并生成 NeteaseMusic。然后，加载-获取歌曲url，发送音乐文件，删除上一条信息
        :return:
        """
        self.logger.info('netease listen_selector_reply: data={}'.format(update.callback_query.data))
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item)

    def response_playlist(self, bot, update, playlist_id):
        pass

    def response_toplist(self, bot, update, search_type='yc'):
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="喵~")
        update.message.message_id = edited_msg.message_id
        self.toplist_turning(bot, update, search_type, 1)

    def songlist_turning(self, bot, query, kw, page):
        pass

    def playlist_turning(self, bot, query, playlist_id, page):
        pass

    def toplist_turning(self, bot, query, search_type, page):
        bot_result = self.crawler.get_songtop(search_type, page)
        if bot_result.get_status() == 404:
            text = "此榜单找不到~"
            query.message.reply_text(text=text)
        elif bot_result.get_status() == 200:
            selector = self.utilz.get_toplist_selector(page, bot_result.get_body())
            panel = self.utilz.produce_toplist_panel(self.m_name, selector)
            query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'])

    def deliver_music(self, bot, query, song_id, delete):
        if delete:
            song_util.selector_cancel(bot, query)

        bot_result = self.crawler.get_song_detail(song_id)
        if bot_result.get_status() == 400:
            text = "警告：版权问题，无法下载"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            song = bot_result.get_body()
            edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                          text="找到歌曲: [{0}]({1})".format(song.song_name, song.song_url),
                                          parse_mode=telegram.ParseMode.MARKDOWN)

            songfile = self.utilz.get_songfile(song)
            self.download_backend(bot, query, songfile, edited_msg)

    def handle_callback(self, bot, query, button_item):
        button_type, button_operate, item_id, page = button_item.t, button_item.o, button_item.i, button_item.c
        if button_operate == ButtonItem.OPERATE_CANCEL:
            song_util.selector_cancel(bot, query)
        if button_type == ButtonItem.TYPE_SONGLIST:
            if button_operate == ButtonItem.OPERATE_PAGE_DOWN:
                self.songlist_turning(bot, query, item_id, page + 1)
            if button_operate == ButtonItem.OPERATE_PAGE_UP:
                self.songlist_turning(bot, query, item_id, page - 1)
            if button_operate == ButtonItem.OPERATE_SEND:
                self.deliver_music(bot, query, item_id, True)
        if button_type == ButtonItem.TYPE_TOPLIST:
            if button_operate == ButtonItem.OPERATE_PAGE_DOWN:
                self.toplist_turning(bot, query, item_id, page + 1)
            if button_operate == ButtonItem.OPERATE_PAGE_UP:
                self.toplist_turning(bot, query, item_id, page - 1)
            if button_operate == ButtonItem.OPERATE_SEND:
                self.deliver_music(bot, query, item_id, False)

    def download_backend(self, bot, query, songfile, edited_msg):
        self.logger.info('download_backend..')
        try:
            handle = song_util.ProgressHandle(bot, query, edited_msg.message_id)
            self.crawler.write_file(songfile, handle=handle)
            songfile.set_id3tags(songfile.song.song_name, list(v.artist_name for v in songfile.song.artists),
                                 song_album=songfile.song.album.album_name)
            self.send_file(bot, query, songfile, edited_msg)
        finally:
            if os.path.exists(songfile.file_path):
                os.remove(songfile.file_path)
            if not songfile.file_stream.closed:
                songfile.file_stream.close()
            if edited_msg:
                edited_msg.delete()

    def send_file(self, bot, query, songfile, edited_msg):
        bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=edited_msg.message_id,
            text='5sing 「{0}」 等待发送'.format(songfile.song.song_name),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

        send_msg = None
        try:
            send_msg = bot.send_audio(chat_id=query.message.chat.id, audio=open(songfile.file_path, 'rb'), caption='',
                                      duration=songfile.song.song_duration,
                                      title=songfile.song.song_name,
                                      performer=' / '.join(v.artist_name for v in songfile.song.artists),
                                      timeout=self.timeout,
                                      disable_notification=True)

            self.logger.info("文件: 「{}」 发送成功.".format(songfile.song.song_name))
        except TelegramError as err:
            if send_msg:
                send_msg.delete()
            self.logger.error("文件: 「{}」 发送失败.".format(songfile.song.song_name), exc_info=err)
