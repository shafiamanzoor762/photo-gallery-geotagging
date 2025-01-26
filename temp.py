# import requests
# from flask import jsonify
# from config import db
# from Model.Location import Location

# class LocationController:

# =======================LOCATION WITH ADDRESS=======================

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



# =======================RECOGNIZE PERSON=======================

    
    # @staticmethod
    # def recognize_person(image_path, person_name=""):
    # # Load the image from the path and encode it
    #   input_image = face_recognition.load_image_file(image_path)
    #   input_encodings = face_recognition.face_encodings(input_image)

    #   if len(input_encodings) == 0:
    #     return make_response(jsonify({'error': 'No faces found in the image'}), 400)

    # # Store the results of recognition
    #   recognition_results = []
      
    # # Loop through stored faces in the 'stored-faces' directory
    #   for stored_file in os.listdir('.\\stored-faces\\'):
    #     if stored_file.endswith(".jpg") or stored_file.endswith(".png"):
    #         stored_image_path = os.path.join('.\\stored-faces\\', stored_file)
    #         stored_image = face_recognition.load_image_file(stored_image_path)
    #         stored_encodings = face_recognition.face_encodings(stored_image)

    #         if len(stored_encodings) > 0:  # Ensure stored_encodings is not empty
    #             new_lines = []
    #             for input_encoding in input_encodings: 
    #                 matches = face_recognition.compare_faces(stored_encodings, input_encoding)
    #                 if True in matches:
    #                    name = ''
    #                    with open('./stored-faces/person.txt', 'r') as file:
    #                       lines = file.readlines()
    #                       for line in lines:
    #                          parts = line.split(';')
    #                          if len(parts) == 3:
    #                            per_name, image_path = parts[0],parts[2].split('\n')[0]
    #                            image_name = image_path.split('/')[-1]
    #                            if image_name == stored_file:
    #                              name = per_name
    #                              if person_name:
    #                               new_lines.append(f'{person_name};{parts[1]};{parts[2]}')
    #                               name=person_name

    #                            else:
    #                               new_lines.append(line)
                                  
    #                    recognition_results.append({
    #                         'file': stored_file,
    #                         'name': name,
    #                         'status': 'Match found'
    #                     })
    #                 # else:
    #                 #     recognition_results.append({
    #                 #         'file': stored_file,
    #                 #         'name':'No name',
    #                 #         'status': 'No match'
    #                 #     })
                   
    #                 elif new_lines:
    #                    with open('./stored-faces/person.txt', 'w') as file:
    #                      file.writelines(new_lines)
    #   if recognition_results:
    #     return make_response(jsonify({'results': recognition_results}), 200)
    #   else:
    #     return make_response(jsonify({'message': 'No matches found'}), 200)


    # @staticmethod
    # def recognize_person(image_path, person_name=""):
    #     # Load the image from the path and encode it
    #     input_image = face_recognition.load_image_file(image_path)
    #     input_encodings = face_recognition.face_encodings(input_image)

    #     if len(input_encodings) == 0:
    #         return make_response(jsonify({'error': 'No faces found in the image'}), 400)

    #     # Store the results of recognition
    #     recognition_results = []
    #     new_lines = []
    #     # Read stored encodings from person.txt
    #     with open('./stored-faces/person.txt', 'r') as file:
    #         lines = file.readlines()
    #         for line in lines:
    #             parts = line.split(';')
    #             if len(parts) == 3:
    #                 stored_name, encoding_str, cropped_image_path = parts[0], parts[1], parts[2].strip()
    #                 stored_encodings = [float(value) for value in encoding_str.split(',')]

    #                 # Compare input encodings to stored encodings
    #                 for input_encoding in input_encodings:
    #                     matches = face_recognition.compare_faces([stored_encodings], input_encoding)
    #                     if True in matches:
    #                         name = stored_name
    #                         if person_name:
    #                             new_lines.append(f'{person_name};{encoding_str};{cropped_image_path}\n')
    #                             name = person_name
    #                         else:
    #                             new_lines.append(line)
                            
    #                         recognition_results.append({
    #                             'file': cropped_image_path,
    #                             'name': name,
    #                             'status': 'Match found'
    #                         })
    #                         break  # Exit loop after first match
    #                     else:
    #                         new_lines.append(line)

    #     # Update person.txt if new names are provided
    #     if person_name and new_lines:
    #         with open('./stored-faces/person.txt', 'w') as file:
    #             file.writelines(new_lines)

    #     if recognition_results:
    #         return make_response(jsonify({'results': recognition_results}), 200)
    #     else:
    #         return make_response(jsonify({'message': 'No matches found'}), 200)




#------------------------------------------------------------
# --------------------DON'T TOUCH THIS CODE!!------------------
# -----------------------------------------------------------

# ==================SAVES BULK PERSONS EMBEDINGGS====================


# @app.route('/save_record', methods=['POST'])
# def save_record():
#     data = request.get_json()

#     if not data or 'directory_path' not in data:
#         return jsonify({'error': 'Directory path is required'}), 400
    
#     directory_path = data['directory_path']

#     if not os.path.isdir(directory_path):
#         return jsonify({'error': 'Provided path is not a valid directory'}), 400

#     for filename in os.listdir(directory_path):
#         file_path = os.path.join(directory_path, filename)

#         if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#             print(f"Processing {filename}...")

#             result = PictureController.extract_face(file_path)
#             print(result)

#     return jsonify({'status': 'Processing complete'}), 200

# # ==================GROUPBY PERSON UNKNOWN CLUSTERS====================
# @app.route('/recognize_person_bulk', methods=['POST'])
# def recognize_person_bulk():
#     try:
#         if request.content_length:
#           app.logger.info(f"Request size: {request.content_length} bytes")
#         files = request.files.getlist("images")
#         print(f"Received files: {[file.filename for file in files]}")
#         if not files:
#             return jsonify({"error": "No files uploaded"}), 400

#         results = []
#         for file in files:
#             try:
#                 file_data = file.read()
#                 file_base64 = base64.b64encode(file_data).decode("utf-8")
#                 print(f"Base64 encoding for {file.filename}: {file_base64[:30]}...")
#                 filename = file.filename
#                 temp_path = os.path.join("temp", filename)

#                 with open(temp_path, "wb") as temp_file:
#                     temp_file.write(file_data)

#                 try:
#                     recognition_response = PictureController.recognize_person(temp_path)
#                     print(f"Recognition response for {filename}: {recognition_response}")

#                     if recognition_response.get('status_code') == 400:
#                         print(f"Error in recognition for {filename}: {recognition_response['error']}")
#                         continue

#                     recognition_results = recognition_response.get('results', [])
#                     for result in recognition_results:
#                         result["original_image"] = file_base64 if file_base64 else None
#                         result["image_name"] = filename

#                     results.extend(recognition_results)
#                 finally:
#                     os.remove(temp_path)
#             except Exception as e:
#                 print(f"Error processing file {file.filename}: {e}")


#         grouped_results = {}
#         for result in results:
#           file_name = result.get("file", "").split("/")[-1]
#           name = result.get("name", "unknown")

#           key = f"{file_name}_{name}"

#           if key not in grouped_results:
#             grouped_results[key] = []

#           grouped_results[key].append(result)


#         return jsonify(grouped_results)

#     except Exception as e:
#         error_message = f"Error processing request: {str(e)}"
#         print(error_message)
#         return jsonify({"error": error_message}), 500