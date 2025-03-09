from Model.Event import Event
from Model.Image import Image
from Model.ImageEvent import ImageEvent
from config import db

class EventController():
    
    @staticmethod
    def fetch_all_events():
        events = Event.query.all()
        return [{
        'event_id':e.id,
        'name': e.name} for e in events]
    
    @staticmethod
    def addnewevent(json_data):
        try:
            
            name = json_data.get('Name')
            print(name)
            existing_event = Event.query.filter_by(name=name).first()

            if existing_event:
               
                return {"message": "Event with this name already exists."}, 400

           
            new_event = Event( 
                name=name, 
            )
            
           
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
           
            id = json_data.get('id')
            print(id)
            existing_id= Image.query.filter_by(id=id).first()
            print(existing_id)
            if existing_id:
                name = json_data.get('names')
                names=name.split(',')
                for n in names:
                   existing_event = Event.query.filter_by(name=n).first()  
    
                   if existing_event:
                    
                     event_id = existing_event.id
                     print(f"Event ID for {n}: {event_id}")
                     add_events = ImageEvent(
                         image_id=existing_id.id,
                         event_id=event_id,
               
                          )
                      
                     db.session.add(add_events)
           
                     db.session.commit()
                   else:
                   
                     print(f"No event found with the name: {n}")
                   
                
                events_data.append({
                            'id': existing_id.id,
                            'name': event_id,
                            
                        })
            else:
                return {"message":"No ID Found"}, 201
            
           
            
            return {"message":"Done"}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @staticmethod
    def groupbyevents():
        try:
           
            
            event_image_dict = {}
           
            events = Event.query.all()
            for event in events:
              event_id = event.id
            
              image_events = ImageEvent.query.filter_by(event_id=event_id).all()

              
              image_ids = [image_event.image_id for image_event in image_events]

              
              print(f"Image IDs for event '{event.name}': {image_ids}")
              image_data = []
              for image_id in image_ids:
                 image = Image.query.get(image_id)  
                 if image:
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
        


