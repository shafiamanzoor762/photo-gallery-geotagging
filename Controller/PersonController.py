import base64, cv2, face_recognition, os, uuid, traceback
import numpy as np
import json
import json
from collections import defaultdict, deque
from sqlalchemy.orm import joinedload
# from flask import jsonify
# from models import Person, Image, ImagePerson, Link  # adjust based on your structure
from config import db

# from collections import defaultdict
from flask import jsonify,make_response



from sqlalchemy import func
from config import db

from Model.ImagePerson import ImagePerson
from Model.Person import Person
from Model.Image import Image
from Model.Link import Link
    # Folder where uploaded images will be saved.
# ASSETS_FOLDER = "Assets"
# Folder and file where face encodings are stored.
STORED_FACES_DIR = "stored-faces"
ENCODINGS_FILE =  "stored-faces\\person.txt"
# STORED_FACES_DIR = "E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\stored-faces"
STORED_FACES_DIR = "stored-faces"

ENCODINGS_FILE = os.path.join(STORED_FACES_DIR, "person.txt")
    
    # Ensure the stored faces directory exists.
if not os.path.exists(STORED_FACES_DIR):
    os.makedirs(STORED_FACES_DIR)


class PersonController():

    # @staticmethod
    # def extract_face(image_path):
    #     # Load Haar Cascade classifier for face detection.
    #     cascade_path = "E:\\PhotoGalleryGeotagging\\photo-gallery-geotagging\\haarcascade_frontalface_default.xml"
    #     haar_cascade = cv2.CascadeClassifier(cascade_path)

    #     # Read image using OpenCV and convert to grayscale.
    #     img = cv2.imread(image_path)
    #     if img is None:
    #         print("Failed to read image at:", image_path)
    #         return []

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
    #                         if encoding.shape[0] == 128:
    #                             stored_encodings.append(encoding)
    #                             stored_paths.append(parts[2])
    #                         else:
    #                             print(f"Skipping invalid encoding (wrong size): {parts[1]}")
    #                     except ValueError:
    #                         print(f"Skipping malformed encoding: {parts[1]}")
    #                         continue

    #     extracted_faces = []

    #     for (x, y, w, h) in faces:
    #         cropped_face = img[y:y + h, x:x + w]
    #         save_file = str(uuid.uuid4().hex)
    #         target_file_name = os.path.join(STORED_FACES_DIR, f"{save_file}.jpg")
    #         cv2.imwrite(target_file_name, cropped_face)

    #         rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
    #         _, buffer = cv2.imencode('.jpg', rgb_cropped_face)
    #         face_base64 = base64.b64encode(buffer).decode('utf-8')

    #         encoding = face_recognition.face_encodings(rgb_cropped_face)
    #         if len(encoding) > 0:
    #             current_encoding = np.array(encoding[0])
    #             is_duplicate = False

    #             if stored_encodings:
    #                 matches = face_recognition.compare_faces(stored_encodings, current_encoding, tolerance=0.55)
    #                 if any(matches):
    #                     is_duplicate = True

    #             if not is_duplicate:
    #                 with open(ENCODINGS_FILE, 'a') as f:
    #                     encoding_str = ",".join([str(num) for num in current_encoding])
    #                     f.write(f"unknown;{encoding_str};{target_file_name}\n")
    #                     stored_encodings.append(current_encoding)

    #                 print(f"New face saved: {target_file_name}")

    #             extracted_faces.append({
    #                 "face_path": target_file_name,
    #                 "encoding": current_encoding.tolist(),
    #                 "face_base64": face_base64
    #             })
    #         else:
    #             print(f"No encoding found for face in image: {image_path}")
    #             os.remove(target_file_name)
    #             continue

    #     return extracted_faces

