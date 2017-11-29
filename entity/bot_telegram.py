import json
import taglib

import telegram


class SongListSelector(object):
    def __init__(self,
                 title,
                 cur_page,
                 total_page,
                 songlist
                 ):
        self.title = title
        self.cur_page = cur_page
        self.total_page = total_page
        self.songlist = songlist

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class PlayListSelector(object):
    def __init__(self,
                 title,
                 cur_page,
                 total_page,
                 playlist
                 ):
        self.title = title
        self.cur_page = cur_page
        self.total_page = total_page
        self.playlist = playlist

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class SongFile(object):
    def __init__(self, file_name, file_path, file_url, file_stream, song=None):
        self.file_name = file_name
        self.file_path = file_path
        self.file_url = file_url
        self.file_stream = file_stream
        self.song = song

    def set_id3tags(self, song_name, artist_name_list=None, song_album=None, track_num='01/10'):
        song = taglib.File(self.file_path)
        if song:
            song.tags["ARTIST"] = artist_name_list
            song.tags["ALBUM"] = [song_album]
            song.tags["TITLE"] = [song_name]
            song.tags["TRACKNUMBER"] = [track_num]
            song.save()


class ProgressHandle(object):
    def __init__(self, bot, query, msg_id):
        self.bot = bot
        self.query = query
        self.msg_id = msg_id

    def update(self, progress_status):
        self.bot.edit_message_text(
            chat_id=self.query.message.chat.id,
            message_id=self.msg_id,
            text=progress_status,
            disable_web_page_preview=True,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
