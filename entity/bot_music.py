import json
import taglib


class Song(object):
    def __init__(self, song_id, song_name, song_duration=None, artists=None, album=None,
                 hot_comments=None, comment_count=None, song_lyric=None,
                 song_url=None):
        self.song_id = song_id
        self.song_name = song_name
        self.song_duration = song_duration
        self.artists = artists
        self.album = album
        self.hot_comments = [] if hot_comments is None else hot_comments
        self.comment_count = 0 if comment_count is None else comment_count
        self.song_lyric = u'' if song_lyric is None else song_lyric
        self.song_url = '' if song_url is None else song_url

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class Comment(object):
    def __init__(self, comment_id, content, like_count, created_time,
                 user_id=None):
        self.comment_id = comment_id
        self.content = content
        self.like_count = like_count
        self.created_time = created_time
        self.user_id = user_id


class Album(object):
    def __init__(self, album_id, album_name, album_pic_id=None, album_pic_url=None, artist_id=None,
                 songs=None, hot_comments=None):
        self.album_id = album_id
        self.album_name = album_name
        self.album_pic_id = album_pic_id
        self.album_pic_url = album_pic_url
        self.artist_id = artist_id
        self.songs = [] if songs is None else songs
        self.hot_comments = [] if hot_comments is None else hot_comments

    def add_song(self, song):
        self.songs.append(song)


class Artist(object):
    def __init__(self, artist_id, artist_name, hot_songs=None):
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.hot_songs = [] if hot_songs is None else hot_songs

    def add_song(self, song):
        self.hot_songs.append(song)


class SongList(object):
    def __init__(self, keyword, track_count, songs):
        self.keyword = keyword
        self.track_count = track_count
        self.songs = songs

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class Playlist(object):
    def __init__(self, playlist_id, playlist_name, track_count, creator=None,
                 songs=None, hot_comments=None):
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.track_count = track_count
        self.creator = creator
        self.songs = [] if songs is None else songs
        self.hot_comments = [] if hot_comments is None else hot_comments

    def add_song(self, song):
        self.songs.append(song)

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class Toplist(object):
    def __init__(self, top_id, top_name, track_count, songs=None):
        """ top_id 是 榜单的类型"""
        self.top_id = top_id
        self.top_name = top_name
        self.track_count = track_count
        self.songs = [] if songs is None else songs

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class User(object):
    def __init__(self, user_id, user_name, songs=None, hot_comments=None):
        self.user_id = user_id
        self.user_name = user_name
        self.songs = [] if songs is None else songs
        self.hot_comments = [] if hot_comments is None else hot_comments

    def add_song(self, song):
        self.songs.append(song)


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

    def convert_to_json(self):
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

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)


class TopListSelector(object):
    def __init__(self,
                 title,
                 cur_page,
                 total_page,
                 toplist
                 ):
        self.title = title
        self.cur_page = cur_page
        self.total_page = total_page
        self.toplist = toplist

    def convert_to_json(self):
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
