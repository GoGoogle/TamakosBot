import json
import taglib


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


class ButtonItem(object):
    TYPE_SONGLIST = 0
    TYPE_PLAYLIST = 1
    TYPE_TOPLIST = 2

    OPERATE_PAGE_DOWN = '+'
    OPERATE_PAGE_UP = '-'
    OPERATE_CANCEL = '*'
    OPERATE_SEND = '#'

    def __init__(self, pattern, button_type, button_operate, item_id=None, page=None):
        """
        由于 64 字节限制。故采用变量缩写。
        :param pattern: query_data 匹配的模块
        :param button_type: 按钮的类型，TYPE_SONGLIST， TYPE_PLAYLIST， TYPE_TOPLIST
        :param button_operate: 按钮的操作， OPERATE_PAGE_DOWN， OPERATE_PAGE_UP， OPERATE_CANCEL
        :param item_id: 项目 id
        :param page: 项目当前页数
        """
        self.p = pattern
        self.t = button_type
        self.o = button_operate
        self.i = item_id
        self.g = page

    def dump_json(self):
        """ the most compact JSON"""
        return json.dumps(self, default=lambda o: o.__dict__, separators=(',', ':'))

    @classmethod
    def parse_json(cls, json_data):
        obj = json.loads(json_data)
        pattern, button_type, operate, item_id, page = \
            obj['p'], obj['t'], obj['o'], obj['i'], obj['g']
        button_item = cls(pattern, button_type, operate, item_id, page)
        return button_item
