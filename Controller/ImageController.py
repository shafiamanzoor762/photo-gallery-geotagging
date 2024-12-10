from flask import jsonify
from sqlalchemy import func
from collections import defaultdict

from Model.Image import Image
from Model.Location import Location
from Model.Event import Event
from Model.ImageEvent import ImageEvent
from datetime import datetime

from config import db

class ImageController:

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
                grouped_images[image.captureDate].append({
                    'id': image.id,
                    'path': image.path,
                    'is_sync': image.isSync,
                    'capture_date': image.captureDate,
                    'event_date': image.eventDate,
                    'last_modified': image.lastModified,
                    'location_id': image.location_id
                })

            # Prepare the response in the desired format
            response = {str(i + 1): records for i, records in enumerate(grouped_images.values())}
            return jsonify(response), 200
        
        except Exception as e:
            # Catch any exceptions and return an error response
            return jsonify({"error": str(e)}), 500







    @staticmethod
    def group_by_location():
        try:
            # Query to join Image and Location without JSON functions
            results = (
                db.session.query(
                    Location.id,
                    Location.name,
                    Location.latitude,
                    Location.longitude,
                    Image.id,
                    Image.path,
                    Image.isSync,
                    Image.captureDate,
                    Image.eventDate,
                    Image.lastModified,
                    Image.location_id
                )
                .join(Image, Image.location_id == Location.id)
                .all()
            )

            # Grouping data in Python
            grouped_data = {}
            for row in results:
                location_id = row[0]
                location_name = row[1]
                latitude = row[2]
                longitude = row[3]

                # Initialize the location entry if it doesn't exist
                if location_name not in grouped_data:
                    grouped_data[location_name] = {
                        'latitude': float(latitude) if latitude else None,
                        'longitude': float(longitude) if longitude else None,
                        'images': []
                    }

                # Append image data to the 'images' list for this location
                grouped_data[location_name]['images'].append({
                    'id': row[4],
                    'path': row[5],
                    'isSync': row[6],
                    'captureDate': row[7],
                    'eventDate': row[8],
                    'lastModified': row[9],
                    'location_id': row[10]
                })

            # Return the response as JSON
            return jsonify(grouped_data), 200

        except Exception as e:
            # Catch any exceptions and return an error response
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def add_image(data):
        try:
            image = Image(
            path=data['path'],
            isSync=data['isSync'],
            captureDate=data.get('captureDate', None),
            eventDate=data.get('eventDate', None),
            lastModified=datetime.utcnow())
            db.session.add(image)
            db.session.commit()

            return jsonify({
            'id': image.id,
            'path': image.path,
            'isSync': image.isSync,
            'captureDate': image.captureDate,
            'eventDate': image.eventDate,
            'lastModified': image.lastModified
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def edit_image(image_id, data):
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        image.path = data.get('path', image.path)
        image.isSync = data.get('isSync', image.isSync)
        image.captureDate = data.get('captureDate', image.captureDate)
        image.eventDate = data.get('eventDate', image.eventDate)
        image.lastModified = datetime.utcnow()
        
        try:
            db.session.commit()
            return jsonify({
            'id': image.id,
            'path': image.path,
            'isSync': image.isSync,
            'captureDate': image.captureDate,
            'eventDate': image.eventDate,
            'lastModified': image.lastModified
        }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def get_image_details(image_id):
            image = Image.query.get(image_id)
            
            if not image:
                return jsonify({'error': 'Image not found'}), 404
            
            return jsonify({
                'id': image.id,
                'path': image.path,
                'isSync': image.isSync,
                'captureDate': image.captureDate,
                'eventDate': image.eventDate,
                'lastModified': image.lastModified
                })
    
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


#---------------------------STUFF FOR EVENT CONTROLLER------------------------------
    @staticmethod
    def fetch_all_events():
        events = Event.query.all()
        return [{
        'event_id':e.id,
        'name': e.name} for e in events]
    
    @staticmethod
    def addnewevent(json_data):
        try:
            # Extract the data from the JSON
            name = json_data.get('name')
            print(name)
            existing_event = Event.query.filter_by(name=name).first()

            if existing_event:
               # If the event already exists, return a message
                return {"message": "Event with this name already exists."}, 400

            # Create a new Image instance
            new_event = Event( 
                name=name, 
            )
            
            # Add and commit to the database
            db.session.add(new_event)
           
            db.session.commit()

            return {"message":new_event.name}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        

    @staticmethod
    def addevents(json_data):
        events_data=[]
        try:
            # Extract the data from the JSON
            id = json_data.get('id')
            print(id)
            existing_id= Image.query.filter_by(id=id).first()
            print(existing_id)
            if existing_id:
                name = json_data.get('names')
                names=name.split(',')
                for n in names:
                   existing_event = Event.query.filter_by(name=n).first()  # Search for the event with the name equal to 'n'
    
                   if existing_event:
                    # If an event with that name exists, retrieve its id
                     event_id = existing_event.id
                     print(f"Event ID for {n}: {event_id}")
                     add_events = ImageEvent(
                         image_id=existing_id.id,
                         event_id=event_id,
               
                          )
                      # Add and commit to the database
                     db.session.add(add_events)
           
                     db.session.commit()
                   else:
                    # If no event is found, you can handle the case here
                     print(f"No event found with the name: {n}")
                   
                
                events_data.append({
                            'id': existing_id.id,
                            'name': event_id,
                            
                        })
            else:
                return {"message":"No ID Found"}, 201
            
           

            #creating problem
            return {"message":ImageEvent.image_id, "events":events_data}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        
    @staticmethod
    def sortevents(json_data):
        try:
            # Extract the data from the JSON
            name = json_data.get('name')
            event_image_dict = {}
            # print(name)
            events = Event.query.all()
            for event in events:
              event_id = event.id
            #   print(f"Event Name: {event.name}, Event ID: {event.id}")
            # Query Image_Event table to get all image_ids for the given event_id
              image_events = ImageEvent.query.filter_by(event_id=event_id).all()

              # Create a list of image_ids corresponding to the event_id
              image_ids = [image_event.image_id for image_event in image_events]

                # Print the list of image_ids
              print(f"Image IDs for event '{event.name}': {image_ids}")
              event_image_dict[event.name] = image_ids

            return {"message":event_image_dict}, 201

        except Exception as e:
            
            return {"error": str(e)}, 500