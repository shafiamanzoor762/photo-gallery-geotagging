
from Controller.MobileSideController import MobileSideController
from Controller.PersonController import PersonController
from Model.ImagePerson import ImagePerson
from Model.Person import Person
# from Model.Image import Image
# from Model.Link import Link
import os
import face_recognition

class TestController():

    # @staticmethod
    # def get_persons_group_from_image(image_file):

    #     persons = [
    #         {
    #             "id": p.id,
    #             "name": p.name,
    #             "path": p.path,
    #             "gender": p.gender,
    #             "dob": p.dob.isoformat() if p.dob else None,
    #             "age": p.age
    #         }
    #         for p in Person.query.all()
    #     ]

    #     links = [
    #         {
    #             "person1_id": link.person1_id,
    #             "person2_id": link.person2_id
    #         }
    #         for link in Link.query.all()
    #     ]

    #     image_ids = [
    #         image.id for image in Image.query
    #         .filter(Image.is_deleted == False)
    #         .all()
    #     ]

    #     image_persons = [
    #         {
    #             "image_id": ip.image_id,
    #             "person_id": ip.person_id
    #         }
    #         for ip in ImagePerson.query.all()
    #     ]

    #     return MobileSideController.process_image_and_get_person_groups(image_file,persons,links,image_persons,image_ids)
    
    # Mobile Side
    @staticmethod
    def process_image_and_get_person_groups_mobile(image_path, persons, links, image_persons, image_ids):

    # Step 1: Extract faces
     extracted_faces = PersonController.extract_face(image_path)
     if not extracted_faces:
        print("❌ No faces extracted.")
        return None

    # Step 2: Build path-to-person-id map
     path_to_person = {
        os.path.basename(p["path"]): p["id"]
        for p in persons if "path" in p
     }

     matched_person_ids = set()
     all_recognition_results = []

    # Step 3: Recognize each face
     for face in extracted_faces:
        face_path = face["face_path"]
        result = PersonController.recognize_person(face_path)
        if result.get("status_code") == 200 and "results" in result:
            for match in result["results"]:
                cropped_filename = os.path.basename(match["file"])
                print("cropped_filename",cropped_filename)
                person_id = path_to_person.get(cropped_filename)
                if person_id:
                    matched_person_ids.add(person_id)
                all_recognition_results.append(match)
        else:
            print(f"⚠️ No match found for face: {face_path}")

    # Step 4: Filter matched persons

     filtered_persons = [p for p in persons if p.get("id") in matched_person_ids]
     

    # Optional debug info
     print(f"✅ Matched persons: {[p.get('name') for p in filtered_persons]}")
     print(f"📸 Recognized {len(all_recognition_results)} faces total.")

    # Step 5: Call group formation logic
     return MobileSideController.get_person_groups_from_data(persons, links, image_persons, image_ids)
    

    @staticmethod 
    def process_image_and_get_person_groups_mobile(image_path, persons, links, image_persons, image_ids):
        threshold = 0.45
        matched_groups = []

        # Step 1: Extract faces from input image
        extracted_faces = PersonController.extract_face(image_path)
        if not extracted_faces:
            print("❌ No faces extracted.")
            return None

        # Step 2: Load all stored groups
        all_groups = MobileSideController.get_person_groups_from_data(persons, links, image_persons, image_ids)

        # Step 3: Loop over each extracted face
        for extracted_face in extracted_faces:
            face_path = extracted_face["face_path"]
            try:
                input_image = face_recognition.load_image_file(face_path)
                input_encodings = face_recognition.face_encodings(input_image)
                if not input_encodings:
                    print(f"⚠️ No encodings found for {face_path}")
                    continue
            except Exception as e:
                print(f"❌ Error processing input face {face_path}: {e}")
                continue

            # Step 4: Loop through each person group and compare
            for group in all_groups:
                person_face_path = group["Person"]["path"].replace('face_images', 'stored-faces')

                # If needed, prepend full path
                if not os.path.exists(person_face_path):
                    print(person_face_path.replace('face_images', 'stored-faces'))
                    person_face_path = os.path.join(person_face_path)

                try:
                    stored_image = face_recognition.load_image_file(person_face_path)
                    stored_encodings = face_recognition.face_encodings(stored_image)
                    if not stored_encodings:
                        print(f"⚠️ No encodings found for stored face {person_face_path}")
                        continue
                except Exception as e:
                    print(f"❌ Error processing stored face {person_face_path}: {e}")
                    continue

                # Step 5: Compare input face with stored face(s)
                match_found = False
                for input_encoding in input_encodings:
                    for stored_encoding in stored_encodings:
                        distance = face_recognition.face_distance([stored_encoding], input_encoding)[0]
                        if distance <= threshold:
                            matched_groups.append(group)
                            match_found = True
                            break
                    if match_found:
                        break

        if matched_groups:
            print(f"✅ Matched {len(matched_groups)} group(s).")
        else:
            print("🔍 No matching groups found.")

        return {
            'extracted_faces': [face["face_path"] for face in extracted_faces],
            'matched_groups': matched_groups
            }
    


    # Desktop Side
    @staticmethod 
    def process_image_and_get_person_groups_desktop(image_path):
        threshold = 0.45
        matched_groups = []

        # Step 1: Extract faces from input image
        extracted_faces = PersonController.extract_face(image_path)
        if not extracted_faces:
            print("❌ No faces extracted.")
            return None

        # Step 2: Load all stored groups
        all_groups = PersonController.get_person_groups()

        # Step 3: Loop over each extracted face
        for extracted_face in extracted_faces:
            face_path = extracted_face["face_path"]
            try:
                input_image = face_recognition.load_image_file(face_path)
                input_encodings = face_recognition.face_encodings(input_image)
                if not input_encodings:
                    print(f"⚠️ No encodings found for {face_path}")
                    continue
            except Exception as e:
                print(f"❌ Error processing input face {face_path}: {e}")
                continue

            # Step 4: Loop through each person group and compare
            for group in all_groups:
                person_face_path = group["Person"]["path"].replace('face_images', 'stored-faces')

                # If needed, prepend full path
                if not os.path.exists(person_face_path):
                    print(person_face_path.replace('face_images', 'stored-faces'))
                    person_face_path = os.path.join(person_face_path)

                try:
                    stored_image = face_recognition.load_image_file(person_face_path)
                    stored_encodings = face_recognition.face_encodings(stored_image)
                    if not stored_encodings:
                        print(f"⚠️ No encodings found for stored face {person_face_path}")
                        continue
                except Exception as e:
                    print(f"❌ Error processing stored face {person_face_path}: {e}")
                    continue

                # Step 5: Compare input face with stored face(s)
                match_found = False
                for input_encoding in input_encodings:
                    for stored_encoding in stored_encodings:
                        distance = face_recognition.face_distance([stored_encoding], input_encoding)[0]
                        if distance <= threshold:
                            matched_groups.append(group)
                            match_found = True
                            break
                    if match_found:
                        break

        if matched_groups:
            print(f"✅ Matched {len(matched_groups)} group(s).")
        else:
            print("🔍 No matching groups found.")

        return {
            'extracted_faces': [face["face_path"] for face in extracted_faces],
            'matched_groups': matched_groups
            }