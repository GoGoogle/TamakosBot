import json
import taglib
import uuid


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

    def dump_kugou_json(self):
        return json.dumps({'p': self.p, 'x': self.i})

    @classmethod
    def parse_kugou_json(cls, json_data):
        obj = json.loads(json_data)
        if obj.get('x'):
            pattern, item_id = obj['p'], obj['x']
            button_item = cls(pattern, ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_SEND, item_id)
        else:
            pattern, button_type, operate, item_id, page = \
                obj['p'], obj['t'], obj['o'], obj['i'], obj['g']
            button_item = cls(pattern, button_type, operate, item_id, page)
        return button_item

    def dump_userdata(self, user_data):
        """
        imitate a json object which contains two properties: 'p' and 'u' means pattern and uuid
        :param user_data: the tg's callback_func params: 'user_data'
        :return: uuid_json
        """
        seq_uuid = str(uuid.uuid4())
        val = self.dump_json()
        user_data[seq_uuid] = val
        callback_uuid = json.dumps({'p': self.p, 'u': seq_uuid}, separators=(',', ':'))
        return callback_uuid

    @staticmethod
    def parse_userdata(query_data, user_data):
        """
        判断 user_data dict 是否是否有值，如果该值为 callback_uuid 则取出该 uuid 对应的值, 否则取出一般值.
        :param query_data: callback_uuid over
        :param user_data: a dict where to store the key(such as the uuid above)  and original value
        :return: button_item
        """""
        obj = json.loads(query_data)
        if obj.get('u'):
            dump_json = user_data[obj.get('u')]
            button_item = ButtonItem.parse_json(dump_json)
            return button_item
        elif obj.get('o'):
            button_item = ButtonItem.parse_json(query_data)
            return button_item
