import os,cv2,uuid,json,base64,face_recognition
from io import BytesIO

from datetime import datetime

from flask import jsonify, request
import numpy as np
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, text
from collections import defaultdict
import json

from Controller.LocationController import LocationController
from Controller.PersonController import PersonController
from Controller.TaggingController import TaggingController

from Model.Person import Person
from Model.Image import Image
from Model.Location import Location
from Model.Event import Event
from Model.ImageEvent import ImageEvent
from Model.ImagePerson import ImagePerson
from Model.Link import Link
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_
from sqlalchemy import update
from sqlalchemy.orm.attributes import flag_modified


from config import db

class ImageController:


# {
#   "2": {
#     "persons_id": [
#       {"id": 1, "name": "Ali","gender": "M"},
#       {"id": 2, "name": "Amna","gender": "F"}
#     ],
#     "event_names": ["iNDEPENDENCE DAY"],
#     "event_date": "2025-01-17",
#     "location": ["New yORK", "33.1234", "73.5678"]
#   }
# }


    @staticmethod
    def edit_image_data(data):
        
        
        print("😋 Parsed JSON:", data)

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Ensure that the input data has exactly one key (the image_id)
        if len(data) != 1:
            return jsonify({"error": "Invalid data format. Expecting a single numeric image_id as the key."}), 400

        # Extract the numeric image_id and its associated data
        try:
            print('editing...')
            image_id = int(next(iter(data.keys())))
            print('on the way...',image_id)
        except ValueError:
            return jsonify({"error": "image_id must be a numeric value"}), 400

        image_data = data.get(str(image_id))  # Get the data associated with the numeric image_id
        if not image_data:
            return jsonify({"error": "image_id data is required"}), 400
        
       

        persons = image_data.get('persons_id')  # Corrected key name to 'persons_id'
        event_names = image_data.get('event_names')
        event_date = image_data.get('event_date')
        location_data = image_data.get('location')


        # Fetch the image record by image_id
        image = Image.query.filter(Image.id == image_id).first()
        print(image)
        if not image:
            return jsonify({"error": "Image not found"}), 404

        # Update event_date and event_name if provided
        if event_date:
            print('========🎃')
            image.event_date = event_date
            # image.last_modified=datetime.utcnow()
        
        print('done with image')

        if event_names:
            image.events = []  # Clears the relationship in the ORM
            db.session.commit()
            
            # Access the related events
            # events = Event.query.filter(Event.name.in_(event_names)).all()
            # if not events:
            #     return {"error": "No matching events found"}, 404
            existing_events = Event.query.filter(Event.name.in_(event_names)).all()
            existing_event_names = {event.name for event in existing_events}
        
            # Determine missing event names
            missing_event_names = set(event_names) - existing_event_names
        
            # Create missing events
            new_events = []
            for name in missing_event_names:
                new_event = Event(name=name)
                db.session.add(new_event)
                new_events.append(new_event)
            
            # Commit new events to get their IDs
            db.session.commit()
        
            # Combine existing and new events
            all_events = existing_events + new_events

            # Associate image with events
            for event in all_events:
                if event not in image.events:
                    image.events.append(event)
            db.session.commit()
        
        print('done with events')
        # print(location_data)

        # Update location
        location_name = None
        latitude = 0.0
        longitude = 0.0

        # Update location if provided
        # Expecting location_data to be a dict
        # Expecting location_data as: ["Hall", 0.0, 0.0]
        if location_data and isinstance(location_data, list) and len(location_data) == 3 and str(location_data[0]).strip() != "":
            print('here in location ')
            try:
                location_name = str(location_data[0]).strip().title()
                latitude = 0.0
                longitude = 0.0
            except (ValueError, TypeError, IndexError) as e:
                print(f"❌ Invalid location data format or value: {location_data}")
                raise ValueError("Invalid location list format or coordinates") from e
        
            print(f"Checking for: {location_name}, {latitude}, {longitude}")
        
            existing_location = Location.query.filter(
                    func.lower(Location.name) == location_name.lower()
                ).first()
            print('existing_location',existing_location)
            if existing_location:
                print(f"✅ Found existing location with ID: {existing_location.id}")
                image.location_id = existing_location.id
            else:
                new_location = Location(name=location_name, latitude=0.0, longitude=0.0)
                db.session.add(new_location)
                db.session.flush()
                image.location_id = new_location.id
        
    