# ------------------------------------------------
    @staticmethod
    def extract_face(image_path):
        try:
            # 1. Load Haar cascade with validation
            alg = "haarcascade_frontalface_default.xml"
            haar_cascade = cv2.CascadeClassifier(alg)
            if haar_cascade.empty():
                print("harcascade empty")
                return []

            # 2. Load image with validation
            img = cv2.imread(image_path)
            if img is None:
                print("image none")
                return []

            # 3. Convert to grayscale with protection
            try:
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            except cv2.error as e:
                print(f"grayscale conversion failed: {e}")
                return []

            # 4. Detect faces with error handling
            try:
                faces = haar_cascade.detectMultiScale(
                    gray_img, 
                    scaleFactor=1.05, 
                    minNeighbors=13, 
                    minSize=(100, 100)
                )
            except Exception as e:
                print(f"face detection failed: {e}")
                return []

            if len(faces) == 0:
                return []

            # 5. Prepare storage directory
            storage_dir = "stored-faces"
            os.makedirs(storage_dir, exist_ok=True)
            encodings_file = os.path.join(storage_dir, "person.txt")
            json_file = os.path.join(storage_dir, "person_group.json")

            # 6. Load existing encodings with memory protection
            stored_encodings = []
            if os.path.exists(encodings_file) and os.path.getsize(encodings_file) > 0:
                with open(encodings_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split(';')
                        if len(parts) > 2:
                            try:
                                encoding = np.array([float(num) for num in parts[1].split(',')], dtype=np.float32)  # float32 saves memory
                                if encoding.shape[0] == 128:
                                    stored_encodings.append(encoding)
                            except (ValueError, IndexError) as e:
                                print(f"skipping malformed encoding: {e}")
                                continue

            extracted_faces = []
            for i, (x, y, w, h) in enumerate(faces):
                try:
                    # Validate crop coordinates first
                    if y + h > img.shape[0] or x + w > img.shape[1]:
                        print(f"invalid face coordinates at {i}")
                        continue

                    # Crop face with bounds checking
                    cropped_face = img[y:y+h, x:x+w]
                    if cropped_face.size == 0:
                        print(f"empty face crop at {i}")
                        continue

                    # Generate filename and save
                    face_filename = f"{uuid.uuid4().hex}.jpg"
                    face_path = os.path.join(storage_dir, face_filename)
                    if not cv2.imwrite(face_path, cropped_face):
                        print(f"failed to save face at {i}")
                        continue

                    # Convert to RGB with protection
                    try:
                        rgb_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                    except Exception as e:
                        print(f"color conversion failed at {i}: {e}")
                        os.remove(face_path)
                        continue

                    # Get encoding with protection
                    try:
                        encodings = face_recognition.face_encodings(rgb_face)
                        if not encodings:
                            print(f"no encoding found at {i}")
                            os.remove(face_path)
                            continue
                            
                        current_encoding = encodings[0]
                    except Exception as e:
                        print(f"encoding failed at {i}: {e}")
                        os.remove(face_path)
                        continue

                    # Check for duplicates
                    is_duplicate = False
                    if stored_encodings:
                        try:
                            matches = face_recognition.compare_faces(
                                np.array(stored_encodings),
                                current_encoding,
                                tolerance=0.55
                            )
                            is_duplicate = any(matches)
                        except Exception as e:
                            print(f"comparison failed at {i}: {e}")
                            is_duplicate = True  # assume duplicate to be safe

                    # Save new encodings
                    if not is_duplicate:
                        try:
                            with open(encodings_file, 'a') as f:
                                encoding_str = ",".join([str(num) for num in current_encoding])
                                f.write(f"unknown;{encoding_str};{face_path}\n")
                                PersonController.update_face_paths_json(json_file, os.path.basename(face_path))
                        except Exception as e:
                            print(f"failed to save encoding at {i}: {e}")

                    # Create base64 with protection
                    try:
                        _, buffer = cv2.imencode('.jpg', rgb_face)
                        face_base64 = base64.b64encode(buffer).decode('utf-8')
                    except Exception as e:
                        print(f"base64 conversion failed at {i}: {e}")
                        face_base64 = ""  # empty string if fails

                    # Maintain same response format as before
                    extracted_faces.append({
                        "face_path": face_path.replace('\\', '/'),
                        "encoding": current_encoding.tolist(),
                        "face_base64": face_base64,
                        "location": {
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h)
                        }
                    })

                    # Explicit cleanup
                    del rgb_face, cropped_face, buffer

                except Exception as face_error:
                    print(f"face processing failed at {i}: {face_error}")
                    continue

            return extracted_faces

        except Exception as e:
            print(f"fatal error in extract_face: {e}")
            return []
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

            print("merged_persons", merged_persons)
    
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


