from entity.bot_person import PersonIfo
from utils.database import DB


class PersonInf(object):
    def __init__(self):
        self.db = DB().new_conn().botdb

    def init_person_inf(self, person_inf):
        self.db.col.insert(person_inf.convert_to_dict())

    def get_person_inf(self, person_id):
        person_inf_dict = self.db.col.find_one({'person_id': person_id})
        return PersonIfo(**person_inf_dict)

    def get_all_person_inf(self):
        person_inf_list = []
        for item in self.db.col.find():
            person_inf_list.append(PersonIfo(**item))
        return person_inf_list
