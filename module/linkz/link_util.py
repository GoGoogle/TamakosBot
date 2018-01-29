import logging

from entity.bot_mode import Mode, ModeList


class Util(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_link_state(self, m_name, nickname):
        self.logger.debug("update link nickname {}".format(nickname))
        ModeList.update_mode_list(4, Mode(m_name, nickname))