# ///////
        # Update persons if provided
        if persons:
            print('💜👌💜👌------------->',persons)
            for person_data in persons:
                print('💜--------------->personData',person_data)
                dob_str = person_data.get('dob')
                dob = None
                if dob_str :
                    try:
                        dob = datetime.fromisoformat(dob_str).date()  # 👈 converts '2000-08-24T18:32:38' to datetime.date(2000, 8, 24)

                    except ValueError:
                        print("Invalid DOB format and age_str:", dob_str)

                print(f"Received DOB: {dob_str}, Parsed DOB: {dob}")

                # person_id = person_data.get('id')
                person_name = person_data.get('name')
                person_path = person_data.get('path')
                print('------------>here',person_path)
                print(person_path)
                gender = person_data.get('gender')
                age =person_data.get('age')
                if person_path:
                    person = Person.query.filter(Person.path == person_path).first()
                    print('------------>',person)
                    if person:
                        if person_name and gender:
                            person.name = person_name
                            person.gender  = gender
                            person.dob = dob
                            person.age =age
                            person_data['path'] = person.path # saving this for tagging
                            person_data['dob'] = dob
                            person_data['age'] = age
                        else:
                            return jsonify({"error": f"Name is required for person with path {person_path}"}), 400
                        
                        # PersonController.recognize_person(person.path.replace('face_images','./stored-faces'), person_name)
                        # persons_db = Person.query.all()
                        # person_list = [
                        #    {"id": p.id, "name": p.name, "path": p.path }
                        #    for p in persons_db
                        #     ]
                        # links = Link.query.all()
                        
                        # link_list = [
                        #     {"person1_id": link.person1_id, "person2_id": link.person2_id}
                        #     for link in links
                        # ]                        
                        # res=ImageController.get_emb_names_for_recognition(person_list,link_list,person.path.split('/')[-1])
                        # embeddings = res.get_json("embeddings", {})
                        # # print(res)
                        # # print("embeddings",embeddings)
                        # for path in embeddings.get("embeddings", []):
                        #     pathes = f'face_images/{path}'
                        #     # print("Looking for person with path:", pathes)
                        
                        #     person = Person.query.filter_by(path=pathes).first()
                        #     if person:
                        #         # person.name = person_name
                        #         # db.session.add(person)
                        #         stmt = (
                        #                     update(Person)
                        #                     .where(Person.path == pathes)
                        #                     .values(name=person_name)  # even if same, it will still fire UPDATE
                        #                 )
                        #         db.session.execute(stmt)
                        #         person.name= person_name
                        #         db.session.add(person)
                        #         print("Updated:", pathes)
                        #     else:
                        #         print("No match found in DB for:", pathes)



                    else:
                        return jsonify({"error": f"Person with path {person_path} not found"}), 404
                else:
                    return jsonify({"error": "Person path is required"}), 400
        
        # Save changes to the database
        try:
            image.is_sync = False
            image.last_modified=datetime.utcnow()

            db.session.commit()
            # return jsonify({"message": "Image, events, location, and persons updated successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500



        if persons:
            print('💜👌💜👌------------->',persons)
            for person_data in persons:
                print('💜--------------->personData',person_data)
                dob_str = person_data.get('dob')
                dob = None
                if dob_str :
                    try:
                        dob = datetime.fromisoformat(dob_str).date()  # 👈 converts '2000-08-24T18:32:38' to datetime.date(2000, 8, 24)

                    except ValueError:
                        print("Invalid DOB format and age_str:", dob_str)

                print(f"Received DOB: {dob_str}, Parsed DOB: {dob}")

                # person_id = person_data.get('id')
                person_name = person_data.get('name')
                person_path = person_data.get('path')
                print('------------>here',person_path)
                print(person_path)
                gender = person_data.get('gender')
                age =person_data.get('age')
                if person_path:
                    person = Person.query.filter(Person.path == person_path).first()
                    print('------------>',person)
                    if person:
                        
                        PersonController.recognize_person(person.path.replace('face_images','./stored-faces'), person_name)
                        persons_db = Person.query.all()
                        person_list = [
                           {"id": p.id, "name": p.name, "path": p.path }
                           for p in persons_db
                            ]
                        links = Link.query.all()
                        
                        link_list = [
                            {"person1_id": link.person1_id, "person2_id": link.person2_id}
                            for link in links
                        ]                        
                        res=ImageController.get_emb_names_for_recognition(person_list,link_list,person.path.split('/')[-1])
                        embeddings = res.get_json("embeddings", {})
                        # print(res)
                        # print("embeddings",embeddings)
                        for path in embeddings.get("embeddings", []):
                            pathes = f'face_images/{path}'
                            # print("Looking for person with path:", pathes)
                        
                            person = Person.query.filter_by(path=pathes).first()
                            if person:
                                # person.name = person_name
                                # db.session.add(person)
                                stmt = (
                                            update(Person)
                                            .where(Person.path == pathes)
                                            .values(name=person_name)  # even if same, it will still fire UPDATE
                                        )
                                db.session.execute(stmt)
                                person.name= person_name
                                db.session.add(person)
                                print("Updated:", pathes)
                            else:
                                print("No match found in DB for:", pathes)
                    else:
                        return jsonify({"error": f"Person with path {person_path} not found"}), 404
                else:
                    return jsonify({"error": "Person path is required"}), 400



        try:
            image_path = image.path  # Full path to original image
            print(persons)
        # Reconstruct the tag JSON structure
            tag_data = {
                "persons": {
                    str(p.get("id")): {
                        "name": p.get("name"),
                        "gender": p.get("gender"),
                        "path": p.get("path", ""),
                        "dob": p.get("dob", ""),
                        "age": p.age("age","")
                    }
                    for p in persons
                } if persons else {},
                "event": event_names[0] if event_names else "",
                "location": location_name if location_name else "",
                "event_date": event_date if event_date else ""
            }

             # Read image file as binary to pass to TaggingController.tagImage
            with open(image_path, "rb") as img_file:
                img_bytes = BytesIO(img_file.read())
                tagged_img_io = TaggingController.tagImage(img_bytes, tag_data)

                if tagged_img_io:

                    with open(image_path, "wb") as output:
                        output.write(tagged_img_io.read())
                        return jsonify({f"Image saved with EXIF data at:": "{image_path}"}), 200
                else:
                    return jsonify({"error": "Tagging failed."}), 500

        except Exception as e:
            print(f"Error tagging and saving image: {str(e)}")
            return jsonify({"error": "EXIF metadata embedding failed."}), 500

    @staticmethod
    def edit_image_data_for_sync_iqra(data):
        
        
        print("😋 Parsed JSON:", data)

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Ensure that the input data has exactly one key (the image_id)
        if len(data) != 1:
            return jsonify({"error": "Invalid data format. Expecting a single numeric image_id as the key."}), 400

        # Extract the numeric image_id and its associated data
        try:
            print('editing...')
            image_id = int(next(iter(data.keys())))
            print('on the way...',image_id)
        except ValueError:
            return jsonify({"error": "image_id must be a numeric value"}), 400

        image_data = data.get(str(image_id))  # Get the data associated with the numeric image_id
        if not image_data:
            return jsonify({"error": "image_id data is required"}), 400
        
       

        persons = image_data.get('persons_id')  # Corrected key name to 'persons_id'
        event_names = image_data.get('event_names')
        event_date = image_data.get('event_date')
        location_data = image_data.get('location')


        # Fetch the image record by image_id
        image = Image.query.filter(Image.id == image_id).first()
        print(image)
        if not image:
            return jsonify({"error": "Image not found"}), 404

        # Update event_date and event_name if provided
        if event_date:
            print('========🎃')
            image.event_date = event_date
            # image.last_modified=datetime.utcnow()
        
        print('done with image')



        if event_names:
            image.events = []  # Clears the relationship in the ORM
            db.session.commit()
            
            # Access the related events
            # events = Event.query.filter(Event.name.in_(event_names)).all()
            # if not events:
            #     return {"error": "No matching events found"}, 404
            existing_events = Event.query.filter(Event.name.in_(event_names)).all()
            existing_event_names = {event.name for event in existing_events}
        
            # Determine missing event names
            missing_event_names = set(event_names) - existing_event_names
        
            # Create missing events
            new_events = []
            for name in missing_event_names:
                new_event = Event(name=name)
                db.session.add(new_event)
                new_events.append(new_event)
            
            # Commit new events to get their IDs
            db.session.commit()
        
            # Combine existing and new events
            all_events = existing_events + new_events

            # Associate image with events
            for event in all_events:
                if event not in image.events:
                    image.events.append(event)
            db.session.commit()
        
        print('done with events')
        # print(location_data)

        # Update location
        location_name = None
        latitude = None
        longitude = None

        # Update location if provided
        # Expecting location_data to be a dict
        # Expecting location_data as: ["Hall", 0.0, 0.0]
        if location_data and isinstance(location_data, list) and len(location_data) == 3 and str(location_data[0]).strip() != "":
            print('here in location ')
            try:
                location_name = str(location_data[0]).strip().title()
                latitude = 0.0
                longitude = 0.0
            except (ValueError, TypeError, IndexError) as e:
                print(f"❌ Invalid location data format or value: {location_data}")
                raise ValueError("Invalid location list format or coordinates") from e
        
            print(f"Checking for: {location_name}, {latitude}, {longitude}")
        
            existing_location = Location.query.filter(
                    func.lower(Location.name) == location_name.lower()
                ).first()
            print('existing_location',existing_location)
            if existing_location:
                print(f"✅ Found existing location with ID: {existing_location.id}")
                image.location_id = existing_location.id
            else:
                new_location = Location(name=location_name, latitude=0.0, longitude=0.0)
                db.session.add(new_location)
                db.session.flush()
                image.location_id = new_location.id
        
    
