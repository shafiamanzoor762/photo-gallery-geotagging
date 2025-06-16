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
    
        # 📍 Location handling (only if the relationship is defined in ImageHistory via backref)
        location_data = None
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
        PersonHistory.version_no ==version

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
        image_data = {
            "id": image.id,
            "path": image.path,
            "is_sync": image.is_sync,
            "capture_date": image.capture_date.strftime('%Y-%m-%d') if image.capture_date else None,
            "event_date": image.event_date.strftime('%Y-%m-%d') if image.event_date else None,
            "last_modified": image.last_modified.strftime('%Y-%m-%d %H:%M:%S') if image.last_modified else None,
            "hash": image.hash,
            "location": location_data,
            "persons": persons,
            "events": events
        }
    
        return image_data
