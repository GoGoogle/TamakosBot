import json


class PersonIfo(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def convert_to_dict(obj):
        person_info_dict = {}
        person_info_dict.update(obj.__dict__)
        return person_info_dict

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.__dict__)

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)