# ///////
        # Update persons if provided
        if persons:
            print('💜👌💜👌------------->',persons)
            for person_data in persons:
                print('💜--------------->personData',person_data)
                dob_str = person_data.get('dob')
                dob = None
                if dob_str:
                    try:
                        # Try ISO format (e.g., '2000-08-24T18:32:38')
                        dob = datetime.fromisoformat(dob_str).date()
                    except ValueError:
                        try:
                            # Try custom format (e.g., 'Jun 19, 1984 12:46:02 AM')
                            dob = datetime.strptime(dob_str, "%b %d, %Y %I:%M:%S %p").date()
                            # dob = dob.strftime("%Y-%m-%d")
                        except ValueError:
                            print("❌ Still Invalid DOB format:", dob_str)

                print(f"Received DOB: {dob_str}, Parsed DOB: {dob}")

                # person_id = person_data.get('id')
                person_name = person_data.get('name')
                person_path = person_data.get('path')
                print('------------>here',person_path)
                print(person_path)
                gender = person_data.get('gender')
                age =person_data.get('age')
                if person_path:
                    person = Person.query.filter(Person.path == person_path).first()
                    print('------------>',person)
                    if person:
                        if person_name and gender:
                            person.name = person_name
                            person.gender  = gender
                            person_data['path'] = person.path # saving this for tagging
                            # person.dob = person.dob
                            # person.age =person.age
                        else:
                            return jsonify({"error": f"Name is required for person with path {person_path}"}), 400
                        
                        PersonController.recognize_person(person.path.replace('face_images','./stored-faces'), person_name)
                        persons_db = Person.query.all()
                        person_list = [
                           {"id": p.id, "name": p.name, "path": p.path }
                           for p in persons_db
                            ]
                        links = Link.query.all()
                        
                        link_list = [
                            {"person1_id": link.person1_id, "person2_id": link.person2_id}
                            for link in links
                        ]                        
                        res=ImageController.get_emb_names_for_recognition(person_list,link_list,person.path.split('/')[-1])
                        embeddings = res.get_json("embeddings", {})
                        # print(res)
                        # print("embeddings",embeddings)
                        for path in embeddings.get("embeddings", []):
                            pathes = f'face_images/{path}'
                            # print("Looking for person with path:", pathes)
                        
                            person = Person.query.filter_by(path=pathes).first()
                            if person:
                                # person.name = person_name
                                # db.session.add(person)
                                stmt = (
                                            update(Person)
                                            .where(Person.path == pathes)
                                            .values(name=person_name)  # even if same, it will still fire UPDATE
                                        )
                                db.session.execute(stmt)
                                person.name= person_name
                                db.session.add(person)
                                print("Updated:", pathes)
                            else:
                                print("No match found in DB for:", pathes)

                                    

                        print("person_name:", person_name)
                        print("gender:", gender)
                        print("dob:", dob)
                        if person:
                            if person_name and gender :
                                person.name = person_name
                                person.gender = gender
                                person.dob = dob
                                person.age = age
                                person_data['id'] = person.id  # For tagging
                            else:
                                return jsonify({"error": f"Name is required for person with path {person_path}"}), 400
                        else:
                            print("No match found in DB for:", pathes)


                    else:
                        return jsonify({"error": f"Person with path {person_path} not found"}), 404
                else:
                    return jsonify({"error": "Person path is required"}), 400

        # Save changes to the database
        try:
            image.is_sync = False
            image.last_modified=datetime.utcnow()

            db.session.commit()
            # return jsonify({"message": "Image, events, location, and persons updated successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

        try:
            image_path = image.path  # Full path to original image
            print(persons)
        # Reconstruct the tag JSON structure
            tag_data = {
                "persons": {
                    str(p.get("id")): {
                        "name": p.get("name"),
                        "gender": p.get("gender"),
                        "path": p.get("path", "")
                    }
                    for p in persons
                } if persons else {},
                "event": event_names[0] if event_names else "",
                "location": location_name if location_name else "",
                "event_date": event_date if event_date else ""
            }

             # Read image file as binary to pass to TaggingController.tagImage
            with open(image_path, "rb") as img_file:
                img_bytes = BytesIO(img_file.read())
                tagged_img_io = TaggingController.tagImage(img_bytes, tag_data)

                if tagged_img_io:

                    with open(image_path, "wb") as output:
                        output.write(tagged_img_io.read())
                        return jsonify({f"Image saved with EXIF data at:": "{image_path}"}), 200
                else:
                    return jsonify({"error": "Tagging failed."}), 500

        except Exception as e:
            print(f"Error tagging and saving image: {str(e)}")
            return jsonify({"error": "EXIF metadata embedding failed."}), 500


     # -=============    Searching          ===============


# {
#     "name": ["Ali", "amna"],
#     "gender": "M",
#     "events": ["Birthday"],
#     "capture_date": ["02-12-2021"],
#     "location": {
#         "latitude": "33.1234",
#         "longitude": "73.5678"
#     }
# }


