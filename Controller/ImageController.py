from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from collections import defaultdict

from Controller.LocationController import LocationController
from Model.Person import Person
from Model.Image import Image
from Model.Location import Location
from Model.Event import Event
from Model.ImageEvent import ImageEvent
from Model.ImagePerson import ImagePerson
from datetime import datetime
from sqlalchemy.orm import joinedload

from config import db

class ImageController:


# {
#   "2": {
#     "persons_id": [
#       {"id": 1, "name": "Ali","gender": "M"},
#       {"id": 2, "name": "Amna","gender": "F"}
#     ],
#     "event_name": "iNDEPENDENCE DAY",
#     "event_date": "2025-01-17",
#     "location": ["New yORK", "33.1234", "73.5678"]
#   }
# }

    # @staticmethod
    # def edit_image_data():
    #     data = request.get_json()  

    #     if not data:
    #         return jsonify({"error": "No data provided"}), 400

    #     if len(data) != 1:
    #         return jsonify({"error": "Invalid data format. Expecting a single numeric image_id as the key."}), 400

    #     try:
    #         image_id = int(next(iter(data.keys())))  
    #     except ValueError:
    #         return jsonify({"error": "image_id must be a numeric value"}), 400

    #     image_data = data.get(str(image_id))  
    #     if not image_data:
    #         return jsonify({"error": "image_id data is required"}), 400

       
    #     persons = image_data.get('persons_id')  
    #     event_name = image_data.get('event_name')
    #     event_date = image_data.get('event_date')
    #     locations = image_data.get('location')

        
    #     image = Image.query.filter(Image.id == image_id).first()
    #     print(image)
    #     if not image:
    #         return jsonify({"error": "Image not found"}), 404

        
    #     if event_date:
    #         image.event_date = event_date
    #     if event_name:
            
    #         for event in image.events:
    #             event.name = event_name

       
    #     if locations:
    #         loc_id = image.location_id
    #         if not loc_id:
    #             return jsonify({"error": "No location associated with this image"}), 404

    #         location =  Location.query.filter(Location.id == loc_id).first()
    #         if location:
    #             location.name = locations[0] if len(locations) > 0 else location.name
    #             location.latitude = locations[2] if len(locations) > 2 else location.latitude
    #             location.longitude = locations[3] if len(locations) > 3 else location.longitude
    #         else:
    #             return jsonify({"error": "Location record not found"}), 404

        
    #     if persons:
    #         for person_data in persons:
    #             person_id = person_data.get('id')
    #             person_name = person_data.get('name')
    #             gender = person_data.get('gender')
    #             if person_id:
    #                 person = Person.query.filter(Person.id == person_id).first()
    #                 if person:
    #                     if person_name and gender:
    #                         person.name = person_name
    #                         person.gender  =gender
    #                     else:
    #                         return jsonify({"error": f"Name is required for person with id {person_id}"}), 400
    #                 else:
    #                     return jsonify({"error": f"Person with id {person_id} not found"}), 404
    #             else:
    #                 return jsonify({"error": "Person id is required"}), 400

    #     try:
    #         db.session.commit()
    #         return jsonify({"message": "Image, location, and persons updated successfully"}), 200
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({"error": f"An error occurred: {str(e)}"}), 500


    # =================================


    @staticmethod
    def edit_image_data():
        data = request.get_json()  # Get JSON data from the request

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Ensure that the input data has exactly one key (the image_id)
        if len(data) != 1:
            return jsonify({"error": "Invalid data format. Expecting a single numeric image_id as the key."}), 400

        # Extract the numeric image_id and its associated data
        try:
            image_id = int(next(iter(data.keys())))  
        except ValueError:
            return jsonify({"error": "image_id must be a numeric value"}), 400

        image_data = data.get(str(image_id))  # Get the data associated with the numeric image_id
        if not image_data:
            return jsonify({"error": "image_id data is required"}), 400

        # Extract necessary fields
        persons = image_data.get('persons_id')  # Corrected key name to 'persons_id'
        event_names = image_data.get('event_names')
        event_date = image_data.get('event_date')
        locations = image_data.get('location')

        # Fetch the image record by image_id
        image = Image.query.filter(Image.id == image_id).first()
        print(image)
        if not image:
            return jsonify({"error": "Image not found"}), 404

        # Update event_date and event_name if provided
        if event_date:
            image.event_date = event_date

        if event_names:
            image.events = []  # Clears the relationship in the ORM
            db.session.commit()
            # Access the related events
            # for event in image.events:
            #     event = Event.query.filter_by(id=event.id).first()
            #     event.name = event_name
            events = Event.query.filter(Event.name.in_(event_names)).all()
            if not events:
                return {"error": "No matching events found"}, 404

            # Associate image with events
            for event in events:
                if event not in image.events:
                    image.events.append(event)

        # Update location if provided
        if locations:
            if not image.location_id:
                return jsonify({"error": "No location associated with this image"}), 404

            location = Location.query.filter_by(id=image.location_id).first()
            if location:
                location.name = locations[0] if len(locations) > 0 else location.name
                location.latitude = locations[2] if len(locations) > 2 else location.latitude
                location.longitude = locations[3] if len(locations) > 3 else location.longitude
            else:
                return jsonify({"error": "Location record not found"}), 404

        # Update persons if provided
        if persons:
            for person_data in persons:
                person_id = person_data.get('id')
                person_name = person_data.get('name')
                gender = person_data.get('gender')
                if person_id:
                    person = Person.query.filter(Person.id == person_id).first()
                    if person:
                        if person_name and gender:
                            person.name = person_name
                            person.gender  =gender
                        else:
                            return jsonify({"error": f"Name is required for person with id {person_id}"}), 400
                    else:
                        return jsonify({"error": f"Person with id {person_id} not found"}), 404
                else:
                    return jsonify({"error": "Person id is required"}), 400

        # Save changes to the database
        try:
            db.session.commit()
            return jsonify({"message": "Image, events, location, and persons updated successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500


       
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
    @staticmethod
    def searching_on_image(): 
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract parameters
        person_names = data.get('name', [])  
        gender = data.get('gender', [])  # Now a list
        events = data.get('events', [])
        capture_dates = data.get('capture_date', [])
        locations = data.get('location', {})

        person_ids = []
        image_ids = []

        # Search for persons
        if person_names:
            for name in person_names:
                query = Person.query.filter(Person.name == name)

                # If gender is provided and is a list, filter by it
                if gender:
                    query = query.filter(Person.gender.in_(gender))  # ✅ FIXED

                persons = query.all()

                for person in persons:
                    if person:  
                        person_ids.append(person.id)  

        # Search for images linked to persons
        if person_ids:
            images = (
                db.session.query(Image.id)  # Select the id column from the Image table
                .join(ImagePerson, ImagePerson.image_id == Image.id)  # Join ImagePerson with Image
                .join(Person, Person.id == ImagePerson.person_id)  # Join Person with ImagePerson
                .filter(ImagePerson.person_id.in_(person_ids))  # Filter by the list of person_ids
                .all()
            )

            for image in images:
                image_ids.append(image.id)

        # Search for images linked to events
        event_ids = []
        if events:
            for event_name in events:
                event = Event.query.filter(Event.name == event_name).first()
                if event:
                    event_ids.append(event.id)

            if event_ids:
                images_of_events = (
                    db.session.query(Image.id)
                    .join(ImageEvent, ImageEvent.image_id == Image.id)
                    .join(Event, Event.id == ImageEvent.event_id)
                    .filter(ImageEvent.event_id.in_(event_ids))
                    .all()
                )

                for image in images_of_events:
                    image_ids.append(image.id)

        # Search for images by capture date
        if capture_dates:
            for date in capture_dates:
                image_dates = Image.query.filter(Image.capture_date == date).all()
                for image in image_dates:
                    image_ids.append(image.id)

        # Search for images by location
        if locations:
            latitude = locations.get('latitude')
            longitude = locations.get('longitude')
            if latitude and longitude:
                loc_name = LocationController.get_location_from_lat_lon(latitude, longitude)

                if loc_name:
                    location = Location.query.filter(Location.name == loc_name).first()
                    if location:
                        images_at_location = Image.query.filter(Image.location_id == location.id).all()
                        for image in images_at_location:
                            image_ids.append(image.id)

        # Retrieve final image paths
        image_paths = []
        if image_ids:
            images = Image.query.filter(Image.id.in_(image_ids)).all()
            for image in images:
                if image:  
                    image_paths.append(image.path)

        return jsonify({"paths": image_paths}), 200  

    # def searching_on_image():
    #     data = request.get_json()

    #     if not data:
    #         return jsonify({"error": "No data provided"}), 400

       
    #     person_names = data.get('name', [])  
    #     gender = data.get('gender')
    #     events = data.get('events', [])
    #     capture_dates = data.get('capture_date', [])
    #     locations = data.get('location', {})

       
    #     person_ids = []
    #     image_ids = []

       
    #     if person_names:
    #         for name in person_names:
    #             persons = Person.query.filter(
    #                 Person.name == name,
    #                 Person.gender == gender if gender else True  
    #             ).all()  
    #             for person in persons:
    #                 if person:  
    #                     person_ids.append(person.id)  

        
    #     if person_ids:
    #         images = (
    #             db.session.query(Image.id) 
    #             .join(ImagePerson, ImagePerson.image_id == Image.id)  
    #             .join(Person, Person.id == ImagePerson.person_id)  
    #             .filter(ImagePerson.person_id.in_(person_ids))  
    #             .all()
    #         )

            
    #         for image in images:
    #             image_ids.append(image.id)

        
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

       
    #     if capture_dates:
    #         for date in capture_dates:
    #             image_dates = Image.query.filter(Image.capture_date == date).all()
    #             for image in image_dates:
    #                 image_ids.append(image.id)

       
    #     if locations:
    #         latitude = locations.get('latitude')
    #         longitude = locations.get('longitude')
    #         if latitude and longitude:
    #             loc_name = LocationController.get_location_from_lat_lon(latitude, longitude)

    #             if loc_name:
    #                 location = Location.query.filter(Location.name == loc_name).first()
    #                 if location:
    #                     images_at_location = Image.query.filter(Image.location_id == location.id).all()
    #                     for image in images_at_location:
    #                         image_ids.append(image.id)

        
    #     image_paths = []
    #     if image_ids:
    #         images = Image.query.filter(Image.id.in_(image_ids)).all()
    #         for image in images:
    #             if image:  
    #                 image_paths.append(image.path)

    #     return jsonify({"paths": image_paths}), 200
    
    #  ===================================

    @staticmethod
    def add_image(data):
        try:
            
            image = Image(
            path=data['path'],
            is_sync=data.get('is_sync',0),
            capture_date=data.get('capture_date', datetime.utcnow()),
            event_date=data.get('event_date', None),
            last_modified=datetime.utcnow())
            print(image)
            db.session.add(image)
            db.session.commit()
            print(image)
            return jsonify(image.to_dict()), 201
        except Exception as e:
            db.session.rollback()
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

        persons = [
        {"id": person.id, "name": person.name, "path": person.path, "gender": person.gender}
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
        "location": location_data,
        "persons": persons,
        "events": events
        }
    
        return jsonify(image_data)

    @staticmethod
    def delete_image(image_id):
            image = Image.query.get(image_id)
            if not image:
                return jsonify({'error': 'Image not found'}), 404
            
            try:
                db.session.delete(image)
                db.session.commit()
                return jsonify({'message': 'Image deleted successfully'}), 200
            except Exception as e:
                db.session.rollback()
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
    def sync_images():
        images = Image.query.filter(Image.is_sync == False).all()
        syncImage=[]
        for image in images:
                syncImage.append(image.to_dict())
        return jsonify(syncImage)
        
    @staticmethod
    def Load_images():
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Fetch the filtering criteria
        person_id = data.get("person_id")  # Expecting a single value, not a list
        event_name = data.get("event")  # Expecting a single event name
        capture_date = data.get("capture_date")  # Expecting a single date
        location_name = data.get("location")  # Expecting a single location name
        
        image_ids = set()  # Using set to avoid duplicates
    
        # 🔹 Filter by Person ID
        if person_id:
            person = Person.query.filter_by(id=person_id).first()
            if person:
                person_images = (
                    db.session.query(Image.id)
                    .join(ImagePerson, ImagePerson.image_id == Image.id)
                    .filter(ImagePerson.person_id == person_id)
                    .all()
                )
                image_ids.update([image.id for image in person_images])
    
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

       
            
        
        
         
        
    
    # getting unlabel images
    def get_unedited_images():
        try:
            unedited_images = (
                db.session.query(Image)
                .outerjoin(Image.persons)  # Join with Person table
                .outerjoin(Image.events)  # Join with Event table
                .filter(
                    (Image.is_deleted == False) &  # Exclude deleted images
                    (Image.event_date.is_(None)) &  # No event date
                    (Image.location_id.is_(None)) &  # No location
                    ((Person.name == "unknown") | (Person.name.is_(None))) &  # Person's name is "unknown" or NULL
                    (Person.gender.is_(None)) &  # Person's gender is NULL
                    ((Event.name == "unknown") | (Event.name.is_(None)))  # Event name is "unknown" or NULL
                )
                .all()
            )
    
            # Convert images to JSON format
            image_list = []
            for img in unedited_images:
                location = img.location if img.location else None
                image_list.append({
                    "id": img.id,
                    "path": img.path,
                    "is_sync": img.is_sync,
                    "capture_date": img.capture_date.strftime('%Y-%m-%d') if img.capture_date else None,
                    "event_date": img.event_date.strftime('%Y-%m-%d') if img.event_date else None,
                    "last_modified": img.last_modified.strftime('%Y-%m-%d %H:%M:%S') if img.last_modified else None,
                    "location": {
                        "id": location.id if location else None,
                        "name": location.name if location else None,
                        "latitude": location.latitude if location else None,
                        "longitude": location.longitude if location else None,
                    },
                    "persons": [{"id": p.id, "name": p.name, "gender": p.gender} for p in img.persons],  # Include person details
                    "events": [{"id": e.id, "name": e.name} for e in img.events]  # Include event details
                })
    
            print(image_list)
            return jsonify({"unedited_images": image_list}), 200
    
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    
    def get_all_person():
        persons = (
            db.session.query(Person.id, Person.name, Person.path, Person.gender)
            .all()
            )    
    
    # Convert result to list of dictionaries
        return [{"id": p.id, "name": p.name, "path": p.path, "gender": p.gender} for p in persons]

    



