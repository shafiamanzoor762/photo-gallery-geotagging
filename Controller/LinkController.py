from config import db
from Model.Link import Link

class LinkController():
    @staticmethod 
    def insert_link(person1_id, person2_id):
        new_link = Link(person1_id=person1_id, person2_id=person2_id)
        db.session.add(new_link)
        db.session.commit()
        return new_link
    