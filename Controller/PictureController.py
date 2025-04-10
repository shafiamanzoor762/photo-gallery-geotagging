import base64
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
from Model.Link import Link
    # Folder where uploaded images will be saved.
# ASSETS_FOLDER = "Assets"
# Folder and file where face encodings are stored.
# STORED_FACES_DIR = "E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces"
STORED_FACES_DIR = "stored-faces"

ENCODINGS_FILE = os.path.join(STORED_FACES_DIR, "person.txt")
    
    # Ensure the stored faces directory exists.
if not os.path.exists(STORED_FACES_DIR):
    os.makedirs(STORED_FACES_DIR)


class PictureController():
    # @staticmethod
    # def extract_face(image_path):
    #     # Load Haar Cascade classifier for face detection.
    #     cascade_path = "E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\haarcascade_frontalface_default.xml"
    #     # cascade_path = "haarcascade_frontalface_default.xml"

    #     haar_cascade = cv2.CascadeClassifier(cascade_path)

    #     # Read image using OpenCV and convert to grayscale.
    #     img = cv2.imread(image_path)
    #     if img is None:
    #         print("Failed to read image at:", image_path)
    #         # Instead of returning an HTTP response, return an empty list.
    #         return []
    #     # Use the original BGR image for saving cropped faces (to keep them colorful)
    #     gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    #     # Detect faces in the image.
    #     faces = haar_cascade.detectMultiScale(
    #         gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
    #     )

    #     # Load stored face encodings from text file.
    #     stored_encodings = []
    #     stored_paths = []
    #     if os.path.exists(ENCODINGS_FILE) and os.stat(ENCODINGS_FILE).st_size > 0:
    #         with open(ENCODINGS_FILE, 'r') as f:
    #             for line in f.readlines():
    #                 parts = line.strip().split(';')
    #                 if len(parts) > 2:
    #                     encoding_values = parts[1].split(',')
    #                     try:
    #                         encoding = np.array([float(num) for num in encoding_values])
    #                         if encoding.shape[0] == 128:  # Valid encoding should be 128-dimensional.
    #                             stored_encodings.append(encoding)
    #                             stored_paths.append(parts[2])
    #                         else:
    #                             print(f"Skipping invalid encoding (wrong size): {parts[1]}")
    #                     except ValueError:
    #                         print(f"Skipping malformed encoding: {parts[1]}")
    #                         continue

    #     extracted_faces = []  # List to store info for each extracted face.

    #     # Process each detected face.
    #     for (x, y, w, h) in faces:
    #         # Crop the face from the original image (BGR) so that the saved image remains colorful.
    #         cropped_face = img[y:y + h, x:x + w]

    #         # Generate a unique filename for this cropped face.
    #         save_file = str(uuid.uuid4().hex)
    #         target_file_name = os.path.join(STORED_FACES_DIR, f"{save_file}.jpg")
    #         cv2.imwrite(target_file_name, cropped_face)

    #         # Convert the cropped face to RGB for face_recognition.
    #         rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)

    #         # Encode the image as Base64 for display (optional).
    #         _, buffer = cv2.imencode('.jpg', rgb_cropped_face)
    #         face_base64 = base64.b64encode(buffer).decode('utf-8')

    #         # Compute the face encoding.
    #         encoding = face_recognition.face_encodings(rgb_cropped_face)
    #         if len(encoding) > 0:
    #             current_encoding = np.array(encoding[0])
    #             is_duplicate = False
    #             duplicate_path = None

    #             # Compare with stored encodings if any exist.
    #             if stored_encodings:
    #                 matches = face_recognition.compare_faces(stored_encodings, current_encoding, tolerance=0.55)
    #                 print(f"Face matches: {matches}")
    #                 if any(matches):
    #                     is_duplicate = True
    #                     duplicate_index = matches.index(True)
    #                     duplicate_path = stored_paths[duplicate_index]
    #                     print(f"Duplicate detected, reusing stored face: {duplicate_path}")

    #             # If duplicate is found, reuse its path.
    #             if is_duplicate:
    #                 final_face_path = duplicate_path
    #                 os.remove(target_file_name)  # Remove the newly saved duplicate.
    #             else:
    #                 final_face_path = target_file_name
    #                 # Save the new encoding to the ENCODINGS_FILE.
    #                 with open(ENCODINGS_FILE, 'a') as f:
    #                     encoding_str = ",".join([str(num) for num in current_encoding])
    #                     f.write(f"unknown;{encoding_str};{target_file_name}\n")
    #                 print(f"New face saved: {target_file_name}")

    #             extracted_faces.append({
    #                 "face_path": final_face_path,
    #                 "encoding": current_encoding.tolist(),
    #                 "face_base64": face_base64
    #             })
    #         else:
    #             print(f"No encoding found for face in image: {image_path}")
    #             os.remove(target_file_name)
    #             continue

    #     # Instead of returning an HTTP response, we return the extracted face info.
    #     return extracted_faces


    @staticmethod
    def extract_face(image_path):
        # Load Haar Cascade classifier for face detection.
        cascade_path = "haarcascade_frontalface_default.xml"
        haar_cascade = cv2.CascadeClassifier(cascade_path)

        # Read image using OpenCV and convert to grayscale.
        img = cv2.imread(image_path)
        if img is None:
            print("Failed to read image at:", image_path)
            return []

        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Detect faces in the image.
        faces = haar_cascade.detectMultiScale(
            gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
        )

        # Load stored face encodings from text file.
        stored_encodings = []
        stored_paths = []
        if os.path.exists(ENCODINGS_FILE) and os.stat(ENCODINGS_FILE).st_size > 0:
            with open(ENCODINGS_FILE, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split(';')
                    if len(parts) > 2:
                        encoding_values = parts[1].split(',')
                        try:
                            encoding = np.array([float(num) for num in encoding_values])
                            if encoding.shape[0] == 128:
                                stored_encodings.append(encoding)
                                stored_paths.append(parts[2])
                            else:
                                print(f"Skipping invalid encoding (wrong size): {parts[1]}")
                        except ValueError:
                            print(f"Skipping malformed encoding: {parts[1]}")
                            continue

        extracted_faces = []

        for (x, y, w, h) in faces:
            cropped_face = img[y:y + h, x:x + w]
            save_file = str(uuid.uuid4().hex)
            target_file_name = os.path.join(STORED_FACES_DIR, f"{save_file}.jpg")
            cv2.imwrite(target_file_name, cropped_face)

            rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', rgb_cropped_face)
            face_base64 = base64.b64encode(buffer).decode('utf-8')

            encoding = face_recognition.face_encodings(rgb_cropped_face)
            if len(encoding) > 0:
                current_encoding = np.array(encoding[0])
                is_duplicate = False

                if stored_encodings:
                    matches = face_recognition.compare_faces(stored_encodings, current_encoding, tolerance=0.55)
                    if any(matches):
                        is_duplicate = True

                if not is_duplicate:
                    with open(ENCODINGS_FILE, 'a') as f:
                        encoding_str = ",".join([str(num) for num in current_encoding])
                        f.write(f"unknown;{encoding_str};{target_file_name}\n")
                        stored_encodings.append(current_encoding)

                    print(f"New face saved: {target_file_name}")

                extracted_faces.append({
                    "face_path": target_file_name,
                    "encoding": current_encoding.tolist(),
                    "face_base64": face_base64
                })
            else:
                print(f"No encoding found for face in image: {image_path}")
                os.remove(target_file_name)
                continue

        return extracted_faces



    # @staticmethod
    # def extract_face(image_path):
    #     # Load Haar cascade algorithm
    #     alg = "E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\haarcascade_frontalface_default.xml"
    #     haar_cascade = cv2.CascadeClassifier(alg)

       
    #     img = cv2.imread(image_path)  
    #     gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  

        
    #     faces = haar_cascade.detectMultiScale(
    #         gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
    #     )

    #     # Directory to store the face encodings and image filenames
    #     # ./stored-faces/person.txt
 
    #     encodings_file = 'E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces\\person.txt'
    #     # ./stored-faces
    #     if not os.path.exists('E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces'):
    #         os.makedirs('E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces')

        
    #     stored_encodings = []
    #     if os.path.exists(encodings_file) and os.stat(encodings_file).st_size > 0:
    #         with open(encodings_file, 'r') as f:
    #             for line in f.readlines():
    #                 parts = line.strip().split(';')
    #                 if len(parts) > 1:  
    #                     encoding = np.array([float(num) for num in parts[1].split(',')])  
    #                     stored_encodings.append(encoding)

        
    #     unique_faces_count = 0
    #     save_file = str(uuid.uuid4().hex)
        
    #     for (x, y, w, h) in faces:
            
    #         cropped_face = gray_img[y:y + h, x:x + w]

    #         # Save the cropped face image in the directory
    #          # target_file_name = f'./stored-faces/{save_file}.jpg'

    #         target_file_name = f'E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces/{save_file}.jpg'
    #         cv2.imwrite(target_file_name, cropped_face)

            
    #         rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)

            
    #         encoding = face_recognition.face_encodings(rgb_cropped_face)

            
    #         if len(encoding) > 0:
    #             current_encoding = encoding[0]

                
    #             if os.stat(encodings_file).st_size == 0:
    #                 with open(encodings_file, 'a') as f:
    #                     encoding_str = ",".join([str(num) for num in current_encoding])
    #                     f.write(f"unknown;{encoding_str};{target_file_name}\n")

    #             else:
                   
    #                 if len(stored_encodings) > 0:
    #                     matches = face_recognition.compare_faces(stored_encodings, current_encoding)

                        
    #                     if not any(matches):
    #                         with open(encodings_file, 'a') as f:
    #                             encoding_str = ",".join([str(num) for num in current_encoding])
    #                             f.write(f"unknown;{encoding_str};{target_file_name}\n")
    #                         save_file = str(uuid.uuid4().hex)
    #         else:
                
    #             current_encoding = None  
    #             print(f"No encoding found for face in image: {image_path}")
                
    #             continue

    #         save_file = str(uuid.uuid4().hex)

    #     return make_response(jsonify({'status': 'Faces saved successfully'}), 200)


# =======================RECOGNIZE PERSON=======================

    @staticmethod
    def recognize_person(image_path, person_name=""):
    
     input_image = face_recognition.load_image_file(image_path)
     input_encodings = face_recognition.face_encodings(input_image)

     if len(input_encodings) == 0:
        return {'error': 'No faces found in the image', 'status_code': 400}

    
     recognition_results = []
     new_lines = []
    # Read stored encodings from person.txt
    # ./stored-faces/person.txt
     with open('./stored-faces/person.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split(';')
            if len(parts) == 3:
                stored_name, encoding_str, cropped_image_path = parts[0], parts[1], parts[2].strip()
                stored_encodings = [float(value) for value in encoding_str.split(',')]

                
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
                        break  
                    else:
                        new_lines.append(line)

    
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
            # Query all data from the ImagePerson table
            records = db.session.query(ImagePerson).all()
    
            # Dictionary to store merged persons
            merged_persons = {}
    
            def find_root(person_id):
                """ Find the representative person ID (root) for linked persons """
                if person_id not in merged_persons:
                    return person_id
                while merged_persons[person_id] != person_id:
                    person_id = merged_persons[person_id]
                return person_id
    
            # Initialize merged persons with self-links
            all_links = db.session.query(Link).all()
            for link in all_links:
                merged_persons[link.person1_id] = link.person1_id
                merged_persons[link.person2_id] = link.person2_id
    
            # Union-Find to merge linked persons
            for link in all_links:
                root1 = find_root(link.person1_id)
                root2 = find_root(link.person2_id)
                if root1 != root2:
                    merged_persons[root2] = root1
    
            grouped_data = {}
    
            for record in records:
                person_id = find_root(record.person_id)  # Get the merged person ID
    
                # Fetch person details
                person = db.session.query(Person).filter_by(id=person_id).first()
                if not person:
                    continue
    
                # Fetch image details, ensuring only non-deleted images
                image = db.session.query(Image).filter_by(id=record.image_id, is_deleted=False).first()
                if not image:
                    continue
    
                if person.id not in grouped_data:
                    grouped_data[person.id] = {
                        "Person": {
                            "id": person.id,
                            "name": person.name,
                            "path": person.path,
                            "gender": person.gender
                        },
                        "Images": []
                    }
    
                # Append image details
                grouped_data[person.id]["Images"].append({
                    "id": image.id,
                    "path": image.path,
                    "is_sync": image.is_sync,
                    "capture_date": image.capture_date,
                    "event_date": image.event_date,
                    "last_modified": image.last_modified,
                    "location_id": image.location_id,
                    "is_deleted": image.is_deleted
                })
    
            # Convert dictionary to list
            result = list(grouped_data.values())
            return jsonify(result)
        
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    

    
    
        
            
            
    
