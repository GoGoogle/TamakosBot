from utils.database import DB


class PersonInf(object):
    def __init__(self):
        self.db = DB().new_conn().botdb

    def init_person_inf(self, person_inf):
        self.db.col.insert({"person_id": person_inf.person_id, "created_date": person_inf.created_date,
                            "username": person_inf.username, "sel_mode": person_inf.sel_mode,
                            "match_counts": person_inf.match_counts})

    def get_person_inf(self, person_id):
        self.db.col.find_one({'person_id': person_id})

    def get_all_person_inf(self):
        self.db.col.find()
