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
        

#   image correspondence add events
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
            return {"message":"Done"}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        
    @staticmethod
    def sortevents():
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