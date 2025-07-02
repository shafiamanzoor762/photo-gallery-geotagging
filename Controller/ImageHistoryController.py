from sqlalchemy.orm import aliased
from sqlalchemy import func
from Model.ImageHistory import ImageHistory  # ✅ Correct import
from config import db  # ensure db is available
from flask import request, jsonify
from sqlalchemy import and_
from Model.PersonHistory import PersonHistory  # ✅ Correct import
from Model.ImageEventHistory import ImageEventHistory  # ✅ Correct import
from datetime import timedelta
from Model.Event import Event  # ✅ Correct import
from Model.ImagePerson import ImagePerson  # ✅ Correct import
from Controller.ImageController import ImageController
class ImageHistoryController:
    @staticmethod
    def get_latest_inactive_non_deleted_images():
        subquery = db.session.query(
            ImageHistory.id.label('image_id'),
            func.max(ImageHistory.version_no).label('max_version')
        ).filter(
            ImageHistory.is_Active == False,
            ImageHistory.is_deleted == False
        ).group_by(ImageHistory.id).subquery()

        IH = aliased(ImageHistory)

        results = db.session.query(
            IH.id,
            IH.path,
            IH.version_no
        ).join(
            subquery,
            (IH.id == subquery.c.image_id) & (IH.version_no == subquery.c.max_version)
        ).filter(
            IH.is_Active == False,
            IH.is_deleted == False
        ).all()
        print (results)
        return [{'id': r.id, 'path': r.path, 'version_no': r.version_no} for r in results]
        
    
    @staticmethod
    def get_image_complete_details_undo(image_id, version):
        image = ImageHistory.query.filter(
            and_(
                ImageHistory.id == image_id,
                ImageHistory.version_no == version
            )
        ).first()
    
        if not image:
            return jsonify({"error": "Image not found"}), 404
    
        # ⏳ Allow a 5-second window for timestamp matching
        delta = timedelta(seconds=5)
        lower_bound = image.created_at - delta
        upper_bound = image.created_at + delta
        deltaperson= timedelta(seconds=2)
        lower_boundperson = image.created_at - deltaperson
        upper_boundperson = image.created_at + deltaperson
    
        # 📍 Location handling (only if the relationship is defined in ImageHistory via backref)
        location_data = {}
        if image.location:
            location_data = {
                "id": image.location.id,
                "name": image.location.name,
                "latitude": float(image.location.latitude),
                "longitude": float(image.location.longitude)
            }
    
        # 👤 Get matching persons within time window
        matching_persons = db.session.query(PersonHistory).join(
    ImagePerson,
    PersonHistory.id == ImagePerson.person_id
).filter(
    ImagePerson.image_id == image.id,
        PersonHistory.created_at.between(lower_boundperson, upper_boundperson),

            ).all()

        persons = [
            {
                "id": person.id,
                "name": person.name,
                "path": person.path,
                "gender": person.gender
            }
            for person in matching_persons
        ]
    
        
        matching_events = db.session.query(Event).join(
    ImageEventHistory,
    and_(
        Event.id == ImageEventHistory.event_id,
        ImageEventHistory.image_id == image.id
    )
).filter(
    ImageEventHistory.created_at.between(lower_bound, upper_bound)
).all()

    
        events = [
    {
        "id": event.id,
        "name": event.name
    }
    for event in matching_events
]

    
        # 🖼️ Final image data response
        # image_data = {
        #     "id": image.id,
        #     "path": image.path,
        #     "is_sync": image.is_sync,
        #     "capture_date": image.capture_date.strftime('%Y-%m-%d') if image.capture_date else None,
        #     "event_date": image.event_date.strftime('%Y-%m-%d') if image.event_date else None,
        #     "last_modified": image.last_modified.strftime('%Y-%m-%d %H:%M:%S') if image.last_modified else None,
        #     "hash": image.hash,
        #     "location": location_data,
        #     "persons": persons,
        #     "events": events
        # }

        image_data = {
    str(image.id): {
        "path": image.path,
            "is_sync": image.is_sync,
            "capture_date": image.capture_date.strftime('%Y-%m-%d') if image.capture_date else None,
            "event_date": image.event_date.strftime('%Y-%m-%d') if image.event_date else None,
            "last_modified": image.last_modified.strftime('%Y-%m-%d %H:%M:%S') if image.last_modified else None,
            "hash": image.hash,
        "persons_id": persons,  # Rename if needed
        "event_names": [event["name"] for event in events],
        "event_date": image.event_date.strftime('%Y-%m-%dT%H:%M:%S') if image.event_date else None,
        "location": [
            location_data.get("name",""),
            location_data.get("latitude",0.0),
            location_data.get("longitude",0.0)
        ]
    }
}

        print("Image Data:", image_data)  # Debugging line to check the output
        return image_data
    

    @staticmethod
    def undo_data(image_id, version):
        try:
            image_data = ImageHistoryController.get_image_complete_details_undo(image_id, version)
            ImageController.edit_image_data(image_data)
    
            image = ImageHistory.query.filter_by(id=image_id, version_no=version).first()
            if not image:
                return False
    
            delta = timedelta(seconds=5)
            lower_bound = image.created_at - delta
            upper_bound = image.created_at + delta
    
            # Update ImageHistory
            ImageHistory.query.filter(
                and_(
                    ImageHistory.id == image_id,
                    ImageHistory.version_no == version
                )
            ).update({"is_Active": True}, synchronize_session=False)
    
            # Update ImageEventHistory
            updated_events = ImageEventHistory.query.filter(
                and_(
                    ImageEventHistory.image_id == image_id,
                    ImageEventHistory.created_at.between(lower_bound, upper_bound)
                )
            ).all()
    
            for ev in updated_events:
                ev.is_Active = True
    
            # Update PersonHistory
            matching_persons = db.session.query(PersonHistory).select_from(PersonHistory).join(
                ImagePerson,
                PersonHistory.id == ImagePerson.person_id
            ).filter(
                ImagePerson.image_id == image_id,
                PersonHistory.created_at.between(lower_bound, upper_bound),
                PersonHistory.version_no == version
            ).all()
    
            for person in matching_persons:
                person.is_Active = True
    
            db.session.commit()
            return True
    
        except Exception as e:
            print(f"Error in undo_data: {e}")
            db.session.rollback()
            return False
    