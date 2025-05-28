from Celery_worker import celery
from Controller.PersonController import PersonController
from config import db
from Model import Image, Person, ImagePerson
from Controller.ImageController import ImageController
from datetime import datetime
import os

@celery.task
def add_image_task(data):
    try:
        existing_image = Image.query.filter_by(hash=data['hash']).first()
        if existing_image:
            existing_image.is_deleted = 0
            existing_image.last_modified = datetime.utcnow()
            db.session.commit()
            print(f"⚠️ Image already exists with hash: {existing_image.hash}")
            return {'message': 'Image already exists'}

        image = Image(
            path=data['path'],
            hash=data['hash'],
            is_sync=data.get('is_sync', 0),
            capture_date=data.get('capture_date', datetime.utcnow()),
            event_date=data.get('event_date', None),
            last_modified=datetime.utcnow()
        )
        db.session.add(image)
        db.session.commit()
        print(f"✅ Image saved: {image.path}")

        full_path = os.path.abspath(os.path.join(data['path']))
        print("Processing image at:", full_path)

        extracted_faces = PersonController.extract_face(full_path)
        if not extracted_faces:
            return {'message': 'No faces found'}

        for face_data in extracted_faces:
            face_path = face_data["face_path"]
            face_filename = os.path.basename(face_path)
            db_face_path = f"face_images/{face_filename}"

            match_data = PersonController.recognize_person(f"./stored-faces/{face_filename}")

            matched_person = None
            if match_data:
                result = match_data["results"][0]
                normalized_path = result["file"].replace("\\", "/")
                face_path_1 = normalized_path.replace('stored-faces', 'face_images')
                matched_person = Person.query.filter_by(path=face_path_1).first()

                for res in match_data["results"]:
                    resembeled_path = os.path.basename(res["file"])
                    if face_filename != resembeled_path:
                        PersonController.update_face_paths_json(
                            "./stored-faces/person_group.json",
                            face_filename,
                            matchedPath=resembeled_path
                        )

            if not matched_person:
                new_person = Person(
                    name="unknown",
                    path=db_face_path,
                    gender="U"
                )
            else:
                new_person = Person(
                    name=matched_person.name,
                    path=db_face_path,
                    gender=matched_person.gender
                )

            db.session.add(new_person)
            db.session.commit()
            matched_person = new_person

            image_person = ImagePerson(image_id=image.id, person_id=matched_person.id)
            db.session.add(image_person)

        db.session.commit()
        return {'message': 'Image and faces saved successfully'}

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in background task: {e}")
        return {'error': str(e)}
