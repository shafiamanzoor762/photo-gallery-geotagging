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
# Person , Image  # Correct import path for your model


class PictureController():


    @staticmethod
    def extract_face(image_path):
        
        alg = "D:\python\photo-gallery-geotagging\haarcascade_frontalface_default.xml"
        haar_cascade = cv2.CascadeClassifier(alg)

       
        img = cv2.imread(image_path)  
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  

        
        faces = haar_cascade.detectMultiScale(
            gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
        )

        
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

        
        unique_faces_count = 0
        save_file = str(uuid.uuid4().hex)
        
        for (x, y, w, h) in faces:
            
            cropped_face = gray_img[y:y + h, x:x + w]

           
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

                else:
                   
                    if len(stored_encodings) > 0:
                        matches = face_recognition.compare_faces(stored_encodings, current_encoding)

                        
                        if not any(matches):
                            with open(encodings_file, 'a') as f:
                                encoding_str = ",".join([str(num) for num in current_encoding])
                                f.write(f"unknown;{encoding_str};{target_file_name}\n")
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
            
            records = db.session.query(ImagePerson).all()

           
            grouped_data = {}
            for record in records:
                if record.person_id not in grouped_data:
                    grouped_data[record.person_id] = []
                grouped_data[record.person_id].append(record.image_id)

            
            result = []
            for person_id, images in grouped_data.items():
               jsonify(result.append({"Person_id": person_id, "Images": images}))

           
            return (result)
        except Exception as e:
            print(f"Error: {e}")
            return None




