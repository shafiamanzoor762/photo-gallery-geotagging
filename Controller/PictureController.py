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


    @staticmethod
    def extract_face(image_path):
        # Load Haar cascade algorithm
        alg = "haarcascade_frontalface_default.xml"
        haar_cascade = cv2.CascadeClassifier(alg)

       
        img = cv2.imread(image_path)  
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  

        
        faces = haar_cascade.detectMultiScale(
            gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
        )

        # Directory to store the face encodings and image filenames
        encodings_file = './stored-faces/person.txt'
        if not os.path.exists('./stored-faces'):
            os.makedirs('./stored-faces')

        
        stored_encodings = []
        if os.path.exists(encodings_file) and os.stat(encodings_file).st_size > 0:
            with open(encodings_file, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split(';')
                    if len(parts) > 1:  
                        encoding = np.array([float(num) for num in parts[1].split(',')])  
                        stored_encodings.append(encoding)
                f.close()

        
        unique_faces_count = 0
        save_file = str(uuid.uuid4().hex)
        
        for (x, y, w, h) in faces:
            
            cropped_face = gray_img[y:y + h, x:x + w]

            # Save the cropped face image in the directory
            target_file_name = f'./stored-faces/{save_file}.jpg'
            cv2.imwrite(target_file_name, cropped_face)

            
            rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)

            
            encoding = face_recognition.face_encodings(rgb_cropped_face)

            
            if len(encoding) > 0:
                current_encoding = encoding[0]

                
                if os.stat(encodings_file).st_size == 0:
                    with open(encodings_file, 'a') as f:
                        encoding_str = ",".join([str(num) for num in current_encoding])
                        f.write(f"unknown;{encoding_str};{target_file_name}\n")
                        f.close()

                else:
                   
                    if len(stored_encodings) > 0:
                        matches = face_recognition.compare_faces(stored_encodings, current_encoding)

                        
                        if not any(matches):
                            with open(encodings_file, 'a') as f:
                                encoding_str = ",".join([str(num) for num in current_encoding])
                                f.write(f"unknown;{encoding_str};{target_file_name}\n")
                                f.close()
                            save_file = str(uuid.uuid4().hex)
            else:
                
                current_encoding = None  
                print(f"No encoding found for face in image: {image_path}")
                
                continue

            save_file = str(uuid.uuid4().hex)

        return make_response(jsonify({'status': 'Faces saved successfully'}), 200)


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
    
            # Group data by person_id
            grouped_data = {}
    
            for record in records:
                # Fetch person details
                person = db.session.query(Person).filter_by(id=record.person_id).first()
                
                # Fetch image details, ensuring only images where is_deleted = False (0)
                image = db.session.query(Image).filter_by(id=record.image_id, is_deleted=False).first()
    
                if person and image:
                    if person.id not in grouped_data:
                        # Initialize person's data
                        grouped_data[person.id] = {
                            "Person": {
                                "id": person.id,
                                "name": person.name,  # Assuming person has a name field
                                "path": person.path,  # Example field
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
                        "event_date": image.event_date,
                        "last_modified": image.last_modified,
                        "location_id": image.location_id,
                        "is_deleted":image.is_deleted
                    })
    
            # Convert dictionary to list of objects
            result = list(grouped_data.values())
            print(result)
            return jsonify(result)  # Return JSON response
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    
