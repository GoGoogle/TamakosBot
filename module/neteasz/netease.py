import os

import telegram
from telegram import TelegramError

from entity.bot_telegram import ButtonItem
from interface.musics.main import MainZ
from module.neteasz import netease_crawler, netease_util
from utils import music
from utils import tele


class Netease(MainZ):
    m_name = 'netease'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Netease, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(500)
        self.crawler = netease_crawler.Crawler(timeout=self.timeout)
        self.utilz = netease_util.Util()

        cfg = tele.get_config()
        self.username = cfg.get('api', 'netease_username')
        self.password = cfg.get('api', 'netease_password')

    def init_login(self, config):
        if self.username and self.password:
            bot_result = self.crawler.login(self.username, self.password)
            if bot_result.get_status() == 200:
                self.logger.debug(bot_result.get_msg())
            elif bot_result.get_status() == 400:
                self.logger.error(bot_result.get_msg())

    def search_music(self, bot, update, kw):
        self.logger.debug('get_music: %s', kw)
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="🍈")
        update.message.message_id = edited_msg.message_id
        self.songlist_turning(bot, update, kw, 1)

    def response_single_music(self, bot, update):
        """监听响应的内容，取消、翻页或者下载
        如果为取消，则直接删除选择列表
        如果为翻页，则修改选择列表并进行翻页
        如果为发送，则获取 music_id 并生成 NeteaseMusic。然后，加载-获取歌曲url，发送音乐文件，删除上一条信息
        :return:
        """
        self.logger.debug('%s response_single_music: data=%s', self.m_name, update.callback_query.data)
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item)

    def response_playlist(self, bot, update, playlist_id):
        try:
            edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                          text="🍈")
            update.message.message_id = edited_msg.message_id
            self.playlist_turning(bot, update, playlist_id, 1)
        except IndexError:
            self.logger.warning('無法獲取該歌曲單目', exc_info=True)

    def songlist_turning(self, bot, query, kw, page):
        bot_result = self.crawler.search_song(kw, page)
        if bot_result.get_status() == 400:
            text = "🍈 400"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 404:
            text = "🍈 404"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            selector = self.utilz.get_songlist_selector(page, bot_result.get_body())
            panel = self.utilz.produce_songlist_panel(self.m_name, selector)
            query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'])

    def playlist_turning(self, bot, query, playlist_id, page):
        bot_result = self.crawler.get_playlist(playlist_id, page)
        if bot_result.get_status() == 400:
            text = "🍈 404"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            selector = self.utilz.get_playlist_selector(page, bot_result.get_body())
            panel = self.utilz.produce_playlist_panel(self.m_name, selector)
            query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'])

    def deliver_music(self, bot, query, song_id, delete=False):
        if delete:
            music.selector_cancel(bot, query)

        bot_result = self.crawler.get_song_detail(song_id)
        if bot_result.get_status() == 400:
            text = "🍈 No Copyright©"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            song = bot_result.get_body()
            edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                          text="[{0}]({1}) 🍈".format(song.song_name, song.song_url),
                                          parse_mode=telegram.ParseMode.MARKDOWN)

            songfile = self.utilz.get_songfile(song)
            self.download_backend(bot, query, songfile, edited_msg)

    def handle_callback(self, bot, query, button_item):
        button_type, button_operate, item_id, page = button_item.t, button_item.o, button_item.i, button_item.g
        if button_operate == ButtonItem.OPERATE_CANCEL:
            music.selector_cancel(bot, query)
        if button_type == ButtonItem.TYPE_SONGLIST:
            if button_operate == ButtonItem.OPERATE_PAGE_DOWN:
                self.songlist_turning(bot, query, item_id, page + 1)
            if button_operate == ButtonItem.OPERATE_PAGE_UP:
                self.songlist_turning(bot, query, item_id, page - 1)
            if button_operate == ButtonItem.OPERATE_SEND:
                self.deliver_music(bot, query, item_id, delete=True)
        if button_type == ButtonItem.TYPE_PLAYLIST:
            if button_operate == ButtonItem.OPERATE_PAGE_DOWN:
                self.playlist_turning(bot, query, item_id, page + 1)
            if button_operate == ButtonItem.OPERATE_PAGE_UP:
                self.playlist_turning(bot, query, item_id, page - 1)
            if button_operate == ButtonItem.OPERATE_SEND:
                self.deliver_music(bot, query, item_id, delete=False)

    def download_backend(self, bot, query, songfile, edited_msg):
        self.logger.debug('download_backend..')
        try:
            handle = music.ProgressHandle(bot, query, edited_msg.message_id)
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
            text='🍈 🍈 🍈'.format(songfile.song.song_name),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

        send_msg = None
        try:
            send_msg = bot.send_audio(chat_id=query.message.chat.id, audio=open(songfile.file_path, 'rb'), caption='',
                                      duration=songfile.song.song_duration / 1000,
                                      title=songfile.song.song_name,
                                      performer=' / '.join(v.artist_name for v in songfile.song.artists),
                                      timeout=self.timeout,
                                      disable_notification=True)

            self.logger.debug("文件: 「%s」 发送成功.", songfile.song.song_name)
        except TelegramError as err:
            if send_msg:
                send_msg.delete()
            self.logger.error("文件: 「%s」 发送失败.", songfile.song.song_name, exc_info=err)
