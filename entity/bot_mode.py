from module.animez import anime
from module.kugouz import kugou
from module.neteasz import netease
from module.qqz import qq


class Mode(object):
    mode_dict = {
        kugou.Kugou.m_name: "酷狗",
        qq.Qqz.m_name: "腾讯",
        netease.Netease.m_name: "网易",
        anime.Anime.m_name: "动画",
        "link": "ⓒ",
    }

    def __init__(self, mode_id, mode_nick, group=0):
        self.mode_id = mode_id
        self.mode_nick = mode_nick
        self.group = group

    @staticmethod
    def get_mode(mode_id):
        return Mode(mode_id, Mode.mode_dict.get(mode_id))


class ModeList(object):
    mode_list = [
        Mode(kugou.Kugou.m_name, "酷狗"),
        Mode(qq.Qqz.m_name, "腾讯"),
        Mode(netease.Netease.m_name, "网易"),
        Mode(anime.Anime.m_name, "动画"),
        Mode("link", "ⓒ"),
    ]

    @staticmethod
    def update_mode_list(index, mode):
        ModeList.mode_list[index] = mode
