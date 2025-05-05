from config import db
from Model.Link import Link
from Model.Person import Person

class LinkController():
    @staticmethod
    def insert_link(person1_id, person2_id):
        person1 = Person.query.get(person1_id)
        person2 = Person.query.get(person2_id)
    
        if not person1 or not person2:
            return {"error": "One or both persons not found"}, 404
    
        # Normalize names for comparison
        name1 = person1.name.strip().lower()
        name2 = person2.name.strip().lower()
    
        # Handle name
        if name1 != name2:
            if name1 != "unknown" and name2 == "unknown":
                person2.name = person1.name
                person2.gender = person1.gender
            elif name2 != "unknown" and name1 == "unknown":
                person1.name = person2.name
                person1.gender = person2.gender
            # If both are non-unknown and different, pick a policy (keep person1's name for now)
            elif name1 != "unknown" and name2 != "unknown":
                person2.name = person1.name
                person2.gender = person1.gender
    
        # Handle gender (simpler logic for now, but you can expand similarly)
        # if person1.gender != person2.gender:
            
    
        db.session.commit()
    
        # Check for existing link
        existing = Link.query.filter(
            ((Link.person1_id == person1_id) & (Link.person2_id == person2_id)) |
            ((Link.person1_id == person2_id) & (Link.person2_id == person1_id))
        ).first()
    
        if existing:
            return {"error": "Link already exists"}, 409  # Conflict
    
        # Create new link
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

    