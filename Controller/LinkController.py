from config import db
from Model.Link import Link
from Model.Person import Person
from Controller.ImageController import ImageController
from flask import jsonify, request
import os

class LinkController():
    @staticmethod
    def insert_link(person1_id, person2_id):
        person1 = Person.query.get(person1_id)
        person2 = Person.query.get(person2_id)
    
        if not person1 or not person2:
            return {"error": "One or both persons not found"}, 404
    
        # Normalize names
        name1 = person1.name.strip().lower()
        name2 = person2.name.strip().lower()
    
        # Name and gender resolution
        if name1 != name2:
            if name1 != "unknown" and name2 == "unknown":
                person2.name = person1.name
                person2.gender = person1.gender
            elif name2 != "unknown" and name1 == "unknown":
                person1.name = person2.name
                person1.gender = person2.gender
            elif name1 != "unknown" and name2 != "unknown":
                person2.name = person1.name
                person2.gender = person1.gender
    
        db.session.commit()
    
        # Check for existing link
        existing = Link.query.filter(
            ((Link.person1_id == person1_id) & (Link.person2_id == person2_id)) |
            ((Link.person1_id == person2_id) & (Link.person2_id == person1_id))
        ).first()
    
        if existing:
            return {"error": "Link already exists"}, 409
    
        # Create and save the new link
        new_link = Link(person1_id=person1_id, person2_id=person2_id)
        db.session.add(new_link)
        db.session.commit()
    
        # Find all person IDs linked with person1_id (in either column)
        linked_ids = set()
        linked = Link.query.filter(
            (Link.person1_id == person1_id) | (Link.person2_id == person1_id)
        ).all()
    
        for link in linked:
            linked_ids.add(link.person1_id)
            linked_ids.add(link.person2_id)
    
        linked_ids.discard(person1_id)  # Optional: skip renaming person1_id itself
    
        # Rename all linked persons to match person1
        for pid in linked_ids:
            linked_person = Person.query.get(pid)
            if linked_person and linked_person.name.lower() != name1:
                print(f"Renaming linked person ID {pid} from {linked_person.name} to {person1.name}")
                linked_person.name = person1.name
                linked_person.gender = person1.gender  # Optional: update gender too
    
        # Get persons and links for embedding update
        persons_db = Person.query.all()
        person_list = [{"id": p.id, "name": p.name, "path": p.path} for p in persons_db]
    
        links = Link.query.all()
        link_list = [{"person1_id": link.person1_id, "person2_id": link.person2_id} for link in links]
    
        same_embeddings = ImageController.get_emb_names_for_recognition(person_list, link_list, name1)
        print(f"Same embeddings for {name1}: {same_embeddings}")
    
        data = same_embeddings.get_json() if hasattr(same_embeddings, 'get_json') else {}
        embedding_names = data.get("embeddings", [])
    
        for emb in embedding_names:
            full_path = os.path.join('face_images', emb)
            person = Person.query.filter_by(image_path=full_path).first()
            if person:
                print(f"Updating {person.name} (image: {emb}) to {person2.name}")
                person.name = person2.name
    
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
    
    @staticmethod
    def merge_persons(person1_id, person2_filename):
        

        try:
            # Build the expected path
            expected_path = f"face_images/{person2_filename}"

            # Find person2 by path
            person2 = db.session.query(Person).filter_by(path=expected_path).first()

            if not person2:
                return jsonify({"error": f"No person found with path '{expected_path}'"}), 404

            # Create a new link record
            print(f"Linking person1_id = {person1_id} with person2_id = {person2.id}")
            new_link = Link(person1_id=person1_id, person2_id=person2.id)
            db.session.add(new_link)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": f"Linked person1_id = {person1_id} with person2_id = {person2.id}"
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    