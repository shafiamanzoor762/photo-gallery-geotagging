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
            event_image_dict = {}
    
            # Fetch all events
            events = Event.query.all()
    
            for event in events:
                event_id = event.id
    
                # Fetch all image-event mappings for this event
                image_events = ImageEvent.query.filter_by(event_id=event_id).all()
    
                # Extract image IDs from the mappings
                image_ids = [image_event.image_id for image_event in image_events]
    
                # Print for debugging
                print(f"Image IDs for event '{event.name}': {image_ids}")
    
                # Fetch images, ensuring only non-deleted ones are included
                image_data = []
                for image_id in image_ids:
                    image = Image.query.filter_by(id=image_id, is_deleted=False).first()  # Exclude deleted images
                    if image:
                        image_data.append({
                            "image_id": image.id,
                            "path": image.path,
                            "is_sync": image.is_sync,
                            "capture_date": image.capture_date,
                            "event_date": image.event_date,
                            "last_modified": image.last_modified,
                            "location_id": image.location_id
                        })
    
                event_image_dict[event.name] = image_data
    
            return {"message": event_image_dict}, 201
    
        except Exception as e:
            return {"error": str(e)}, 500
        
    
    
    