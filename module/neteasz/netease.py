import os

import telegram
from telegram import TelegramError

from config import application
from interface import MainZ
from module.neteasz import netease_crawler, netease_util
from util import song_util


class Netease(MainZ):
    def __init__(self):
        super().__init__()
        self.crawler = netease_crawler.Crawler(timeout=application.FILE_TRANSFER_TIMEOUT)
        self.utilz = netease_util.Util()
        self.init_login(application.NETEASE_LOGIN_PAYLOAD)

    def init_login(self, config):
        bot_result = self.crawler.login(config['username'], config['password'])
        if bot_result.get_status() == 200:
            self.logger.info(bot_result.get_msg())
        elif bot_result.get_status() == 400:
            self.logger.error(bot_result.get_msg())

    def search_music(self, bot, update, kw):
        self.logger.info('get_music: {}'.format(kw))
        edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                      text="喵~")
        update.message.message_id = edited_msg.message_id
        self.songlist_turning(bot, update, kw, 1)

    def response_single_music(self, bot, update):
        """监听响应的内容，取消、翻页或者下载
        如果为取消，则直接删除选择列表
        如果为翻页，则修改选择列表并进行翻页
        如果为下载，则获取 music_id 并生成 NeteaseMusic。然后，加载-获取歌曲url，发送音乐文件，删除上一条信息
        :return:
        """
        self.logger.info('netease listen_selector_reply: data={}'.format(update.callback_query.data))
        query = update.callback_query
        index1 = query.data.find('*')
        index2 = query.data.find('+')
        index3 = query.data.find('-')
        index4 = query.data.find('D')
        index5 = query.data.find('U')
        index6 = query.data.find('P')
        if index1 != -1:
            song_util.selector_cancel(bot, query)
        elif index2 != -1:
            page = int(query.data[index2 + 1:]) + 1
            kw = query.data[8:index2 - 1]
            self.songlist_turning(bot, query, kw, page)
        elif index3 != -1:
            page = int(query.data[index3 + 1:]) - 1
            kw = query.data[8:index3 - 1]
            self.songlist_turning(bot, query, kw, page)
        elif index4 != -1:
            page = int(query.data[index4 + 1:]) + 1
            playlist_id = query.data[8:index4 - 1]
            self.playlist_turning(bot, query, playlist_id, page)
        elif index5 != -1:
            page = int(query.data[index5 + 1:]) - 1
            playlist_id = query.data[8:index5 - 1]
            self.playlist_turning(bot, query, playlist_id, page)
        elif index6 != -1:
            music_id = query.data[index6 + 1:]
            self.deliver_music(bot, query, music_id, False)
        else:
            music_id = query.data[8:]
            self.deliver_music(bot, query, music_id, True)

    def response_playlist(self, bot, update, playlist_id):
        try:
            edited_msg = bot.send_message(chat_id=update.message.chat.id,
                                          text="喵~")
            update.message.message_id = edited_msg.message_id
            self.playlist_turning(bot, update, playlist_id, 1)
        except IndexError:
            self.logger.warning('無法獲取該歌曲單目', exc_info=True)

    def songlist_turning(self, bot, query, kw, page):
        bot_result = self.crawler.search_song(kw, page)
        if bot_result.get_status() == 400:
            text = "缺少歌曲名称"
            query.message.reply_text(text=text)
        elif bot_result.get_status() == 404:
            text = "此歌曲找不到~"
            query.message.reply_text(text=text)
        elif bot_result.get_status() == 200:
            selector = self.utilz.get_songlist_selector(page, bot_result.get_body())
            panel = self.utilz.produce_songlist_panel(selector)
            query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'])

    def playlist_turning(self, bot, query, playlist_id, page):
        bot_result = self.crawler.get_playlist(playlist_id, page)
        if bot_result.get_status() == 400:
            text = "此歌单找不到~"
            query.message.reply_text(text=text)
        elif bot_result.get_status() == 200:
            selector = self.utilz.get_playlist_selector(page, bot_result.get_body())
            panel = self.utilz.produce_playlist_panel(selector)
            query.message.edit_text(text=panel['text'], reply_markup=panel['reply_markup'])

    def deliver_music(self, bot, query, song_id, delete):
        if delete:
            song_util.selector_cancel(bot, query)

        bot_result = self.crawler.get_song_detail(song_id)
        if bot_result.get_status() == 400:
            text = "版权问题，暂不提供下载~"
            bot.send_message(chat_id=query.message.chat.id, text=text)
        elif bot_result.get_status() == 200:
            song = bot_result.get_body()
            edited_msg = bot.send_message(chat_id=query.message.chat.id,
                                          text="找到歌曲: [{0}]({1})".format(song.song_name, song.song_url),
                                          parse_mode=telegram.ParseMode.MARKDOWN)

            songfile = self.utilz.get_songfile(song)
            self.download_backend(bot, query, songfile, edited_msg)

    def download_backend(self, bot, query, songfile, edited_msg):
        self.logger.info('download_backend..')
        try:
            handle = song_util.ProgressHandle(bot, query, edited_msg.message_id)
            self.crawler.write_file(songfile, handle=handle)
            songfile.set_id3tags(songfile.song.song_name, list(v.artist_name for v in songfile.song.artists),
                                 song_album=songfile.song.album.album_name)
            self.send__file(bot, query, songfile, edited_msg)
        finally:
            if os.path.exists(songfile.file_path):
                os.remove(songfile.file_path)
            if not songfile.file_stream.closed:
                songfile.file_stream.close()
            if edited_msg:
                edited_msg.delete()

    def send__file(self, bot, query, songfile, edited_msg):
        bot.send_chat_action(query.message.chat.id, action=telegram.ChatAction.UPLOAD_AUDIO)
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=edited_msg.message_id,
            text='163 「{0}」 等待发送'.format(songfile.song.song_name),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

        send_msg = None
        try:
            send_msg = bot.send_audio(chat_id=query.message.chat.id, audio=open(songfile.file_path, 'rb'), caption='',
                                      duration=songfile.song.song_duration / 60,
                                      title=songfile.song.song_name,
                                      performer=' / '.join(v.artist_name for v in songfile.song.artists),
                                      timeout=application.FILE_TRANSFER_TIMEOUT,
                                      disable_notification=True)

            self.logger.info("文件: 「{}」 发送成功.".format(songfile.song.song_name))
        except TelegramError as err:
            if send_msg:
                send_msg.delete()
            self.logger.error("文件: 「{}」 发送失败.".format(songfile.song.song_name), exc_info=err)
