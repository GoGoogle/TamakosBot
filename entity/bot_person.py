import json


class PersonIfo(object):

    def __init__(self, person_id, created_date, username=None, sel_mode=None, match_counts=None):
        self.person_id = person_id
        self.created_date = created_date
        self.username = username
        self.sel_mode = sel_mode
        self.match_counts = match_counts

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)
