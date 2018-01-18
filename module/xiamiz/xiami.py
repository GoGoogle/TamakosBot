import os

import telegram
from telegram import TelegramError

from config import application
from entity.bot_telegram import ButtonItem
from interface.song.main import MainZ
from module.xiamiz import xiami_crawler, xiami_util
from util import song_util


class Xiami(MainZ):
    m_name = 'xiami'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Xiami, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(timeout=application.FILE_TRANSFER_TIMEOUT)
        self.crawler = xiami_crawler.Crawler(timeout=self.timeout)
        self.utilz = xiami_util.Util()

    def search_music(self, bot, update, kw):
        self.logger.debug('get_music: %s', kw)
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="🙄")
        update.message.message_id = edited_msg.message_id
        self.songlist_turning(bot, update, kw, 1)

    def songlist_turning(self, bot, query, kw, page):
        bot_result = self.crawler.search_song(kw, page)
        if bot_result.get_status() == 400:
            text = "🤔缺少歌曲名称"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 404:
            text = "🤔此歌曲找不到"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            selector = self.utilz.get_songlist_selector(page, bot_result.get_body())
            panel = self.utilz.produce_songlist_panel(self.m_name, selector)
            query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'])

    def response_single_music(self, bot, update):
        self.logger.debug('%s response_single_music: data=%s', self.m_name, update.callback_query.data)
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item)

    def handle_callback(self, bot, query, button_item):
        button_type, button_operate, item_id, page = button_item.t, button_item.o, button_item.i, button_item.g
        if button_operate == ButtonItem.OPERATE_CANCEL:
            song_util.selector_cancel(bot, query)
        if button_type == ButtonItem.TYPE_SONGLIST:
            if button_operate == ButtonItem.OPERATE_PAGE_DOWN:
                self.songlist_turning(bot, query, item_id, page + 1)
            if button_operate == ButtonItem.OPERATE_PAGE_UP:
                self.songlist_turning(bot, query, item_id, page - 1)
            if button_operate == ButtonItem.OPERATE_SEND:
                self.deliver_music(bot, query, item_id, delete=True)

    def deliver_music(self, bot, query, song_id, delete=False):
        if delete:
            song_util.selector_cancel(bot, query)

        bot_result = self.crawler.get_song_detail(song_id)
        if bot_result.get_status() == 400:
            text = "😶没有版权©"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            song = bot_result.get_body()
            edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                          text="找到歌曲: [{0}]({1})".format(song.song_name, song.song_url),
                                          parse_mode=telegram.ParseMode.MARKDOWN)

            songfile = self.utilz.get_songfile(song)
            self.download_backend(bot, query, songfile, edited_msg)

    def download_backend(self, bot, query, songfile, edited_msg):
        self.logger.debug('download_backend..')
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
            text='🦐 「{0}」 等待发送'.format(songfile.song.song_name),
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

            self.logger.debug("文件: 「%s」 发送成功.", songfile.song.song_name)
        except TelegramError as err:
            if send_msg:
                send_msg.delete()
            self.logger.error("文件: 「%s」 发送失败.", songfile.song.song_name, exc_info=err)
