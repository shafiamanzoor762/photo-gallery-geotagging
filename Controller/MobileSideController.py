from flask import jsonify, request,Response
import os, json
import base64
from collections import defaultdict

from Model.Person import Person
from Model.Image import Image
from Model.Link import Link

from Controller.PersonController import PersonController
from Controller.ImageController import ImageController
from config import db

class MobileSideController:

    @staticmethod
    def add_mobile_image(image_path):
        try:
            # Extract faces from the image
            extracted_faces = PersonController.extract_face(image_path)
            if not extracted_faces:
                return jsonify({'message': 'No faces found'}), 200
    
            response_data = []
    
            for face_data in extracted_faces:
                face_path = face_data["face_path"]
                face_filename = os.path.basename(face_path)
                db_face_path = f"face_images/{face_filename}"
    
                matched_person = None
                match_data = PersonController.recognize_person(f"./stored-faces/{face_filename}")
                
                if match_data and "results" in match_data and match_data["results"]:

                    result = match_data["results"][0]
                    normalized_path = result["file"].replace("\\", "/")
                    face_path_1 = normalized_path.replace('stored-faces', 'face_images')
                    matched_person = Person.query.filter_by(path=face_path_1).first()
                    
                    for res in  match_data["results"]:
                        resembeled_path = os.path.basename(res["file"])
                        print(resembeled_path)
                        if(face_filename != resembeled_path):
                            PersonController.update_face_paths_json("./stored-faces/person_group.json", face_filename, matchedPath=resembeled_path)
    
                if not matched_person:
                     # Get ID without committing
                    print(f"✅ New person added: {db_face_path}")

                    response_data.append({
                        "status": "new",
                        "name": "unknown",
                        "path": db_face_path,
                        "gender": "U"
                    })
                else:

                    response_data.append({
                        "status": "matched",
                        "name": matched_person.name,
                        "path": db_face_path,
                        "gender": matched_person.gender
                    })
    
            
            return jsonify(response_data), 201
    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return jsonify({'error': str(e)}), 500
        
    


    @staticmethod
    def get_person_groups_from_data(persons, links, image_persons, image_ids):
     try:
        # print(persons,links,image_persons,image_ids)

        # Load JSON file
        with open('./stored-faces/person_group.json', 'r') as f:
            json_groups = json.load(f)

        # Step 1: Create path → person.id map from provided persons
        path_to_person = {
            os.path.basename(p["path"]): p["id"]
            for p in persons if "path" in p
        }

        # Step 2: Build mapping from JSON group key → person IDs
        json_group_id_to_person_ids = {}
        for key_path, group_paths in json_groups.items():
            group_ids = set()
            if key_path in path_to_person:
                group_ids.add(path_to_person[key_path])
            for p in group_paths:
                if p in path_to_person:
                    group_ids.add(path_to_person[p])
            if group_ids:
                json_group_id_to_person_ids[key_path] = group_ids

        # Step 3: Initialize union-find to merge groups
        parent = {}

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px = find(x)
            py = find(y)
            if px != py:
                parent[py] = px

        json_group_keys = list(json_group_id_to_person_ids.keys())
        group_key_to_index = {k: idx for idx, k in enumerate(json_group_keys)}
        for idx in range(len(json_group_keys)):
            parent[idx] = idx

        person_id_to_group_index = {}
        for key, ids in json_group_id_to_person_ids.items():
            idx = group_key_to_index[key]
            for pid in ids:
                person_id_to_group_index[pid] = idx

        # Step 4: Apply unions based on links
        for link in links:
            g1 = person_id_to_group_index.get(link["person1_id"])
            g2 = person_id_to_group_index.get(link["person2_id"])
            if g1 is not None and g2 is not None and g1 != g2:
                union(g1, g2)

        # Step 5: Final groupings
        merged_groups = defaultdict(set)
        for pid, idx in person_id_to_group_index.items():
            root_idx = find(idx)
            merged_groups[root_idx].add(pid)

        # Step 6: Prepare grouped output
        grouped_data = {}
        used_image_ids_per_group = {}

        for group_idx, person_ids in merged_groups.items():
            for person_id in person_ids:
                person = next((p for p in persons if p["id"] == person_id), None)
                if not person:
                    continue

                # Find image ids for the person that are in the provided image_ids
                person_image_ids = [
                    ip["image_id"] for ip in image_persons
                    if ip["person_id"] == person_id and ip["image_id"] in image_ids
                ]

                if group_idx not in grouped_data:
                    grouped_data[group_idx] = {
                        "Person": {
                            "id": person["id"],
                            "name": person.get("name"),
                            "path": person.get("path"),
                            "gender": person.get("gender"),
                            "dob": person.get("dob"),
                            "age": person.get("age")
                        },
                        "Images": []
                    }
                    used_image_ids_per_group[group_idx] = set()
                    # print(grouped_data)

                for img_id in person_image_ids:
                    if img_id not in used_image_ids_per_group[group_idx]:
                        grouped_data[group_idx]["Images"].append({"id": img_id})
                        used_image_ids_per_group[group_idx].add(img_id)
                        # print(grouped_data)

        print(grouped_data)

        result = list(grouped_data.values())
        return result


     except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500
     

    @staticmethod
    def get_unlinked_persons_by_id(person_id, persons, links):
     try:
        # Get target person's details
        target_person = next((p for p in persons if p["id"] == person_id), None)
        if not target_person:
            return {"error": "Person not found"}, 404
        
        person_name = target_person.get("name")
        if not person_name:
            return {"error": "Person has no name"}, 400

        # Load face grouping JSON
        with open('./stored-faces/person_group.json', 'r') as f:
            json_groups = json.load(f)

        # Create mappings
        path_to_person = {os.path.basename(p["path"]): p["id"] for p in persons if "path" in p}
        id_to_person = {p["id"]: p for p in persons}

        # Build person ID → group keys mapping
        person_id_to_groups = defaultdict(set)
        for key_path, group_paths in json_groups.items():
            if key_path in path_to_person:
                person_id_to_groups[path_to_person[key_path]].add(key_path)
            for p in group_paths:
                if p in path_to_person:
                    person_id_to_groups[path_to_person[p]].add(key_path)

        # Find existing links
        linked_person_ids = {
            link["person2_id"] if link["person1_id"] == person_id else link["person1_id"]
            for link in links 
            if person_id in (link["person1_id"], link["person2_id"])
        }

        # Find potential matches
        result = []
        for person in persons:
            # Skip if: same person, different name, or already linked
            if (person["id"] == person_id or 
                person.get("name") != person_name or
                person["id"] in linked_person_ids):
                continue

            # Get group members as full person objects
            group_persons = []
            for group_key in person_id_to_groups.get(person["id"], set()):
                for path in json_groups.get(group_key, []):
                    if path in path_to_person:
                        member_id = path_to_person[path]
                        if member_id in id_to_person and member_id != person_id:
                            group_persons.append(id_to_person[member_id])

            # Remove duplicates by ID
            unique_persons = []
            seen_ids = set()
            for p in group_persons:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    unique_persons.append(p)

            if unique_persons:
                result.append({
                    "person": {
                        "id": person["id"],
                        "name": person.get("name"),
                        "path": person.get("path"),
                        "gender": person.get("gender")
                    },
                    "persons": unique_persons,
                    "shared_groups": list(person_id_to_groups.get(person["id"], set()))
                })

        print(result)
        return result

     except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500


    @staticmethod
    def get_unsync_images_new():
        images = Image.query.filter(Image.is_sync == False).all()
        sync_images = []
        links = []
    
        for image in images:
            image_details = ImageController.get_image_complete_details(image.id)
            if image_details:
                sync_images.append(image_details)
    
                for person in image.persons:
                    res, status = PersonController.get_person_and_linked_as_list(person.id)
                    if status == 200:
                        if isinstance(res, Response):
                            res_data = res.get_json()
                        else:
                            res_data = res
                        
                        link_data = MobileSideController.convert_to_linked_paths(res_data)
                        links.append(link_data)
    
        print({
            "images": sync_images,
            "links": links
            })
        
        return {
            "images": sync_images,
            "links": links
            }

    

    def convert_to_linked_paths(person_list):
     if not person_list or len(person_list) < 2:
        return {}

     first_path = person_list[0].get("path")
     remaining_paths = [p["path"] for p in person_list[1:] if "path" in p]

     return {first_path: remaining_paths}


    def build_links_from_image(image):
     links_dict = defaultdict(list)

     for person in image.persons:
        person_id = person.id

        # Call the method (directly invoke underlying logic instead of jsonify)
        main_person = Person.query.get(person_id)
        if not main_person:
            continue

        # Get linked IDs (bidirectionally)
        linked_ids = db.session.query(Link.person2_id).filter(Link.person1_id == person_id).all()
        linked_ids += db.session.query(Link.person1_id).filter(Link.person2_id == person_id).all()
        
        # Flatten and remove duplicates and self
        linked_ids = set(pid for tup in linked_ids for pid in tup if pid != person_id)

        # Query linked persons
        linked_persons = Person.query.filter(Person.id.in_(linked_ids)).all()

        # Add links to the dict using path
        current_path = main_person.path
        linked_paths = [p.path for p in linked_persons if p.path and p.path != current_path]

        # Avoid overwriting if already added
        if current_path not in links_dict:
            links_dict[current_path] = []

        # Add unique paths
        for lp in linked_paths:
            if lp not in links_dict[current_path]:
                links_dict[current_path].append(lp)

     return dict(links_dict)
