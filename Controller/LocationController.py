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
            # Reverse geocode to get the location
            location = LocationController.geolocator.reverse((latitude, longitude), language="en")
            if location:
                address = location.address  # Extract the full address string from the Location object
                locations = [part.strip() for part in address.split(',')]  # Split and strip each part of the address
                required_loc = ', '.join(locations[-4:])  # Join the last 4 components as a single string
                
                return required_loc  # Return the processed location string matching the DB format
            else:
                return None  # Return None if the location is not found
        except Exception as e:
            # Return the error as a string (useful for logging/debugging)
            return str(e)

        
    @staticmethod
    def addLocation(latitude, longitude):
        try:
            # Reverse geocode to get the address
            location = LocationController.geolocator.reverse((latitude, longitude), language="en")
            if location:
                address = location.address  # Extract the full address string from the Location object
                locations = [part.strip() for part in address.split(',')]  # Split the address into parts and strip spaces
                required_loc = ', '.join(locations[-4:])  # Keep only the last 4 components as a single string

                # Check if a location with the same latitude and longitude already exists
                existing_location = db.session.query(Location).filter_by(latitude=latitude, longitude=longitude).first()

                if existing_location:
                    # If the location already exists, return a message
                    return jsonify({
                        "status": "Location already exists",
                        "location_name": existing_location.name
                    }), 200

                # Create a new Location entry with the required location parts
                new_location = Location(
                    name=required_loc,  # Save the processed location string as the location name
                    latitude=latitude,
                    longitude=longitude
                )

                # Add the new location object to the session and commit it to the database
                db.session.add(new_location)
                db.session.commit()

                return jsonify({
                    "status": "Location saved successfully",
                    "location_name": required_loc
                }), 201

                return jsonify({
                    "status": "Location saved successfully",
                    "location_name": required_loc
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