# ----------------- GROUP BY PERSONS -----------------

    @staticmethod
    def get_person_image_groups():
     try:
        # Step 1: Load JSON data
        with open('./stored-faces/person_group.json', 'r') as f:
            json_data = json.load(f)

        # Step 2: Build image hash → image & person lookup
        image_map = {}
        person_to_images = defaultdict(list)
        image_hash_to_id = {}
        image_id_to_person = {}
        
        images = db.session.query(Image).options(joinedload(Image.persons)).filter(Image.is_deleted == False).all()
        for img in images:
            image_hash_to_id[img.hash] = img.id
            for person in img.persons:
                image_map[img.hash] = img
                person_to_images[person.id].append(img)
                image_id_to_person[img.id] = person.id

        # Step 3: Build Union-Find for linked persons
        class DSU:
            def __init__(self):
                self.parent = {}

            def find(self, x):
                if self.parent.setdefault(x, x) != x:
                    self.parent[x] = self.find(self.parent[x])
                return self.parent[x]

            def union(self, x, y):
                self.parent[self.find(x)] = self.find(y)

            def groups(self):
                roots = defaultdict(list)
                for node in self.parent:
                    roots[self.find(node)].append(node)
                return roots.values()

        dsu = DSU()
        links = db.session.query(Link).all()
        for link in links:
            dsu.union(link.person1_id, link.person2_id)

        link_groups = list(dsu.groups())  # list of sets of person IDs

        # Step 4: Add JSON-based image linkage
        # (images that appear together should be in the same group)
        image_groups = []
        visited_images = set()

        for key_img, linked_imgs in json_data.items():
            group = set()
            if key_img in image_hash_to_id:
                group.add(image_hash_to_id[key_img])
            for img_hash in linked_imgs:
                if img_hash in image_hash_to_id:
                    group.add(image_hash_to_id[img_hash])
            if group:
                if not group.issubset(visited_images):
                    image_groups.append(group)
                    visited_images.update(group)

        # Step 5: Combine all person groups with their images
        grouped_data = []

        seen_person_ids = set()
        seen_image_ids = set()

        for person_group in link_groups:
            group_entry = None
            for person_id in person_group:
                person = db.session.query(Person).filter_by(id=person_id).first()
                if not person:
                    continue

                person_images = [
                    img for img in person_to_images.get(person_id, [])
                    if img.id not in seen_image_ids
                ]

                if not person_images:
                    continue

                if not group_entry:
                    group_entry = {
                        "Person": {
                            "id": person.id,
                            "name": person.name,
                            "path": person.path,
                            "gender": person.gender
                        },
                        "Images": []
                    }

                for image in person_images:
                    seen_image_ids.add(image.id)
                    group_entry["Images"].append(image.to_dict())

                seen_person_ids.add(person.id)

            if group_entry:
                grouped_data.append(group_entry)

        # Step 6: Add groups from image-based JSON that are not already seen
        for image_group in image_groups:
            group_entry = None
            for image_id in image_group:
                image = db.session.query(Image).filter_by(id=image_id, is_deleted=False).first()
                if not image or image.id in seen_image_ids:
                    continue

                person_id = image_id_to_person.get(image_id)
                if not person_id or person_id in seen_person_ids:
                    continue

                person = db.session.query(Person).filter_by(id=person_id).first()
                if not person:
                    continue

                if not group_entry:
                    group_entry = {
                        "Person": {
                            "id": person.id,
                            "name": person.name,
                            "path": person.path,
                            "gender": person.gender
                        },
                        "Images": []
                    }

                group_entry["Images"].append(image.to_dict())
                seen_image_ids.add(image.id)
                seen_person_ids.add(person_id)

            if group_entry:
                grouped_data.append(group_entry)

        # Step 7: Add any remaining persons with valid images not yet added
        remaining = db.session.query(Person).all()
        for person in remaining:
            if person.id in seen_person_ids:
                continue

            images = [
                img for img in person_to_images.get(person.id, [])
                if img.id not in seen_image_ids
            ]

            if not images:
                continue

            group_entry = {
                "Person": {
                    "id": person.id,
                    "name": person.name,
                    "path": person.path,
                    "gender": person.gender
                },
                "Images": [img.to_dict() for img in images]
            }

            for img in images:
                seen_image_ids.add(img.id)

            grouped_data.append(group_entry)

        return jsonify(grouped_data)

     except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

        

