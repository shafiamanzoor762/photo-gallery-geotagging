# import requests
# from flask import jsonify
# from config import db
# from Model.Location import Location

# class LocationController:

#     @staticmethod
#     def add_location(latitude, longitude):
#         try:
#             # Reverse geocoding API to fetch the location name
#             api_key = "your_opencage_api_key"
#             url = f"https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}"

#             # Send the request to the geocoding API
#             response = requests.get(url)
#             data = response.json()

#             # Check if the API returned results
#             if data['results']:
#                 location_name = data['results'][0]['formatted']
#             else:
#                 # Return an error if no location name was found
#                 return jsonify({"error": "Location not found for the given coordinates"}), 400

#             # Create a new Location object
#             new_location = Location(
#                 name=location_name,
#                 latitude=latitude,
#                 longitude=longitude
#             )

#             # Add the new location to the session and commit to save it
#             db.session.add(new_location)
#             db.session.commit()

#             # Return the newly created location as a response
#             return jsonify({"message": "Location added successfully", "location": {
#                 "name": new_location.name,
#                 "latitude": new_location.latitude,
#                 "longitude": new_location.longitude
#             }}), 201

#         except Exception as e:
#             # Catch any exceptions and return an error response
#             return jsonify({"error": str(e)}), 500
