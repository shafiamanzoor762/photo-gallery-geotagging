from sqlalchemy import desc, select
from sqlalchemy.orm import aliased
from sqlalchemy import func, text
from Model.Image import Image
from Model.ImageEvent import ImageEvent
from Model.ImageHistory import ImageHistory  # ✅ Correct import
from Model.Person import Person
from config import db  # ensure db is available
from flask import request, jsonify
from sqlalchemy import and_
from Model.PersonHistory import PersonHistory  # ✅ Correct import
from Model.ImageEventHistory import ImageEventHistory  # ✅ Correct import
from datetime import datetime, timedelta
from Model.Event import Event  # ✅ Correct import
from Model.ImagePerson import ImagePerson  # ✅ Correct import
from Controller.ImageController import ImageController
class ImageHistoryController:
    @staticmethod
    # def get_latest_inactive_non_deleted_images():
    #     subquery = db.session.query(
    #         ImageHistory.id.label('image_id'),
    #         func.max(ImageHistory.version_no).label('max_version')
    #     ).filter_by(is_Active=False, is_deleted=False).group_by(ImageHistory.id).subquery()

    #     IH = aliased(ImageHistory)

    #     results = db.session.query(
    #         IH.id,
    #         IH.path,
    #         IH.version_no
    #     ).join(
    #         subquery,
    #         (IH.id == subquery.c.image_id) & (IH.version_no == subquery.c.max_version)
    #     ).all()

    #     return [{'id': r.id, 'path': r.path, 'version_no': r.version_no} for r in results]

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
        delta = timedelta(seconds=1)
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
    def toggle_triggers(enable=True):
        action = "ENABLE" if enable else "DISABLE"

        triggers = {
            "Image": "trg_UpdateImageHistory_new",
            "ImageEvent": "trg_Delete_ImageEventHistory",
            "Person": "trg_UpdatePersonHistory"
        }

        for table, trigger in triggers.items():
            db.session.execute(text(f"{action} TRIGGER {trigger} ON {table}"))
        db.session.flush()





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


