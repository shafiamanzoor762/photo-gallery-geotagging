from config import db
from Model.Link import Link

class LinkController():
    @staticmethod 
    def insert_link(person1_id, person2_id):


        existing = Link.query.filter(
            ((Link.person1_id == person1_id) & (Link.person2_id == person2_id)) |
            ((Link.person1_id == person2_id) & (Link.person2_id == person1_id))
        ).first()
    
        if existing:
            return {"error": "Link already exists"}, 409  # Conflict
    
        new_link = Link(person1_id=person1_id, person2_id=person2_id)
        db.session.add(new_link)
        db.session.commit()
        return {"message": "Link created successfully"}
        # new_link = Link(person1_id=person1_id, person2_id=person2_id)
        # db.session.add(new_link)
        # db.session.commit()
        # return new_link

    @staticmethod
    def link_exists(person1_id, person2_id):
        existing = Link.query.filter(
            ((Link.person1_id == person1_id) & (Link.person2_id == person2_id)) |
            ((Link.person1_id == person2_id) & (Link.person2_id == person1_id))
        ).first()
    
        return existing is not None  # Returns True if link exists, otherwise False

    