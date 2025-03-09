import requests
from flask import jsonify
from config import db

from Model.Image import Image
from Model.Location import Location

import requests
from flask import jsonify
from config import db
from Model.Location import Location
from geopy.geocoders import Nominatim


class LocationController:
    geolocator = Nominatim(user_agent="FindLocationAddress")
    @staticmethod
    def get_location_from_lat_lon(latitude, longitude):

        try:
            
            location = LocationController.geolocator.reverse((latitude, longitude), language="en")
            if location:
                  address = location.address  
                  locations = [part.strip() for part in address.split(',')]  
                  required_loc = locations[-4:] 
                
                  return required_loc
            #       return jsonify({"location": required_loc})
            # else:
            #     return jsonify({"error": "Location not found"}), 404
        except Exception as e:
            
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    def addLocation(latitude, longitude):
        try:
            
            location = LocationController.geolocator.reverse((latitude, longitude), language="en")
            if location:
                address = location.address  

               
                existing_location = db.session.query(Location).filter_by(latitude=latitude, longitude=longitude).first()

                if existing_location:
                    
                    return jsonify({
                        "status": "Location already exists",
                        "location_name": existing_location.name
                    }), 200

                
                new_location = Location(
                    name=address,  
                    latitude=latitude,
                    longitude=longitude
                )

                
                db.session.add(new_location)
                db.session.commit()

                return jsonify({
                    "status": "Location saved successfully",
                    "location_name": address
                }), 201
            else:
                return jsonify({"error": "Location not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    def group_by_location():
        try:
            
            results = (
                db.session.query(
                    Location.id,
                    Location.name,
                    Location.latitude,
                    Location.longitude,
                    Image.id,
                    Image.path,
                    Image.is_sync,
                    Image.capture_date,
                    Image.event_date,
                    Image.last_modified,
                    Image.location_id
                )
                .join(Image, Image.location_id == Location.id)
                .all()
            )

            
            grouped_data = {}
            for row in results:
                location_id = row[0]
                location_name = row[1]
                latitude = row[2]
                longitude = row[3]

                
                if location_name not in grouped_data:
                    grouped_data[location_name] = {
                        'latitude': float(latitude) if latitude else None,
                        'longitude': float(longitude) if longitude else None,
                        'images': []
                    }

                
                grouped_data[location_name]['images'].append({
                    'id': row[4],
                    'path': row[5],
                    'isSync': row[6],
                    'captureDate': row[7],
                    'eventDate': row[8],
                    'lastModified': row[9],
                    'location_id': row[10]
                })

           
            return jsonify(grouped_data), 200

        except Exception as e:
           
            return jsonify({"error": str(e)}), 500
