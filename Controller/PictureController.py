from collections import defaultdict
from flask import jsonify,make_response
import cv2
import face_recognition
import os
import numpy as np
import uuid

from sqlalchemy import func
from config import db

from Model.ImagePerson import ImagePerson
from Model.Person import Person
from Model.Image import Image


class PictureController():

# FETCH CROP FACE OF PERSON (WORK FOR GROUP IMAGES ALSO)
    @staticmethod
    def extract_face(image_path):
        # Load Haar cascade algorithm
        alg = "E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\haarcascade_frontalface_default.xml"
        haar_cascade = cv2.CascadeClassifier(alg)

        # Load the image in color (for saving) and grayscale (for face detection)
        img = cv2.imread(image_path)  # Read in color for saving and encoding
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # Convert to grayscale for detection

        # Detect faces in the image
        faces = haar_cascade.detectMultiScale(
            gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
        )

        # Directory to store the face encodings and image filenames
        encodings_file = 'E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces\\person.txt'
        if not os.path.exists('E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces'):
            os.makedirs('E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces')

        # Load previously stored encodings from the text file (if it exists)
        stored_encodings = []
        if os.path.exists(encodings_file) and os.stat(encodings_file).st_size > 0:
            with open(encodings_file, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split(';')
                    if len(parts) > 1:  # Ensure proper data format
                        encoding = np.array([float(num) for num in parts[1].split(',')])  # Extract the encoding part
                        stored_encodings.append(encoding)

        # Counter for naming unknown faces
        unique_faces_count = 0
        save_file = str(uuid.uuid4().hex)
        # Process each detected face
        for (x, y, w, h) in faces:
            # Crop the face from the image
            cropped_face = gray_img[y:y + h, x:x + w]

            # Save the cropped face image in the directory
            target_file_name = f'E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces\\{save_file}.jpg'
            cv2.imwrite(target_file_name, cropped_face)

            # Convert the cropped face to RGB (face_recognition uses RGB images)
            rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)

            # Get the encoding of the cropped face using face_recognition
            encoding = face_recognition.face_encodings(rgb_cropped_face)

            # If encoding is found (not all cropped images may produce encodings)
            if len(encoding) > 0:
                current_encoding = encoding[0]

                # If the encoding file is empty, write the first entry
                if os.stat(encodings_file).st_size == 0:
                    with open(encodings_file, 'a') as f:
                        encoding_str = ",".join([str(num) for num in current_encoding])
                        f.write(f"unknown;{encoding_str};{target_file_name}\n")

                else:
                    # Compare with previously stored encodings
                    if len(stored_encodings) > 0:
                        matches = face_recognition.compare_faces(stored_encodings, current_encoding)

                        # If no matches are found (i.e., the encoding is unique)
                        if not any(matches):
                            with open(encodings_file, 'a') as f:
                                encoding_str = ",".join([str(num) for num in current_encoding])
                                f.write(f"unknown;{encoding_str};{target_file_name}\n")
                            save_file = str(uuid.uuid4().hex)
            else:
                # Handle the case where no encoding is found
                current_encoding = None  # Set it to None to prevent uninitialized reference
                print(f"No encoding found for face in image: {image_path}")
                # Optionally, you can handle the case where no encoding is found by skipping or logging
                continue

            save_file = str(uuid.uuid4().hex)

        return make_response(jsonify({'status': 'Faces saved successfully'}), 200)


# =======================RECOGNIZE PERSON=======================

    @staticmethod
    def recognize_person(image_path, person_name=""):
    # Load the image from the path and encode it
     input_image = face_recognition.load_image_file(image_path)
     input_encodings = face_recognition.face_encodings(input_image)

     if len(input_encodings) == 0:
        return {'error': 'No faces found in the image', 'status_code': 400}

    # Store the results of recognition
     recognition_results = []
     new_lines = []
    # Read stored encodings from person.txt
     with open('E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces\\person.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split(';')
            if len(parts) == 3:
                stored_name, encoding_str, cropped_image_path = parts[0], parts[1], parts[2].strip()
                stored_encodings = [float(value) for value in encoding_str.split(',')]

                # Compare input encodings to stored encodings
                for input_encoding in input_encodings:
                    matches = face_recognition.compare_faces([stored_encodings], input_encoding)
                    if True in matches:
                        name = stored_name
                        if person_name:
                            new_lines.append(f'{person_name};{encoding_str};{cropped_image_path}\n')
                            name = person_name
                        else:
                            new_lines.append(line)

                        recognition_results.append({
                            'file': cropped_image_path,
                            'name': name,
                            'status': 'Match found'
                        })
                        break  # Exit loop after first match
                    else:
                        new_lines.append(line)

    # Update person.txt if new names are provided
     if person_name and new_lines:
        with open('./stored-faces/person.txt', 'w') as file:
            file.writelines(new_lines)

     if recognition_results:
        return {'results': recognition_results, 'status_code': 200}
     else:
        return {'message': 'No matches found', 'status_code': 200}



# =============== group by person=============
    @staticmethod
    def group_by_person():
        try:
            # Fetch all records
            records = db.session.query(ImagePerson).all()

            # Dictionary to store grouped data
            grouped_data = {}

            for record in records:
                # Fetch person details
                person = db.session.query(Person).filter_by(id=record.person_id).first()
                # Fetch image details
                image = db.session.query(Image).filter_by(id=record.image_id).first()

                if person and image:
                    if person.id not in grouped_data:
                        # Initialize person's data
                        grouped_data[person.id] = {
                            "Person": {
                                "id": person.id,
                                "name": person.name,  # Assuming person has a name field
                                "path": person.path,    # Example field
                                "gender": person.gender  # Any other fields
                            },
                            "Images": []
                        }

                    # Append image details
                    grouped_data[person.id]["Images"].append({
                        "id": image.id,
                        "path": image.path,  
                        "is_sync": image.is_sync, 
                        "capture_date": image.capture_date,
                        "event_date":image.event_date,
                        "last_modified":image.last_modified,
                        "location_id":image.location_id
                    })

            # Convert dictionary to list of objects
            result = list(grouped_data.values())

            return jsonify(result)  # Return JSON response
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500



