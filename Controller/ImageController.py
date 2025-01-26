from flask import jsonify, request
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
            image_id = int(next(iter(data.keys())))  # Get the first key and convert it to an integer
        except ValueError:
            return jsonify({"error": "image_id must be a numeric value"}), 400

        image_data = data.get(str(image_id))  # Get the data associated with the numeric image_id
        if not image_data:
            return jsonify({"error": "image_id data is required"}), 400

        # Extract necessary fields
        persons = image_data.get('persons_id')  # Corrected key name to 'persons_id'
        event_name = image_data.get('event_name')
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
        if event_name:
            # Access the related events
            for event in image.events:
                event.name = event_name

        # Update location if provided
        if locations:
            loc_id = image.location_id
            if not loc_id:
                return jsonify({"error": "No location associated with this image"}), 404

            location =  Location.query.filter(Location.id == loc_id).first()
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
            return jsonify({"message": "Image, location, and persons updated successfully"}), 200
        except Exception as e:
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


    @staticmethod
    def searching_on_image():
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract necessary fields
        person_names = data.get('name', [])  # Corrected key name to 'persons_id'
        gender = data.get('gender')
        events = data.get('events', [])
        capture_dates = data.get('capture_date', [])
        locations = data.get('location', {})

        # Initialize lists to store person_ids and image paths
        person_ids = []
        image_ids = []

        # Fetch person_ids for all person_names
        if person_names:
            for name in person_names:
                persons = Person.query.filter(
                    Person.name == name,
                    Person.gender == gender if gender else True  # Only filter gender if provided
                ).all()  # Fetch matching persons
                for person in persons:
                    if person:  # Ensure the person record exists
                        person_ids.append(person.id)  # Add the person's ID to the list

        # Fetch image paths associated with person_ids using JOIN
        if person_ids:
            images = (
                db.session.query(Image.id)  # Select the id column from the Image table
                .join(ImagePerson, ImagePerson.image_id == Image.id)  # Join ImagePerson with Image
                .join(Person, Person.id == ImagePerson.person_id)  # Join Person with ImagePerson
                .filter(ImagePerson.person_id.in_(person_ids))  # Filter by the list of person_ids
                .all()
            )

            # Extract image ids from the query result
            for image in images:
                image_ids.append(image.id)

        # Get the ids of images based on events (Multiple or One Event)
        event_ids = []
        if events:
            for event_name in events:
                event = Event.query.filter(Event.name == event_name).first()  # Fetch the first matching event
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

        # Get the ids of images based on capture dates
        if capture_dates:
            for date in capture_dates:
                image_dates = Image.query.filter(Image.capture_date == date).all()
                for image in image_dates:
                    image_ids.append(image.id)

        # Get the ids of images based on location
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

        # Fetch image paths for the collected image_ids
        image_paths = []
        if image_ids:
            images = Image.query.filter(Image.id.in_(image_ids)).all()
            for image in images:
                if image:  # Ensure the image record exists
                    image_paths.append(image.path)

        return jsonify({"paths": image_paths}), 200

            





                





    #  ===================================
    
    # @staticmethod
    # def group_by_date():
    #     try:
    #         # Query all images from the database
    #         images = Image.query.all()

    #         # Check if any images were returned
    #         if not images:
    #             return jsonify({"message": "No images found"}), 200

    #         # Group images by capture_date
    #         grouped_images = defaultdict(list)
    #         for image in images:
    #             grouped_images[image.captureDate].append({
    #                 'id': image.id,
    #                 'path': image.path,
    #                 'is_sync': image.is_sync,
    #                 'capture_date': image.capture_date,
    #                 'event_date': image.event_date,
    #                 'last_modified': image.last_modified,
    #                 'location_id': image.location_id
    #             })

    #         # Prepare the response in the desired format
    #         response = {str(i + 1): records for i, records in enumerate(grouped_images.values())}
    #         return jsonify(response), 200
        
    #     except Exception as e:
    #         # Catch any exceptions and return an error response
    #         return jsonify({"error": str(e)}), 500


    @staticmethod
    def add_image(data):
        try:
            image = Image(
            path=data['path'],
            is_sync=data.get('is_sync',0),
            capture_date=data.get('capture_date', datetime.utcnow()),
            event_date=data.get('event_date', None),
            last_modified=datetime.utcnow())
            db.session.add(image)
            db.session.commit()

            return jsonify(image.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def edit_image(image_id, data):
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        image.path = data.get('path', image.path)
        image.is_sync = data.get('isSync', image.is_sync)
        image.capture_date = data.get('captureDate', image.capture_date)
        image.event_date = data.get('eventDate', image.event_date)
        image.last_modified = datetime.utcnow()
        
        try:
            db.session.commit()
            return jsonify(image.to_dict()
        #         {
        #     'id': image.id,
        #     'path': image.path,
        #     'isSync': image.isSync,
        #     'captureDate': image.captureDate,
        #     'eventDate': image.eventDate,
        #     'lastModified': image.lastModified
        # }
        ), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def get_image_details(image_id):
            image = Image.query.get(image_id)
            
            if not image:
                return jsonify({'error': 'Image not found'}), 404
            
            return jsonify(image.to_dict()
                # {
                # 'id': image.id,
                # 'path': image.path,
                # 'isSync': image.isSync,
                # 'captureDate': image.captureDate,
                # 'eventDate': image.eventDate,
                # 'lastModified': image.lastModified
                # }
                )
    
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
            

    # Group images by capture_date
    @staticmethod
    def group_by_date():
        try:
            # Query all images from the database
            images = Image.query.all()

            # Check if any images were returned
            if not images:
                return jsonify({"message": "No images found"}), 200

            # Group images by capture_date
            grouped_images = defaultdict(list)
            for image in images:
                grouped_images[image.capture_date].append(image.to_dict())

            # Prepare the response in the desired format
            response = {str(i + 1): records for i, records in enumerate(grouped_images.values())}
            return jsonify(response), 200
        
        except Exception as e:
            # Catch any exceptions and return an error response
            return jsonify({"error": str(e)}), 500
            
