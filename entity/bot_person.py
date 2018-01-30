import json


class Person(object):
    def __init__(self, person_id, created_date, first_name, username=None):
        self.person_id = person_id
        self.created_date = created_date
        self.first_name = first_name
        self.username = username

    def convert_to_dict(self):
        person_info_dict = {}
        person_info_dict.update(self.__dict__)
        return person_info_dict

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.__dict__)

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)
