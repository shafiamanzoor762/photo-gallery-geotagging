import requests
from flask import jsonify
from config import db

from Model.Image import Image
from Model.Location import Location

from geopy.geocoders import Nominatim


class LocationController:
    geolocator = Nominatim(user_agent="FindLocationAddress")
    @staticmethod
    def get_location_from_lat_lon(latitude, longitude):
        try:
            # Reverse geocode to get the location
            location = LocationController.geolocator.reverse((latitude, longitude), language="en")
            if location:
                  address = location.address  # Extract the address string from the Location object
                  locations = [part.strip() for part in address.split(',')]  # Split the address and strip each part of extra spaces
                  required_loc = locations[-4:]  # Get the last 4 parts of the address
                  return required_loc
            else:
                return None  # Return None if the location is not found
        except Exception as e:
            # Return the error message as JSON
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    def addLocation(latitude, longitude):
        try:
            location = LocationController.geolocator.reverse((latitude, longitude), language="en")
            if location:
                address = location.address  # Extract the address string from the Location object
                
                # Create a new Location entry and store it in the database
                new_location = Location(
                    name=address,  # Save the full address as the location name
                    latitude=latitude,
                    longitude=longitude
                )
                
                # Add the new location object to the session and commit it to the database
                db.session.add(new_location)
                db.session.commit()
                
                return jsonify({"status": "Location saved successfully", "location_name": address})
            else:
                return jsonify({"error": "Location not found"}), 404
        except Exception as e:
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
                    Image.is_sync,
                    Image.capture_date,
                    Image.event_date,
                    Image.last_modified,
                    Image.location_id,
                    Image.is_deleted
                )
                .join(Image, Image.location_id == Location.id)
                .filter(Image.is_deleted == False)
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

                # Append image data to the 'images' list for this location
                grouped_data[location_name]['images'].append({
                    'id': row[4],
                    'path': row[5],
                    'isSync': row[6],
                    'captureDate': row[7],
                    'eventDate': row[8],
                    'lastModified': row[9],
                    'location_id': row[10],
                    'is_deleted':row[11]
                })

            # Return the response as JSON
            return jsonify(grouped_data), 200

        except Exception as e:
            # Catch any exceptions and return an error response
            return jsonify({"error": str(e)}), 500