# {
#     "name": ["Ali", "amna"],
#     "gender": ["F"],
#     "events": ["Birthday Party"],
#     "capture_date": ["2023-12-01"],
#     "location": {
#     "latitude":"51.50735100",
#     "longitude":"-0.12775800"
# } 
# }
    # @staticmethod
    # def searching_on_image(): 
    #     data = request.get_json()
    #     print (data)

    #     if not data:
    #         return jsonify({"error": "No data provided"}), 400

    #     # Extract parameters
    #     person_names = data.get('name', [])  
    #     gender = data.get('gender', [])  # Now a list
    #     events = data.get('selectedEvents', [])
    #     capture_dates = data.get('capture_date', [])
    #     age= data.get('age')
    #     locations = data.get('location', {})

    #     person_ids = []
    #     image_ids = []

    #     # # Search for persons
    #     # if person_names:
    #     #     for name in person_names:
    #     #         query = Person.query.filter(Person.name == name)

    #     #         # If gender is provided and is a list, filter by it
    #     #         if gender:
    #     #             query = query.filter(Person.gender.in_(gender))  # ✅ FIXED

    #     #         persons = query.all()

    #     #         for person in persons:
    #     #             if person:  
    #     #                 person_ids.append(person.id)  
    #     # Search for persons
    #     if person_names:
    #         for name in person_names:
    #             query = Person.query.filter(Person.name == name)

    #             # If gender is provided and is a list, filter by it
    #             if gender:
    #                 query = query.filter(Person.gender.in_(gender))

    #             # ✅ If age is provided, filter by it as well
    #             if isinstance(age, int) and age > 0:
    #                 query = query.filter(Person.age == age)

    #             # Get matching persons
    #             persons = query.all()

    #             # Add their IDs to the list
    #             for person in persons:
    #                 if person:
    #                     person_ids.append(person.id)

    #     # Search for images linked to persons
    #     if person_ids:
    #         images = (
    #             db.session.query(Image.id)  # Select the id column from the Image table
    #             .join(ImagePerson, ImagePerson.image_id == Image.id)  # Join ImagePerson with Image
    #             .join(Person, Person.id == ImagePerson.person_id)  # Join Person with ImagePerson
    #             .filter(ImagePerson.person_id.in_(person_ids))  # Filter by the list of person_ids
    #             .all()
    #         )

    #         for image in images:
    #             image_ids.append(image.id)

    #     # Search for images linked to events
    #     event_ids = []
    #     if events:
    #         for event_name in events:
    #             event = Event.query.filter(Event.name == event_name).first()
    #             if event:
    #                 event_ids.append(event.id)

    #         if event_ids:
    #             images_of_events = (
    #                 db.session.query(Image.id)
    #                 .join(ImageEvent, ImageEvent.image_id == Image.id)
    #                 .join(Event, Event.id == ImageEvent.event_id)
    #                 .filter(ImageEvent.event_id.in_(event_ids))
    #                 .all()
    #             )

    #             for image in images_of_events:
    #                 image_ids.append(image.id)

    #     # Search for images by capture date
    #     if capture_dates:
    #         for date in capture_dates:
    #             image_dates = Image.query.filter(Image.capture_date == date).all()
    #             for image in image_dates:
    #                 image_ids.append(image.id)

    #     # Search for images by location
    #     if locations:
    #         name = locations.get('Name')
    #         latitude = locations.get('latitude')
    #         longitude = locations.get('longitude')
    #         print(name,latitude,longitude)

    #         # if latitude and longitude :
    #             # loc_name = LocationController.get_location_from_lat_lon(latitude, longitude)
    #         loc_name = name


    #         if loc_name:
    #             location = Location.query.filter(Location.name == loc_name).first()
    #             if location:
    #                 images_at_location = Image.query.filter(Image.location_id == location.id).all()
    #                 for image in images_at_location:
    #                     image_ids.append(image.id)

    #     # Retrieve final image paths
    #     image_paths = []
    #     if image_ids:
    #         images = Image.query.filter(Image.id.in_(image_ids)).all()
    #         for image in images:
    #             if image:  
    #                 image_paths.append(image.path)

    #     return jsonify({"paths": image_paths}), 200  

    @staticmethod
    def searching_on_image():
        data = request.get_json()
        print(data)

        if not data:
            return jsonify({"error": "No data provided"}), 400

        person_names = data.get('name', [])
        gender = data.get('gender', [])
        events = data.get('selectedEvents', [])
        capture_dates = data.get('capture_date', [])
        age = data.get('age')
        location_data = data.get('location', {})

        image_ids = set()
        has_any_filter = False

        # ✅ PERSON FILTER (all combinations like Kotlin)
        person_ids = []
        if person_names or gender or (isinstance(age, int) and age > 0):
            has_any_filter = True

            if person_names and gender and isinstance(age, int) and age > 0:
                persons = Person.query.filter(
                    Person.name.in_(person_names),
                    Person.gender.in_(gender),
                    Person.age == age
                ).all()
            elif person_names and gender:
                persons = Person.query.filter(
                    Person.name.in_(person_names),
                    Person.gender.in_(gender)
                ).all()
            elif person_names and isinstance(age, int) and age > 0:
                persons = Person.query.filter(
                    Person.name.in_(person_names),
                    Person.age == age
                ).all()
            elif gender and isinstance(age, int) and age > 0:
                persons = Person.query.filter(
                    Person.gender.in_(gender),
                    Person.age == age
                ).all()
            elif person_names:
                persons = Person.query.filter(Person.name.in_(person_names)).all()
            elif gender:
                persons = Person.query.filter(Person.gender.in_(gender)).all()
            elif isinstance(age, int) and age > 0:
                persons = Person.query.filter(Person.age == age).all()
            else:
                persons = []

            person_ids = [p.id for p in persons]

            if person_ids:
                person_images_query = (
                    db.session.query(Image.id)
                    .join(ImagePerson, ImagePerson.image_id == Image.id)
                    .filter(ImagePerson.person_id.in_(person_ids))
                )

                # ✅ Date filter
                if capture_dates:
                    person_images_query = person_images_query.filter(Image.capture_date.in_(capture_dates))

                # ✅ Location filter
                if location_data:
                    loc_name = location_data.get("Name", "")
                    if loc_name:
                        location = Location.query.filter(Location.name == loc_name).first()
                        if location:
                            person_images_query = person_images_query.filter(Image.location_id == location.id)

                # ✅ Event filter
                if events:
                    event_ids = [e.id for e in Event.query.filter(Event.name.in_(events)).all()]
                    if event_ids:
                        person_images_query = (
                            person_images_query
                            .join(ImageEvent, ImageEvent.image_id == Image.id)
                            .filter(ImageEvent.event_id.in_(event_ids))
                        )

                # ✅ Add all final image IDs
                for img in person_images_query.all():
                    image_ids.add(img.id)

        # ✅ GLOBAL FILTERS (if person filters were not used or gave no results)
        if not person_ids:
            if events or capture_dates or location_data:
                has_any_filter = True

                query = db.session.query(Image.id)

                # Event filter
                if events:
                    event_ids = [e.id for e in Event.query.filter(Event.name.in_(events)).all()]
                    if event_ids:
                        query = (
                            query.join(ImageEvent, ImageEvent.image_id == Image.id)
                            .filter(ImageEvent.event_id.in_(event_ids))
                        )

                # Date filter
                if capture_dates:
                    query = query.filter(Image.capture_date.in_(capture_dates))

                # Location filter
                if location_data:
                    loc_name = location_data.get("Name", "")
                    if loc_name:
                        location = Location.query.filter(Location.name == loc_name).first()
                        if location:
                            query = query.filter(Image.location_id == location.id)

                # ✅ Add final filtered image IDs
                for img in query.all():
                    image_ids.add(img.id)

        # ✅ Return if no filters applied
        if not has_any_filter:
            return jsonify({"paths": []}), 200

        # ✅ Get image paths from final image IDs
        final_image_ids = list(image_ids)
        image_paths = []
        if final_image_ids:
            images = Image.query.filter(Image.id.in_(final_image_ids)).all()
            image_paths = [img.path for img in images if img]

        return jsonify({"paths": image_paths}), 200



    @staticmethod
    def add_image(data):
        try:
            # 1. Check if image already exists based on HASH
            existing_image = Image.query.filter_by(hash=data['hash']).first()
            if existing_image:
                existing_image.is_deleted = 0  # Mark as not deleted
                existing_image.last_modified = datetime.utcnow()
                db.session.commit()
                print(f"⚠️ Image already exists with hash: {existing_image.hash}")
                return jsonify({'message': 'Image already exists'}), 200
                
            
            # 2. Insert new image record
            image = Image(
                path=data['path'],
                hash=data['hash'],  # Save the hash into database
                is_sync=data.get('is_sync', 0),
                capture_date=data.get('capture_date', datetime.utcnow()),
                event_date=data.get('event_date', None),
                last_modified=datetime.utcnow()
            )
            db.session.add(image)
            db.session.commit()
            print(f"✅ Image saved: {image.path}")

            # 3. Extract faces from the saved image
            # extracted_faces = PersonController.extract_face(image.path.replace('images', 'Assets'))
                        
            # Combine base path and relative path safely
            # path =relative path
            full_path = os.path.join(data['path'])
            clean_path = os.path.abspath(full_path)
            print("in a method :",clean_path)

            # Now use this full path
            extracted_faces = PersonController.extract_face(full_path)
            if not extracted_faces:
                return jsonify({'message': 'No faces found'}), 200

            # 4. For each extracted face
            for face_data in extracted_faces:
                face_path = face_data["face_path"]
                face_filename = os.path.basename(face_path)
                db_face_path = f"face_images/{face_filename}"

                # Check if this face already exists based on path
                # matched_person = Person.query.filter_by(path=db_face_path).first()

                match_data = PersonController.recognize_person(f"./stored-faces/{face_filename}") #db_face_path.path.replace('face_images','./stored-faces')
                
                if match_data:
                    result = match_data["results"][0]
                    print("result in recognition",result)
                    file_path = result["file"]  # e.g. "stored-faces\\3ec88a981d204ab8b0501cc4da150bf5.jpg"
                    normalized_path = file_path.replace("\\", "/")
                    face_path_1 = normalized_path.replace('stored-faces', 'face_images')
                    matched_person = Person.query.filter_by(path=face_path_1).first()

                    PersonController.update_face_paths_json("./stored-faces/person_group.json", face_filename,matchedPath=os.path.basename(result["file"]))

                    for res in  match_data["results"]:
                        resembeled_path = os.path.basename(res["file"])
                        print("resembeled path",resembeled_path)
                        if(face_filename != resembeled_path):
                            PersonController.update_face_paths_json("./stored-faces/person_group.json", face_filename, matchedPath=resembeled_path)


                # 5. If not found, create a new person
                if not matched_person:
                    new_person = Person(
                        name="unknown",
                        path=db_face_path,
                        gender="U"  # Unknown gender
                    )
                    db.session.add(new_person)
                    db.session.commit()
                    print(f"✅ New person added: {new_person.path}")
                    matched_person = new_person
                else:
                    new_person = Person(
                        name=matched_person.name,
                        path=db_face_path,
                        gender=matched_person.gender  # Unknown gender
                    )
                    db.session.add(new_person)
                    db.session.commit()
                    matched_person = new_person

                # 6. Link the image and the person
                image_person = ImagePerson(image_id=image.id, person_id=matched_person.id)
                db.session.add(image_person)

            db.session.commit()
            return jsonify({'message': 'Image and faces saved successfully'}), 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return jsonify({'error': str(e)}), 500

    
    
    

    @staticmethod
    def get_image_details(image_id):
            image = Image.query.get(image_id)
            
            if not image:
                return jsonify({'error': 'Image not found'}), 404
            
            return jsonify(image.to_dict())

    @staticmethod
    def get_image_complete_details(image_id):
        image = Image.query.get(image_id)
        if not image:
            return jsonify({"error": "Image not found"}), 404

        location_data = None
        if image.location:
            location_data = {
            "id": image.location.id,
            "name": image.location.name,
            "latitude": float(image.location.latitude),
            "longitude": float(image.location.longitude)
            }