#  ya iqra version
    # @staticmethod
    # def undo_data(image_id, version=None):
    #     try:
    #         ImageHistoryController.toggle_triggers(enable=False)

    #         orig = Image.query.get(image_id)
    #         if not orig:
    #             return False

    #         active_image = db.session.query(ImageHistory).filter_by(id=image_id, is_Active=True).first()
    #         # ✅ Added this condition to stop undo if version = 1
    #         # if active_image and active_image.version_no == 1:
    #         #     print("⚠️ Undo not allowed. Already at version 1.")
    #         #     ImageHistoryController.toggle_triggers(enable=True)
    #         #     return False

    #         # 🔴 CASE 1: is_Active = 0 → No active record in history
    #         if not active_image:
    #         #     # Save current original image into history if not already
    #         #     # 🔹 Step 1: Get the current/original image
    #             orig = Image.query.get(image_id)
    #             if not orig:
    #                 return False

    #             # 🔹 Step 2: Save original image into history if this version is not already saved
    #             exists = db.session.query(ImageHistory).filter_by(
    #                 id=orig.id,
    #                 path=orig.path,
    #                 location_id=orig.location_id,
    #                 is_deleted=orig.is_deleted,
    #                 hash=orig.hash
    #             ).first()

    #             if not exists:
    #                 max_ver = db.session.query(func.max(ImageHistory.version_no)).filter_by(id=orig.id).scalar() or 0
    #                 db.session.add(ImageHistory(
    #                     id=orig.id,
    #                     path=orig.path,
    #                     is_sync=orig.is_sync,
    #                     capture_date=orig.capture_date,
    #                     event_date=orig.event_date,
    #                     last_modified=orig.last_modified,
    #                     location_id=orig.location_id,
    #                     version_no=max_ver + 1,
    #                     is_deleted=orig.is_deleted,
    #                     hash=orig.hash,
    #                     is_Active=False,
    #                     created_at=datetime.utcnow()
    #                 ))
    #                 db.session.flush()

    #             # 🔹 Step 3: Get the latest max version, to get the previous version
    #             current_max_ver = db.session.query(func.max(ImageHistory.version_no)).filter_by(id=image_id).scalar() or 0
    #             prev_ver = current_max_ver - 1

    #             # 🔹 Step 4: Load the previous version
    #             prev_row = db.session.query(ImageHistory).filter_by(id=image_id, version_no=prev_ver).first()
    #             if not prev_row:
    #                 return False

    #             # 🔹 Step 5: Set all previous versions to inactive
    #             db.session.query(ImageHistory).filter_by(id=image_id).update({'is_Active': False})

    #             # 🔹 Step 6: Make the previous version active
    #             prev_row.is_Active = True

    #             # 🔹 Step 7: Restore this version to the original Image table
    #             orig.path = prev_row.path
    #             orig.is_sync = prev_row.is_sync
    #             orig.capture_date = prev_row.capture_date
    #             orig.event_date = prev_row.event_date
    #             orig.last_modified = datetime.utcnow()
    #             orig.location_id = prev_row.location_id
    #             orig.is_deleted = prev_row.is_deleted
    #             orig.hash = prev_row.hash
    #             orig.is_Active = True

            

    #             # 🔁 Restore ImageEvent
    #             event_ids = db.session.query(ImageEventHistory.event_id).filter_by(image_id=image_id).distinct()
    #             for eid_row in event_ids:
    #                 eid = eid_row.event_id
    #                 active_evt = db.session.query(ImageEventHistory).filter_by(image_id=image_id, event_id=eid, is_Active=True).first()
    #                 if not active_evt:
    #                     max_evt = db.session.query(ImageEventHistory).filter_by(
    #                         image_id=image_id, event_id=eid
    #                     ).order_by(ImageEventHistory.version_no.desc()).first()

    #                     if max_evt:
    #                         db.session.add(ImageEventHistory(
    #                             image_id=image_id, event_id=eid,
    #                             version_no=(max_evt.version_no or 0) + 1,
    #                             is_Active=False, created_at=datetime.utcnow()
    #                         ))

    #                     # ✅ Activate latest version in history
    #                     max_evt.is_Active = True

    #                     # ✅ Ensure mapping exists in ImageEvent table (without is_Active)
    #                     if not db.session.query(ImageEvent).filter_by(image_id=image_id, event_id=eid).first():
    #                         db.session.add(ImageEvent(image_id=image_id, event_id=eid))
    #                 else:
    #                     active_evt.is_Active = False

    #                     prev_evt = db.session.query(ImageEventHistory).filter_by(
    #                         image_id=image_id, event_id=eid,
    #                         version_no=active_evt.version_no - 1
    #                     ).first()

    #                     if prev_evt:
    #                         prev_evt.is_Active = True

    #                         # ✅ Ensure mapping exists in ImageEvent table
    #                         if not db.session.query(ImageEvent).filter_by(image_id=image_id, event_id=eid).first():
    #                             db.session.add(ImageEvent(image_id=image_id, event_id=eid))


    #             # 🔁 Restore Person
    #             # 🔁 Undo logic for all persons linked with this image
    #             person_ids = db.session.query(ImagePerson.person_id).filter_by(image_id=image_id).distinct()

    #             for pid_row in person_ids:
    #                 pid = pid_row.person_id

    #                 # 🔹 Step 1: Get the current/original person
    #                 orig_person = Person.query.get(pid)
    #                 if not orig_person:
    #                     continue

    #                 # 🔹 Step 2: Save current person into PersonHistory if this version is not already saved
    #                 exists = db.session.query(PersonHistory).filter_by(
    #                     id=orig_person.id,
    #                     name=orig_person.name,
    #                     gender=orig_person.gender,
    #                     dob=orig_person.dob,
    #                     age=orig_person.age,
    #                     path=orig_person.path
    #                 ).first()

    #                 if not exists:
    #                     max_ver = db.session.query(func.max(PersonHistory.version_no)).filter_by(id=pid).scalar() or 0
    #                     db.session.add(PersonHistory(
    #                         id=orig_person.id,
    #                         name=orig_person.name,
    #                         gender=orig_person.gender,
    #                         dob=orig_person.dob,
    #                         age=orig_person.age,
    #                         path=orig_person.path,
    #                         is_Active=False,
    #                         version_no=max_ver + 1,
    #                         created_at=datetime.utcnow()
    #                     ))
    #                     db.session.flush()

    #                 # 🔹 Step 3: Get the latest max version, and subtract 1 to get the previous version
    #                 current_max_ver = db.session.query(func.max(PersonHistory.version_no)).filter_by(id=pid).scalar() or 0
    #                 prev_ver = current_max_ver - 1

    #                 # 🔹 Step 4: Load the previous version
    #                 prev_row = db.session.query(PersonHistory).filter_by(id=pid, version_no=prev_ver).first()
    #                 if not prev_row:
    #                     continue

    #                 # 🔹 Step 5: Set all versions to inactive first
    #                 db.session.query(PersonHistory).filter_by(id=pid).update({'is_Active': False})

    #                 # 🔹 Step 6: Make the previous version active
    #                 prev_row.is_Active = True

    #                 # 🔹 Step 7: Restore this version to the original Person table
    #                 db.session.merge(Person(
    #                     id=pid,
    #                     name=prev_row.name,
    #                     gender=prev_row.gender,
    #                     dob=prev_row.dob,
    #                     age=prev_row.age,
    #                     path=prev_row.path
    #                 ))


    #             db.session.commit()
    #             ImageHistoryController.toggle_triggers(enable=True)
    #             return True

    #         # 🟢 CASE 2: Active history record exists, perform standard undo
            
    #         # 🟢 CASE 2: Active history record exists, perform standard undo
    #         if not active_image or not active_image.version_no or active_image.version_no < 1:
    #             return False

    #         prev_version = active_image.version_no - 1
    #         if prev_version < 1:
    #             return False

    #         prev_image = db.session.query(ImageHistory).filter_by(id=image_id, version_no=prev_version).first()
    #         if not prev_image:
    #             return False

    #         # 📝 Save current into history if not already saved with same data
    #         exists = db.session.query(ImageHistory).filter_by(
    #             id=orig.id, path=orig.path, location_id=orig.location_id,
    #             is_deleted=orig.is_deleted, hash=orig.hash
    #         ).first()

    #         if not exists:
    #             max_ver = db.session.query(func.max(ImageHistory.version_no)).filter_by(id=orig.id).scalar() or 0
    #             db.session.add(ImageHistory(
    #                 id=orig.id,
    #                 path=orig.path,
    #                 is_sync=orig.is_sync,
    #                 capture_date=orig.capture_date,
    #                 event_date=orig.event_date,
    #                 last_modified=orig.last_modified,
    #                 location_id=orig.location_id,
    #                 version_no=max_ver + 1,   # ✅ No NULL version
    #                 is_deleted=orig.is_deleted,
    #                 hash=orig.hash,
    #                 is_Active=False,
    #                 created_at=datetime.utcnow()
    #             ))
    #             db.session.flush()

    #         # 🔄 Deactivate current version
    #         active_image.is_Active = False
    #         prev_image.is_Active = True

    #         # 🔁 Apply previous version to original Image
    #         orig.path = prev_image.path
    #         orig.is_sync = prev_image.is_sync
    #         orig.capture_date = prev_image.capture_date
    #         orig.event_date = prev_image.event_date
    #         orig.last_modified = datetime.utcnow()
    #         orig.location_id = prev_image.location_id
    #         orig.is_deleted = prev_image.is_deleted
    #         orig.hash = prev_image.hash
    #         orig.is_Active = True

    #         # 🔁 Restore previous ImageEvents
    #         event_ids = db.session.query(ImageEventHistory.event_id).filter_by(image_id=image_id).distinct()
    #         for eid_row in event_ids:
    #             eid = eid_row.event_id

    #             active_evt = db.session.query(ImageEventHistory).filter_by(
    #                 image_id=image_id, event_id=eid, is_Active=True
    #             ).first()

    #             # Deactivate current
    #             if active_evt and active_evt.version_no:
    #                 active_evt.is_Active = False
    #                 prev_ver = active_evt.version_no - 1
    #             else:
    #                 prev_ver = db.session.query(func.max(ImageEventHistory.version_no)).filter_by(
    #                     image_id=image_id, event_id=eid
    #                 ).scalar() or 0
    #                 prev_ver = max(prev_ver - 1, 0)

    #             if prev_ver < 1:
    #                 continue

    #             prev_evt = db.session.query(ImageEventHistory).filter_by(
    #                 image_id=image_id, event_id=eid, version_no=prev_ver
    #             ).first()

    #             if prev_evt:
    #                 db.session.query(ImageEventHistory).filter_by(image_id=image_id, event_id=eid).update({'is_Active': False})
    #                 prev_evt.is_Active = True

    #                 # Reflect in main ImageEvent
    #                 img_evt = db.session.query(ImageEvent).filter_by(image_id=image_id, event_id=eid).first()
    #                 if img_evt:
    #                     img_evt.is_Active = True
    #                 else:
    #                     db.session.add(ImageEvent(image_id=image_id, event_id=eid, is_Active=True))

    #         # 🔁 Restore previous Persons
    #         person_ids = db.session.query(ImagePerson.person_id).filter_by(image_id=image_id).distinct()
    #         for pid_row in person_ids:
    #             pid = pid_row.person_id
    #             active_person = db.session.query(PersonHistory).filter_by(id=pid, is_Active=True).first()
    #             if active_person and active_person.version_no:
    #                 active_person.is_Active = False
    #                 prev_ver = active_person.version_no - 1
    #                 if prev_ver < 1:
    #                     continue
    #                 prev_person = db.session.query(PersonHistory).filter_by(id=pid, version_no=prev_ver).first()
    #                 if prev_person:
    #                     prev_person.is_Active = True
    #                     db.session.merge(Person(
    #                         id=prev_person.id,
    #                         name=prev_person.name,
    #                         gender=prev_person.gender,
    #                         dob=prev_person.dob,
    #                         age=prev_person.age,
    #                         path=prev_person.path
    #                     ))
    #             if not db.session.query(ImagePerson).filter_by(image_id=image_id, person_id=pid).first():
    #                 db.session.add(ImagePerson(image_id=image_id, person_id=pid))

    #         db.session.commit()
    #         ImageHistoryController.toggle_triggers(enable=True)
    #         return True

    #     except Exception as e:
    #         print(f"❌ Error in undo_data: {e}")
    #         db.session.rollback()
    #         ImageHistoryController.toggle_triggers(enable=True)
    #         return False