#------------------ GET ALL TRANING IMAGES OF A PERSON ----------------

    @staticmethod
    def get_person_and_linked_as_list(person_id):
    # Get the main person
        main_person = Person.query.get(person_id)
        if not main_person:
            return jsonify({"personList": []}), 404

        # Get linked IDs (bidirectionally)
        linked_ids = db.session.query(Link.person2_id).filter(Link.person1_id == person_id).all()
        linked_ids += db.session.query(Link.person1_id).filter(Link.person2_id == person_id).all()
    
        # Flatten and remove duplicates and self
        linked_ids = set(pid for tup in linked_ids for pid in tup if pid != person_id)

        # Query linked persons
        linked_persons = Person.query.filter(Person.id.in_(linked_ids)).all()

        # Build the complete list
        all_persons = [main_person] + linked_persons

        # Format JSON
        person_list = [
            {
                "id": p.id,
                "name": p.name,
                "path": p.path,
                "gender": p.gender
            } for p in all_persons
        ]

        return jsonify(person_list), 200
    
    #------------------ GET ALL TRANING IMAGES OF A PERSON ----------------

    @staticmethod
    def get_person_and_linked_as_list(person_id):
    # Get the main person
        main_person = Person.query.get(person_id)
        if not main_person:
            return jsonify({"personList": []}), 404

        # Get linked IDs (bidirectionally)
        linked_ids = db.session.query(Link.person2_id).filter(Link.person1_id == person_id).all()
        linked_ids += db.session.query(Link.person1_id).filter(Link.person2_id == person_id).all()
    
        # Flatten and remove duplicates and self
        linked_ids = set(pid for tup in linked_ids for pid in tup if pid != person_id)

        # Query linked persons
        linked_persons = Person.query.filter(Person.id.in_(linked_ids)).all()

        # Build the complete list
        all_persons = [main_person] + linked_persons

        # Format JSON
        person_list = [
            {
                "id": p.id,
                "name": p.name,
                "path": p.path,
                "gender": p.gender
            } for p in all_persons
        ]

        return jsonify(person_list), 200
    

    def update_face_paths_json(json_file, path, matchedPath=None):
        # Ensure the JSON file exists; if not, initialize an empty dict
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        # If matchedPath is given, write under that key
        if matchedPath:
            # Create the set if the key doesn't exist
            if matchedPath not in data:
                data[matchedPath] = []
            # Add the path if it's not already there
            if path not in data[matchedPath]:
                data[matchedPath].append(path)
        else:
            # Treat path as a new key
            if path not in data:
                data[path] = []

        # Write the updated data back to the file
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)

# # Example usage:
# update_face_paths_json("faces.json", "face1.jpg")
# update_face_paths_json("faces.json", "face2.jpg", matchedPath="face1.jpg")
            
            
    
