from Model.Event import Event
from Model.Image import Image
from Model.ImageEvent import ImageEvent
from config import db

class EventController():
    
    @staticmethod
    def fetch_all_events():
        events = Event.query.all()
        return [{
        'Id':e.id,
        'Name': e.name} for e in events]
    
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
    def groupbyevents():
        try:
            # Extract the data from the JSON
            
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
              image_data = []
              for image_id in image_ids:
        # Query Image table to get detailed info about each image
                 image = Image.query.get(image_id)  # Adjust query as needed for your model
                 if image:
            # Collect any data you need for each image, e.g., name, file path, etc.
                     image_data.append({
                "image_id": image.id,
                "path": image.path,
                "is_sync": image.is_sync,  
                "capture_date":image.capture_date,
                "event_date":image.event_date,
                "last_modified":image.last_modified,
                "location_id":image.location_id


            })
              event_image_dict[event.name] = image_data

            return {"message":event_image_dict}, 201

        except Exception as e:
            
            return {"error": str(e)}, 500
        


