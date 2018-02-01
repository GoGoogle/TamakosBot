import json
import uuid
from queue import Queue
from utils.tele import is_contain_zh


class BotChat(object):
    def __init__(self, chat_id, chat_title, chat_type, date):
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.chat_type = chat_type
        self.date = date


class BotUser(object):
    def __init__(self, user_id, first_name, last_name, username, is_bot):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.is_bot = is_bot


class Picture(object):
    def __init__(self, sticker, thumb):
        self.sticker = sticker
        self.thumb = thumb


class BotContent(object):
    def __init__(self, text, picture=None, photo=None, audio=None, video=None, document=None):
        self.text = text
        self.picture = picture
        self.photo = photo
        self.audio = audio
        self.video = video
        self.document = document


class BotMessage(object):
    def __init__(self, msg_id, bot_chat, bot_user, bot_content):
        self.msg_id = msg_id
        self.bot_chat = bot_chat
        self.bot_user = bot_user
        self.bot_content = bot_content

    @staticmethod
    def get_botmsg(msg):
        """
        Here use the msg['photo'][-1]，because Object of type 'PhotoSize' is not JSON serializable
        :param msg:
        :return:
        """
        msg_id = msg['message_id']
        bot_chat = BotChat(msg['chat']['id'], msg['chat']['title'], msg['chat']['type'], msg['date'])
        bot_user = BotUser(msg['from_user']['id'], msg['from_user']['first_name'], msg['from_user']['last_name'],
                           msg['from_user']['username'], msg['from_user']['is_bot'])
        bot_content = BotContent(msg['text'], Picture(msg['sticker'], msg['thumb']),
                                 msg['photo'][-1] if msg['photo'] else None,
                                 msg['audio'],
                                 msg['video'],
                                 msg['document'])
        bot_msg = BotMessage(msg_id, bot_chat, bot_user, bot_content)
        return bot_msg


class ButtonItem(object):
    TYPE_MODE = 0
    TYPE_SONGLIST = 1
    TYPE_PLAYLIST = 2
    TYPE_TOPLIST = 3
    TYPE_DIALOG = 4
    TYPE_TOPLIST_CATEGORY = 5

    OPERATE_CANCEL = '*'
    OPERATE_PAGE_DOWN = '+'
    OPERATE_PAGE_UP = '-'
    OPERATE_SEND = '#'

    OPERATE_ENTER = '+'
    OPERATE_EXIT = '-'

    def __init__(self, pattern, button_type, button_operate, item_id="", page=""):
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
        """
        the most compact JSON
        the self.i's max length is 22 bytes, and utf-8 Chinese 3 bytes per character. only handle for chinese
        :return:
        """
        if isinstance(self.i, str) and u'\u4e00' <= self.i <= u'\u9fa5' and len(self.i.encode('utf-8')) > 22:
            self.i = self.i[:7]
        _json = json.dumps(self, default=lambda o: o.__dict__, separators=(',', ':'), ensure_ascii=False)
        return _json

    @classmethod
    def parse_json(cls, json_data):
        obj = json.loads(json_data)
        pattern, button_type, operate, item_id, page = \
            obj['p'], obj['t'], obj['o'], obj['i'], obj['g']
        button_item = cls(pattern, button_type, operate, item_id, page)
        return button_item

    def dump_simple_json(self):
        if isinstance(self.i, str) and is_contain_zh(self.i) and len(self.i.encode('utf-8')) > 22:
            self.i = self.i[:7]
        if self.t == ButtonItem.TYPE_SONGLIST:
            return json.dumps({'p': self.p, 'x': self.i}, separators=(',', ':'), ensure_ascii=False)
        if self.t == ButtonItem.TYPE_PLAYLIST:
            return json.dumps({'p': self.p, 'y': self.i}, separators=(',', ':'), ensure_ascii=False)
        if self.t == ButtonItem.TYPE_TOPLIST:
            return json.dumps({'p': self.p, 'z': self.i}, separators=(',', ':'), ensure_ascii=False)

    @classmethod
    def parse_simple_json(cls, json_data):
        obj = json.loads(json_data)
        if obj.get('x'):
            button_item = cls(obj['p'], ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_SEND, obj['x'])
        elif obj.get('y'):
            button_item = cls(obj['p'], ButtonItem.TYPE_PLAYLIST, ButtonItem.OPERATE_SEND, obj['y'])
        elif obj.get('z'):
            button_item = cls(obj['p'], ButtonItem.TYPE_TOPLIST, ButtonItem.OPERATE_SEND, obj['z'])
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


class MatchItem(object):
    def __init__(self, my_created, my_id, my_status, your_created=None, your_id=None, your_status=None):
        self.my_id = my_id
        self.my_status = my_status
        self.my_created = my_created
        self.your_id = your_id
        self.your_status = your_status
        self.your_created = your_created

    def update_my_status(self, my_status):
        self.my_status = my_status

    def update_your_status(self, your_status):
        self.your_status = your_status


class MatchGroup(object):
    def __init__(self):
        self.group_queue = Queue()

    def put(self, key_id, match_item):
        dict({key_id: match_item})
