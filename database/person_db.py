from entity.bot_person import Person
from utils.mongo import DB


class PersonDB(object):
    def __init__(self):
        self.db = DB().new_conn().botdb

    def add_person(self, my_person):
        self.db.col.insert(my_person.convert_to_dict())

    def get_person(self, person_id):
        person_dict = self.db.col.find_one({'person_id': person_id})
        return Person(**person_dict)

    def get_all_person(self):
        person_list = []
        for item in self.db.col.find():
            person_list.append(Person(**item))
        return person_list
