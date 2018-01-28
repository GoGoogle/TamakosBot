import logging

from utils import tele

from entity.bot_telegram import BotMessage, ButtonItem
from module.recordz import record_util
from utils import tele


class Recordz(object):
    m_name = "recordz"
    store = tele.DataStore()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Recordz, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.util = record_util.Utilz()

        cfg = tele.get_config()
        self.admin_room = cfg.get('base', 'admin_room')

    @staticmethod
    def get_module_name(self):
        return self.m_name

    def record_msg(self, bot, update):
        """
        判断聊天室是否为"东方情报部门" 聊天室
        :param bot:
        :param update:
        :return:
        """
        bot_msg = BotMessage.get_botmsg(update['message'])
        self.logger.debug('msg send success!')
        panel = self.util.produce_record_panel(bot_msg, self.m_name, self.store)
        bot.send_message(chat_id=self.admin_room, text=panel["text"],
                         reply_markup=panel["markup"])
        if bot_msg.bot_content.picture.sticker:
            bot.send_sticker(chat_id=self.admin_room, sticker=bot_msg.bot_content.picture.sticker)
        if bot_msg.bot_content.photo:
            bot.send_photo(chat_id=self.admin_room,
                           photo=bot_msg.bot_content.photo)

    def record_reply(self, bot, update):
        bot_msg = BotMessage.get_botmsg(update['message'])
        if self.store.is_exist(ButtonItem.OPERATE_ENTER):
            if bot_msg.bot_content.text:
                bot.send_message(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                 text=bot_msg.bot_content.text)
            if bot_msg.bot_content.picture.sticker:
                bot.send_sticker(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                 sticker=bot_msg.bot_content.picture.sticker)
            if bot_msg.bot_content.photo:
                bot.send_photo(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                               photo=bot_msg.bot_content.photo)
            if bot_msg.bot_content.audio:
                bot.send_audio(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                               audio=bot_msg.bot_content.audio)
            if bot_msg.bot_content.video:
                bot.send_video(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                               video=bot_msg.bot_content.video)
            if bot_msg.bot_content.document:
                bot.send_document(chat_id=self.store.get(ButtonItem.OPERATE_ENTER),
                                  document=bot_msg.bot_content.document)

    def response_chat_enter(self, bot, update, chat_data):
        self.logger.debug('response_chat_enter !')
        query = update.callback_query

        button_item = ButtonItem.parse_json(query.data)
        self.handle_callback(bot, query, button_item, chat_data)

    def handle_callback(self, bot, query, button_item, chat_data):
        button_type, button_operate, item_id = button_item.t, button_item.o, button_item.i
        if button_type == ButtonItem.TYPE_DIALOG:
            if button_operate == ButtonItem.OPERATE_EXIT:
                self.end_conversation(bot, query)
            if button_operate == ButtonItem.OPERATE_ENTER:
                self.start_conversation(bot, query, item_id, chat_data)

    def start_conversation(self, bot, query, room_id, chat_data):
        """
        Here use ButtonItem.OPERATE_ENTER as the key of chat_data
        :param bot:
        :param query:
        :param room_id:
        :param chat_data:
        :return:
        """
        if chat_data.get("mode") == "center_m":
            self.store.set(ButtonItem.OPERATE_ENTER, room_id)
            text = "正在回复: {}".format(room_id)
            bot.answerCallbackQuery(query.id, text=text, show_alert=False)
        else:
            text = "请先开启回复模式"
            bot.answerCallbackQuery(query.id, text=text, show_alert=False)

    def end_conversation(self, bot, query):
        if self.store.get(ButtonItem.OPERATE_ENTER):
            self.store.clear_data()
            text = "已中断当前对话"
            bot.answer_callback_query(query.id, text=text, show_alert=False)
        else:
            text = "请先开启一个对话"
            bot.answerCallbackQuery(query.id, text=text, show_alert=False)
