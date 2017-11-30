import unittest
from unittest import TestCase

from entity.bot_telegram import ButtonItem

button_item = ButtonItem('netease', ButtonItem.TYPE_SONGLIST, ButtonItem.OPERATE_PAGE_UP, '414312414', 244)


class TestButtonItem(TestCase):
    # def test_dump_json(self):
    #     json = button_item.dump_json()
    #     print(json)

    def test_load_json(self):
        json_data = button_item.dump_json()
        ButtonItem.parse_json(json_data)
        result = ButtonItem.parse_json(json_data)
        print(result.dump_json())
        print(len(result.dump_json()))


if __name__ == '__main__':
    unittest.main()