# {"id": person.id, "name": person.name, "path": person.path, "gender": person.gender,
#          "DOB": person.dob.strftime('%Y-%m-%d') if person.dob else None,
#          "Age":person.age}
        persons = [
        {"id": person.id, 
         "name": person.name, 
         "path": person.path, 
         "gender": person.gender,
        #    "dob":person.dob,
        #   "age":person.age

        #"dob": person.dob.strftime('%Y-%m-%d') if person.dob else None,
        #"age":person.age 
        
        # ya comment rhna dena isy nhi hatana ok na 
         "DOB": person.dob.strftime('%Y-%m-%d') if person.dob else None,
         "Age":person.age
         }
        for person in image.persons
        ]
    
        events = [
        {"id": event.id, "name": event.name}
        for event in image.events
        ]

        image_data = {
        "id": image.id,
        "path": image.path,
        "is_sync": image.is_sync,
        "capture_date": image.capture_date.strftime('%Y-%m-%d') if image.capture_date else None,
        "event_date": image.event_date.strftime('%Y-%m-%d') if image.event_date else None,
        "last_modified": image.last_modified.strftime('%Y-%m-%d %H:%M:%S') if image.last_modified else None,
        "hash":image.hash,
        "location": location_data,
        "persons": persons,
        "events": events
        }
    
        return image_data

    # @staticmethod
    # def delete_image(image_id):
    #         image = Image.query.get(image_id)
    #         if not image:
    #             return jsonify({'error': 'Image not found'}), 404
            
    #         try:
    #             db.session.delete(image)
    #             db.session.commit()
    #             return jsonify({'message': 'Image deleted successfully'}), 200
    #         except Exception as e:
    #             db.session.rollback()
    #             return jsonify({'error': str(e)}), 500
            ######delete metaddta
   




        # Replace with your actual database module
    @staticmethod
    def delete_metadata(image_id):
        try:
            # Save metadata to ImageHistory before clearing
            db.session.execute(text("""
                INSERT INTO ImageHistory (
                    id, path, is_sync, capture_date, event_date, last_modified,
                    location_id, hash, version_no
                )
                SELECT 
                    id, path, is_sync, capture_date, event_date, last_modified,
                    location_id, hash,
                    COALESCE((SELECT MAX(version_no) FROM ImageHistory WHERE id = :image_id), 0) + 1
                FROM Image
                WHERE id = :image_id
            """), {'image_id': image_id})

            # Save Image-Person relationships to history
            db.session.execute(text("""
                INSERT INTO ImagePersonHistory (image_id, person_id, version_no)
                SELECT image_id, person_id,
                    COALESCE((SELECT MAX(version_no) FROM ImagePersonHistory WHERE image_id = :image_id), 0) + 1
                FROM ImagePerson
                WHERE image_id = :image_id
            """), {'image_id': image_id})

            # Save Image-Event relationships to history
            db.session.execute(text("""
                INSERT INTO ImageEventHistory (image_id, event_id, version_no)
                SELECT image_id, event_id,
                    COALESCE((SELECT MAX(version_no) FROM ImageEventHistory WHERE image_id = :image_id), 0) + 1
                FROM ImageEvent
                WHERE image_id = :image_id
            """), {'image_id': image_id})

            # Clear metadata fields from the Image table
            db.session.execute(text("""
                UPDATE Image 
                SET location_id = NULL, event_date = NULL 
                WHERE id = :image_id
            """), {'image_id': image_id})

            # Delete associated records from relational tables
            db.session.execute(text("DELETE FROM ImagePerson WHERE image_id = :image_id"), {'image_id': image_id})
            db.session.execute(text("DELETE FROM ImageEvent WHERE image_id = :image_id"), {'image_id': image_id})

            db.session.commit()
            return jsonify({'message': 'Metadata cleared and saved to history successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def delete_image_metadata(image_id):
        try:
            image = image = Image.query.filter(Image.id == image_id).first()

            image.event_date = None
            image.location_id = None
            image.last_modified=datetime.utcnow()
            image.events = []
            image.persons = []
            image.is_sync = False
            
            db.session.commit()

            tag_data = {
                "event": "",
                "event_date": "",
                "location": "",
                "persons": {}
                }
            
            image_path = image.path
            with open(image_path, "rb") as img_file:
                img_bytes = BytesIO(img_file.read())
                tagged_img_io = TaggingController.tagImage(img_bytes, tag_data)

                if tagged_img_io:

                    with open(image_path, "wb") as output:
                        output.write(tagged_img_io.read())
                        return jsonify({f"Image saved with EXIF data at:": "{image_path}"}), 200
                else:
                    return jsonify({"error": "Tagging failed."}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def delete_image(image_id):
        image = Image.query.get(image_id)  # Fetch image from the database by ID
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404  # Return error if image not found
        
        try:
            image.is_deleted = True  # Mark the image as deleted (soft delete)
            db.session.commit()  # Commit the change to the database
            
            return jsonify({'message': 'Image marked as deleted successfully'}), 200  # Success response
        except Exception as e:
            db.session.rollback()  # Rollback any changes in case of error
            return jsonify({'error': str(e)}), 500    
    
    @staticmethod
    def group_by_date():
        try:
            # Query all images from the database
            images = Image.query.filter_by(is_deleted=False).all()

            
            if not images:
                return jsonify({"message": "No images found"}), 200

            
            grouped_images = defaultdict(list)
            for image in images:
                grouped_images[image.capture_date].append(image.to_dict())

            # Prepare the response in the desired format
            response = {str(i + 1): records for i, records in enumerate(grouped_images.values())}
            return jsonify(response), 200
        
        except Exception as e:
            # Catch any exceptions and return an error response
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    def Load_images():
        data = request.get_json()
        print("dd",data)
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Fetch the filtering criteria
        person_id = data.get("person_id")  # Expecting a single value, not a list
        event_name = data.get("event")  # Expecting a single event name
        capture_date = data.get("capture_date")  # Expecting a single date
        location_name = data.get("location")  # Expecting a single location name
        
        # image_ids = set()  # Using set to avoid duplicates
    
        # # 🔹 Filter by Person ID
        # # 🔹 Filter by Person ID and include linked persons via the Link table
        # if person_id:
        #     person = Person.query.filter_by(id=person_id).first()
        
        #     if person:
        #         # Get all linked person IDs (bidirectional lookup)
        #         linked_ids = (
        #             db.session.query(Link.person2_id)
        #             .filter(Link.person1_id == person_id)
        #             .union(
        #                 db.session.query(Link.person1_id)
        #                 .filter(Link.person2_id == person_id)
        #             )
        #             .all()
        #         )
        
        #         # Flatten and combine all linked person IDs with the original person_id
        #         linked_person_ids = {person_id} | {id for (id,) in linked_ids}
        
        #         # Get all image IDs associated with those persons
        #         person_images = (
        #             db.session.query(Image.id)
        #             .join(ImagePerson, ImagePerson.image_id == Image.id)
        #             .filter(ImagePerson.person_id.in_(linked_person_ids))
        #             .all()
        #         )
        
        #         image_ids.update([image.id for image in person_images])


        image_ids = set()

        if person_id:
        #  print(person_id)
         # Fetch person and their directly linked images
        #  person = Person.query.filter_by(id=person_id).first()
        #  if person:
        #       person_images = person.images  # Assuming there's a relationship set up
        #       image_ids.update([image.id for image in person_images])

              # Fetch the image groups that include this person

         groups = PersonController.get_person_groups()
         print("Returned groups:", groups)  # DEBUG

         for group in groups:
             print("Group Person ID:", group.get("Person", {}).get("id"))
             if int(group.get("Person", {}).get("id")) == int(person_id):
                 print("Group Person ID:", group.get("Person", {}).get("id"), type(group.get("Person", {}).get("id")))
                 print("Given Person ID:", person_id, type(person_id))

                 for img in group.get("Images", []):
                     image_ids.add(img["id"])  # Ensure all group images are added

        
            
        # 🔹 Filter by Event Name
        if event_name:
            event = Event.query.filter_by(name=event_name).first()
            if event:
                event_images = (
                    db.session.query(Image.id)
                    .join(ImageEvent, ImageEvent.image_id == Image.id)
                    .filter(ImageEvent.event_id == event.id)
                    .all()
                )
                image_ids.update([image.id for image in event_images])
    
        # 🔹 Filter by Capture Date
        if capture_date:
            date_images = Image.query.filter_by(capture_date=capture_date).all()
            image_ids.update([image.id for image in date_images])
    
        # 🔹 Filter by Location Name
        if location_name:
            location = Location.query.filter_by(name=location_name).first()
            if location:
                location_images = Image.query.filter_by(location_id=location.id).all()
                image_ids.update([image.id for image in location_images])
    
        # 🔹 Fetch and return full image details
        if image_ids:
            images = Image.query.filter(Image.id.in_(image_ids)).all()
            image_data = []
    
            for img in images:
                # Fetch location name
                location = Location.query.filter_by(id=img.location_id).first()
                location_name = location.name if location else None
    
                # Fetch all events associated with the image
                events = (
                    db.session.query(Event.id, Event.name)
                    .join(ImageEvent, ImageEvent.event_id == Event.id)
                    .filter(ImageEvent.image_id == img.id)
                    .all()
                )
                event_list = [{"id": event.id, "name": event.name} for event in events]
    
                # Fetch all persons associated with the image
                persons = (
                    db.session.query(Person.id, Person.name, Person.gender)
                    .join(ImagePerson, ImagePerson.person_id == Person.id)
                    .filter(ImagePerson.image_id == img.id)
                    .all()
                )
                person_list = [
                    {"id": person.id, "name": person.name, "gender": person.gender}
                    for person in persons
                ]
    
                # Add image data to the list
                image_data.append(
                    {
                        "id": img.id,
                        "path": img.path,
                        "is_sync": img.is_sync,
                        "capture_date": img.capture_date,
                        #"location_id": img.location_id,
                        #"location_name": location_name,
                        "event_date": img.event_date,
                        "last_modified": img.last_modified,
                        "events": event_list,
                        "persons": person_list,
                        "location": {
                        "id": location.id if location else None,
                        "name": location.name if location else None,
                        "latitude": location.latitude if location else None,
                        "longitude": location.longitude if location else None,
                    },
                    }
                )
            print(image_data)
            # Wrap the response data correctly
            return jsonify({"images": image_data}), 200
    
        return jsonify({"error": "No matching images found"}), 404

       
            
    @staticmethod
    def get_person_images(json_data):
        data = request.get_json()
    
        if not data:
            return jsonify({"error": "No data provided"}), 400
    
        images = json_data["images"]  # This is a list, not a query
        image_person_map = json_data["image_person_map"]
        links = json_data.get("links", [])
    
        person_id = data.get("person_id")
        print("Given Person ID:", person_id, type(person_id))
        image_ids = set()
    
        if person_id:
            groups = PersonController.get_single_person_groups(json_data)
            print("Returned groups:", groups)  # DEBUG
    
            for group in groups:
                person = group.get("Person", {})
                group_person_id = person.get("id")
                print("Group Person ID:", group_person_id)
    
                if group_person_id is not None and int(group_person_id) == int(person_id):
                    for img in group.get("Images", []):
                        image_ids.add(img["id"])  # Add image ID
    
        if image_ids:
            # ✅ Filter the list using list comprehension
            filtered_images = [img for img in images if img["id"] in image_ids]
            image_data = []
    
            for img in filtered_images:
                # Simulate DB join by filtering image_person_map list
                persons = [
                    {"id": item["person_id"]}
                    for item in image_person_map
                    if item["image_id"] == img["id"]
                ]
    
                image_data.append({
                    "id": img["id"],
                    "path": img["path"],
                    "persons": persons
                })
    
            print("Final image data:", image_data)
            return jsonify({"images": image_data}), 200
    
        return jsonify({"error": "No matching images found"}), 404
    
       
            
         
        
    @staticmethod
    # getting unlabel images
    def get_unedited_images():
        unedited_images = (
            db.session.query(Image)
            .outerjoin(Image.persons)
            .outerjoin(Image.events)
            .filter(
                (Image.is_deleted != 1),
                or_(
                    Image.event_date.is_(None),
                    Image.location_id.is_(None),
                    ~Image.persons.any(),  # No persons at all
                    Image.persons.any(
                        or_(
                            Person.name == "unknown",
                            Person.name.is_(None),
                            Person.gender.is_(None),
                            Person.gender == 'U',
                            Person.dob=='',
                            Person.dob.is_(None)
                        )
                    ),
                    ~Image.events.any(),  # No events at all
                    Image.events.any(
                        or_(
                            Event.name == "unknown",
                            Event.name.is_(None)
                        )
                    )
                )
            )
            .all()
        )
    
        # Convert images to JSON format
        image_list = []
        for img in unedited_images:
            image_list.append({
                "id": img.id,
                "path": img.path,
                "is_sync": img.is_sync,
                "capture_date": img.capture_date.strftime('%Y-%m-%d') if img.capture_date else None,
                "event_date": img.event_date.strftime('%Y-%m-%d') if img.event_date else None,
                "last_modified": img.last_modified.strftime('%Y-%m-%d %H:%M:%S') if img.last_modified else None,
                "location_id": img.location_id,
                "persons": [{"id": p.id, "name": p.name, "gender": p.gender} for p in img.persons],
                "events": [{"id": e.id, "name": e.name} for e in img.events]
            })
    
        return jsonify({"status": "success", "unedited_images": image_list}), 200


   
    def get_all_person():
            persons = (
                db.session.query(Person.id, Person.name, Person.path, Person.gender)
                .all()
                )    
        
        # Convert result to list of dictionaries
            return [{"id": p.id, "name": p.name, "path": p.path, "gender": p.gender} for p in persons]

#Aimen's mobile app code 
    @staticmethod
    def mobile_img_processing(image_path):
        try:
            # Extract faces from the image
            extracted_faces = PersonController.extract_face(image_path)
            if not extracted_faces:
                    return jsonify([]), 200    
            response_data = []
    
            for face_data in extracted_faces:
                face_path = face_data["face_path"]
                face_filename = os.path.basename(face_path)
                db_face_path = f"face_images/{face_filename}"
    
                matched_person = None
                match_data = PersonController.recognize_person(f"./stored-faces/{face_filename}")
                
                if match_data and "results" in match_data and match_data["results"]:

                    result = match_data["results"][0]
                    file_path = result["file"]
                    normalized_path = file_path.replace("\\", "/")
                    face_path_1 = normalized_path.replace('stored-faces', 'face_images')
                    matched_person = Person.query.filter_by(path=face_path_1).first()

                    for res in  match_data["results"]:
                        resembeled_path = os.path.basename(res["file"])
                        print("resembeled path",resembeled_path)
                        if(face_filename != resembeled_path):
                            PersonController.update_face_paths_json("./stored-faces/person_group.json", face_filename, matchedPath=resembeled_path)

    
                if not matched_person:
                    new_person = Person(
                        name="unknown",
                        path=db_face_path,
                        # gender="U"
                    )
                     # Get ID without committing
                    print(f"✅ New person added: {new_person.path}")
                    matched_person = new_person
                    response_data.append({
                        "status": "new_person_detected",
                        "name": new_person.name,
                        "path": new_person.path,
                        # "gender": new_person.gender
                    })
                else:
                    new_person = Person(
                        name=matched_person.name,
                        path=db_face_path,
                        # gender=matched_person.gender
                    )
                    
                    matched_person = new_person
                    response_data.append({
                        "status": "known_person_instance_detected",
                        "name": new_person.name,
                        "path": new_person.path,
                        # "gender": new_person.gender
                    })
    
                # Optionally link person to image here if image object is available
                # image_person = ImagePerson(image_id=image.id, person_id=matched_person.id)
                # db.session.add(image_person)
    
            
            return jsonify(response_data), 201
    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def build_link_groups(links):
        # Union-Find for grouping linked persons
        parent = {}
    
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
    
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[py] = px
    
        # Initialize parent map
        for link in links:
            # Dynamically detect key styleAdd commentMore actions
            if "person1Id" in link and "person2Id" in link:
                a, b = link["person1Id"], link["person2Id"]
            elif "person1_id" in link and "person2_id" in link:
                a, b = link["person1_id"], link["person2_id"]
            else:
                continue  # Skip if keys are missing or inconsistent
        
            if a not in parent:
                parent[a] = a
            if b not in parent:
                parent[b] = b
            union(a, b)
    
        # Build groups
        groups = {}
        for person_id in parent:
            root = find(person_id)
            if root not in groups:
                groups[root] = []
            groups[root].append(person_id)
    
        return groups
    @staticmethod
    def are_groups_linked(group1, group2, persons, links):
        id_by_emb = {person["path"].split("/")[-1]: person["id"] for person in persons}
        
        ids1 = {id_by_emb.get(name) for name in group1 if id_by_emb.get(name) is not None}
        ids2 = {id_by_emb.get(name) for name in group2 if id_by_emb.get(name) is not None}
    
        # for link in links:
        #     if (link["person1_id"] in ids1 and link["person2_id"] in ids2) or \
        #        (link["person2_id"] in ids1 and link["person1_id"] in ids2):
        #         return True
        # return False
        for link in links:
            # Dynamically detect the keysAdd commentMore actions
            if "person1Id" in link and "person2Id" in link:
                p1 = link["person1Id"]
                p2 = link["person2Id"]
            elif "person1_id" in link and "person2_id" in link:
                p1 = link["person1_id"]
                p2 = link["person2_id"]
            else:
                continue  # Skip if neither key pattern is present
    
            if (p1 in ids1 and p2 in ids2) or (p2 in ids1 and p1 in ids2):
                return True
        return False
    @staticmethod
    def merge_linked_overlapping_groups(group_dict, persons, links):
        groups = [set(v) for v in group_dict.values()]
        merged = []
    
        while groups:
            first, *rest = groups
            first = set(first)
    
            changed = True
            while changed:
                changed = False
                rest2 = []
                for r in rest:
                    if first & r and ImageController.are_groups_linked(first, r, persons, links):
                        first |= r
                        changed = True
                    else:
                        rest2.append(r)
                rest = rest2
            merged.append(first)
            groups = rest

    # Build merged dict using first item of each group as key
        merged_dict = {}
        for group in merged:
            group = sorted(group)
            merged_dict[group[0]] = group
    
        return merged_dict


    @staticmethod
    def get_emb_names(persons, links, person1,personrecords):
        # print(person1)
        # print(persons)
        # print(links)
        # print(personrecords)
        if "personPath" in person1:
           emb_name = person1["personPath"].split('/')[-1]
        elif "path" in person1:
            emb_name = person1["path"].split('/')[-1]
        print(person1,"         ")
        print(persons,"         ")
        print(links,"           ")
        
        person1_id = person1["id"]
        
        link_groups = ImageController.build_link_groups(links)
    
        with open('stored-faces/person_group.json', 'r') as f:
            person_group = json.load(f)
    
        result = {}
    
        for dbemb_name in persons:
            db_emb_name = dbemb_name["path"].split('/')[-1]

            dbemb_id = dbemb_name["id"]
    
            # Step 1: Check if both persons are in the same link group
            for group in link_groups.values():
                if person1_id in group and dbemb_id in group:
                    print("Person1 and db_emb_name are logically linked in group — returning full group.")
                    return {}  # Early return with linked group
                    print("linked_group", list(group))
                 
    
            # Step 2: Check for direct link
            if any(
                (
        (
            ("person1Id" in link and "person2Id" in link and
             ((link["person1Id"] == person1_id and link["person2Id"] == dbemb_id) or
              (link["person1Id"] == dbemb_id and link["person2Id"] == person1_id)))
            or
            ("person1_id" in link and "person2_id" in link and
             ((link["person1_id"] == person1_id and link["person2_id"] == dbemb_id) or
              (link["person1_id"] == dbemb_id and link["person2_id"] == person1_id)))
        )
    )
    for link in links
):
            #   if any(
            #     (link["person1_id"] == person1_id and link["person2_id"] == dbemb_id) or
            #     (link["person1_id"] == dbemb_id and link["person2_id"] == person1_id)
            #     for link in links
            # ):

                print("Person1 and db_emb_name are directly linked — skipping.")
                return {}
    
            # Step 3: Check groupings in person_group JSON
            for key, embeddings in person_group.items():
                # Skip this group if emb_name is the key or in values
                if emb_name == key or emb_name in embeddings:
                    continue
    
                # Skip if both are in same group already
                if (key == emb_name or emb_name in embeddings) and (db_emb_name == key or db_emb_name in embeddings):
                    return {}
    
                if key == db_emb_name:
                    group = set(embeddings + [key])
                    result[key] = list(group)
    
                elif db_emb_name in embeddings:
                    group = set([key] + embeddings)
                    result[key] = list(group)
    
        # Merge overlapping groups before returning
        # Merge groups only if there's a link between them
        result = ImageController.merge_linked_overlapping_groups(result, personrecords, links)
        print("RESULT",result)
        return result


    @staticmethod
    def sync_images():
        images = Image.query.filter(Image.is_sync == False).all()
        syncImage=[]
        for image in images:
                syncImage.append(image.to_dict())
        return jsonify(syncImage)
    
# {
#     "capture_date": "2025-06-17",
#     "event_date": "2025-06-10",
#     "events": [
#         {
#             "id": 2,
#             "name": "Convocation"
#         }
#     ],
#     "hash": "8d97807e7d37bf87273d59ac0d1bbf30790322f5f5ec61c26845c3ae52390cc9",
#     "id": 13,
#     "is_sync": true,
#     "last_modified": "2025-06-18 12:25:23",
#     "location": ["New yORK", "33.1234", "73.5678"],
#     "path": "E:/fyp/uni_images/2020-01-30 20th Convocation-20250418T034555Z-002/2020-01-30 20th Convocation/4-test/DSC_5274.JPG",
#     "persons": [
#         {
#             "age": -1,
#             "dob": "Wed, 18 Jun 2025 00:00:00 GMT",
#             "gender": "M",
#             "id": 38,
#             "name": "Am",
#             "path": "face_images/2ff77cdd91324465bce5d30ca22e4b42.jpg"
#         },
#         {
#             "age": -1,
#             "dob": "Wed, 18 Jun 2025 00:00:00 GMT",
#             "gender": "M",
#             "id": 39,
#             "name": "Al",
#             "path": "face_images/7d7cb89d68414b22a99ec6ddafb75f51.jpg"
#         }
#     ],
#    'links': {
#               'face_images/2ff77cdd91324465bce5d30ca22e4b42.jpg': [], 
#               'face_images/7d7cb89d68414b22a99ec6ddafb75f51.jpg': ['face_images/2ff77cdd91324465bce5d30ca22e4b42.jpg']
#             }
# }

    def save_unsync_image_with_metadata_iqra(data):
        try:
            print("Receive Images ////////////",data)
            for idx, item in enumerate(data):
                print(f"\n🔹 Processing Image {idx + 1}:")

                # image_data_b64 = item.get('image_data')
                capture_date = item.get('capture_date')
                event_date = item.get('event_date','')
                last_modified_str = item.get('last_modified')
                hash_val = item.get('hash','')
                location = item.get('location','')
                events = item.get('events', [])
                persons = item.get('persons', [])
                links = item.get('links', [])
                print("HEEEEEEEEEEEEEEEEEEEEEEEEEELOO",last_modified_str,",",hash_val,capture_date,links)
                print("Locationnnnnnnn", location)
                print("Linkssssssss",links)

                if not hash_val or not last_modified_str:
                    print("❌ Missing hash or last_modified. Skipping...")
                    continue

                # Convert string to date
                # try:
                #     last_modified_date = datetime.strptime(last_modified_str, "%Y-%m-%d").date()
                # except ValueError:
                #     print("❌ Invalid date format. Skipping...")
                #     continue

                    # Try parsing as datetime with time
                if " " in last_modified_str:
                    last_modified_date = datetime.strptime(last_modified_str, "%Y-%m-%d %H:%M:%S")
                    

                

                # Check if image with hash exists
                existing_image = Image.query.filter_by(hash=hash_val).first()
                print(last_modified_str,'🙌--------->',existing_image.last_modified)

                if existing_image:
                    print(f"✅ Image with hash {hash_val} found with ID {existing_image.id}")
                    print("last_MODIFIED ",{last_modified_date}," and", {existing_image.last_modified})

                    if last_modified_date > existing_image.last_modified:
                        #  Extract event names if events are dictionaries
                        event_names = [e['name'] for e in events if isinstance(e, dict) and 'name' in e]
                        # ✅ Convert location dict to list
                        location_list = []
                        if isinstance(location, dict):
                            location_list = [
                                location.get("name"),
                                location.get("latitude"),
                                location.get("longitude")
                            ]

                        # persons_data = []
                        # for person in persons:
                        #     per = Person.query.filter_by(path = person.get('path')).first()
                        
                        persons_data = [
                            {
                                "name": p.get('name'),
                                "path": p.get('path'),
                                "gender": p.get('gender'),
                                "dob": p.get('DOB'),
                                "age": p.get('Age')
                                # "dob": p.get('dob'),
                                # "age": p.get('age')
                                }
                                for p in persons]
                            
                        if persons_data:
                            print("Persons Data.........", persons_data)
                            print("Events Data.........", event_names)
                            print("Location Data.........", location_list)
                            edit_payload = {
                                    str(existing_image.id): {
                                    "persons_id": persons_data,
                                    "event_names": event_names,
                                    "event_date": event_date,
                                    "location": location_list
                                    }
                                }
                        else:
                            edit_payload = {
                                    str(existing_image.id): {
                                    "event_names": event_names,
                                    "event_date": event_date,
                                    "location": location_list
                                    }
                                }
                            
                        print("EditPayload/////// ////",edit_payload)  
                        ImageController.create_links_if_not_exist(links)
                        ImageController.edit_image_data_for_sync_iqra(edit_payload)

                        existing_image.is_sync = True
                        print('👌-----------------------------------------saving--------')
                        db.session.commit()

            return jsonify({'status': 'success', 'message': 'All images processed successfully'}), 200

        except Exception as e:
                print(f"❌ Error: {e}")
                return jsonify({'error': str(e)}), 500



    def save_unsync_image_with_metadata(data):
        try:
         print("Receive Unsync",data)
         for idx, item in enumerate(data):
            print(f"\n🔹 Processing Image {idx + 1}:")

            # image_data_b64 = item.get('image_data')
            capture_date = item.get('capture_date')
            event_date = item.get('event_date','')
            last_modified_str = item.get('last_modified')
            hash_val = item.get('hash','')
            location = item.get('location','')
            events = item.get('events', [])
            persons = item.get('persons', [])
            links = item.get('links', {})
            print("HHHHHHHHHHHHHEEEEEEEELOOOOOO",last_modified_str,",",hash_val,capture_date,links)

            if not hash_val or not last_modified_str:
                print("❌ Missing hash or last_modified. Skipping...")
                continue

            # Convert string to date
            # try:
            #     last_modified_date = datetime.strptime(last_modified_str, "%Y-%m-%d").date()
            # except ValueError:
            #     print("❌ Invalid date format. Skipping...")
            #     continue

                # Try parsing as datetime with time
            if " " in last_modified_str:
                last_modified_date = datetime.strptime(last_modified_str, "%Y-%m-%d %H:%M:%S")
                

            

            # Check if image with hash exists
            existing_image = Image.query.filter_by(hash=hash_val).first()
            print(last_modified_str,'🙌--------->',existing_image.last_modified)

            if existing_image:
                print(f"✅ Image with hash {hash_val} found with ID {existing_image.id}")
                print("last_MODIFIED ",{last_modified_date}," and", {existing_image.last_modified})

                if last_modified_date > existing_image.last_modified:

                    print("✅ last_modified_1 is more recent")

                    # persons_data = []
                    # for person in persons:
                    #     per = Person.query.filter_by(path = person.get('path')).first()

                    # Extract event names if events are dictionaries
                    event_names = [e['name'] for e in events if isinstance(e, dict) and 'name' in e]

                
                    persons_data = [
                        {
                            "name": p.get('name'),
                            "path": p.get('path'),
                            "gender": p.get('gender'),
                    
                            "dob": p.get('dob'),
                            "age": p.get('age')
                            }
                            for p in persons]
                        
                    if persons_data:
                        print("Persons Data/////////////////////////", persons_data)
                        edit_payload = {
                                str(existing_image.id): {
                                "persons_id": persons_data,
                                "event_names": event_names,
                                "event_date": event_date,
                                "location": location
                                }
                            }
                        print("Before check links")
                        ImageController.create_links_if_not_exist(links)
                        print("After check links")
                        ImageController.edit_image_data(edit_payload)
                        existing_image.is_sync = True
                        print('👌-----------------------------------------saving--------')
                        db.session.commit()
                    else:
                        edit_payload = {
                                str(existing_image.id): {
                                "event_names": event_names,
                                "event_date": event_date,
                                "location": location
                                }
                            }
                        print("Before check links")
                        ImageController.create_links_if_not_exist(links)
                        print("After check links")
                        print("Event NAMES", event_names, "AND LOCATION",location)

                        ImageController.edit_image_data(edit_payload)
                        existing_image.is_sync = True
                        print('👌-----------------------------------------saving--------')
                        db.session.commit()

         return jsonify({'status': 'success', 'message': 'All images processed successfully'}), 200

        except Exception as e:
            print(f"❌ Error: {e}")
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def create_links_if_not_exist(links):
     for path1, related_paths in links.items():
        # print(f"🧠 Looking for person by path: {path1} and {path2}")
        # Get person1 object from path
        person1 = Person.query.filter_by(path=path1).first()

        if not person1:
            print(f"❌ Person not found for path: {path1}")
            continue

        for path2 in related_paths:
            # Get person2 object from path
            person2 = Person.query.filter_by(path=path2).first()
            if not person2:
                print(f"❌ Person not found for path: {path2}")
                continue

            # Check if link already exists (in either direction)
            existing_link = Link.query.filter(
                ((Link.person1_id == person1.id) & (Link.person2_id == person2.id)) |
                ((Link.person1_id == person2.id) & (Link.person2_id == person1.id))
            ).first()

            if existing_link:
                print(f"🔗 Link already exists between {person1.name} and {person2.name}")
                continue

            # If not, create a new Link
            new_link = Link(person1_id=person1.id, person2_id=person2.id)
            db.session.add(new_link)
            print(f"✅ Link created between {person1.name} and {person2.name}")

     db.session.commit()
     print("🎉 All links processed and committed.")

    
    @staticmethod
    def get_emb_names_for_recognition(persons, links, emb_name):
        # print('person list:', persons)
        # print('links:', links)
        # print('emb name:', emb_name)
    
        # Load the JSON file
        with open('stored-faces/person_group.json') as f:
            emb_data = json.load(f)
    
        # Helper: Get all groups (key and value matches)
        def get_related_groups(target_emb):
            related = set()
            for key, values in emb_data.items():
                if target_emb == key or target_emb in values:
                    related.add(key)
                    related.update(values)
            return related
    
        collected_embs = set()
    
        # Step 1: Collect all groups where emb_name is key or in values
        collected_embs.update(get_related_groups(emb_name))
    
        # Step 2: Check if emb_name is in person path
        emb_path_check = f'face_images/{emb_name}'
        person_id = None
        for person in persons:
            if emb_path_check in person["path"]:
                person_id = person["id"]
                break
    
        if person_id:
            # Step 3: Find linked person IDs
            linked_ids = set()
            for link in links:
                # Dynamically get the correct keysAdd commentMore actions
                if "person1Id" in link and "person2Id" in link:
                    a, b = link["person1Id"], link["person2Id"]
                elif "person1_id" in link and "person2_id" in link:
                    a, b = link["person1_id"], link["person2_id"]
                else:
                    continue  # Skip malformed entries
            
                if person_id in (a, b):
                    linked_ids.add(a)
                    linked_ids.add(b)
            linked_ids.discard(person_id)
    
            # Step 4: For each linked ID, get embedding name and related groups
            for pid in linked_ids:
                for person in persons:
                    if person["id"] == pid:
                        path_parts = person["path"].split('/')
                        if len(path_parts) > 1:
                            linked_emb = path_parts[1]
                            collected_embs.update(get_related_groups(linked_emb))
        print(list(collected_embs))
        return jsonify({"embeddings": list(collected_embs)})



    @staticmethod
    def get_persons(person1,name):
        
        samenamedpersons=Person.query.filter_by(name=name).all()
        samenamedpersons_list = [
            {"id": p.id, "name": p.name, "path": p.path}
            for p in samenamedpersons
            ]
        persons_db = Person.query.all()
        person_list = [
               {"id": p.id, "name": p.name, "path": p.path}
               for p in persons_db
                ]
        links = Link.query.all()
            
        link_list = [
                {"person1_id": link.person1_id, "person2_id": link.person2_id}
                for link in links
            ] 
        # print("samenamedpersons",samenamedpersons_list)
        # print("link_list",link_list)
        # print("person1",person1)
        # print("person_list",person_list)   
        result=ImageController.get_emb_names(samenamedpersons_list, link_list, person1,person_list) 
        print(result)
        return result or {} 
    
    @staticmethod
    def build_person_links(person_records, link_records):
        # Step 1: Create a mapping from person_id to image path
        id_to_path = {person["id"]: person["path"] for person in person_records}
    
        # Step 2: Initialize result dict with empty lists
        links = {path: [] for path in id_to_path.values()}
    
        # Step 3: Fill in the links based on link_records
        for link in link_records:
            p1_id = link.get("person1_id")
            p2_id = link.get("person2_id")
    
            p1_path = id_to_path.get(p1_id)
            p2_path = id_to_path.get(p2_id)
    
            if p1_path and p2_path:
                # Add links in one direction or both as needed
                links[p2_path].append(p1_path)
                # If you want bidirectional links, uncomment this:
                # links[p1_path].append(p2_path)
    
        return {"links": links}
                   