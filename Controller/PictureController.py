from flask import jsonify,make_response
import cv2
import face_recognition
import os
import numpy as np
import uuid

class PictureController():

    @staticmethod
    def extract_face(image_path):
        # Load Haar cascade algorithm
        alg = "haarcascade_frontalface_default.xml"
        haar_cascade = cv2.CascadeClassifier(alg)

        # Load the image in color (for saving) and grayscale (for face detection)
        img = cv2.imread(image_path)  # Read in color for saving and encoding
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # Convert to grayscale for detection

        # Detect faces in the image
        faces = haar_cascade.detectMultiScale(
            gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
        )

        # Directory to store the face encodings and image filenames
        encodings_file = './stored-faces/person.txt'
        if not os.path.exists('./stored-faces'):
            os.makedirs('./stored-faces')

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
            target_file_name = f'./stored-faces/{save_file}.jpg'
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
                # If no stored encodings, just save the current one
                with open(encodings_file, 'a') as f:
                    encoding_str = ",".join([str(num) for num in current_encoding])
                    f.write(f"unknown;{encoding_str};{target_file_name}\n")
            save_file = str(uuid.uuid4().hex)

        return make_response(jsonify({'status': 'Faces saved successfully'}), 200)


    
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


    @staticmethod
    def recognize_person(image_path, person_name=""):
        # Load the image from the path and encode it
        input_image = face_recognition.load_image_file(image_path)
        input_encodings = face_recognition.face_encodings(input_image)

        if len(input_encodings) == 0:
            return make_response(jsonify({'error': 'No faces found in the image'}), 400)

        # Store the results of recognition
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
            return make_response(jsonify({'results': recognition_results}), 200)
        else:
            return make_response(jsonify({'message': 'No matches found'}), 200)
