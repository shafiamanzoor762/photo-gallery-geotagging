from datetime import datetime
from flask import Flask, request, jsonify, send_file,make_response, send_from_directory
from PIL import Image
from io import BytesIO
from config import db,app

import os, uuid, base64, json, piexif, io, tempfile, urllib

from werkzeug.utils import secure_filename
from config import db,app

from Controller.PersonController import PersonController
from Controller.EventController import EventController
from Controller.ImageController import ImageController
from Controller.LocationController import LocationController
from Controller.LinkController import LinkController
from Controller.DirectoryController import DirectoryController
from Controller.TaggingController import TaggingController
from Controller.MobileSideController import MobileSideController
from Controller.ImageHistoryController import ImageHistoryController

# ✅ Set this dynamically on startup using your helper
IMAGE_ROOT_DIR = DirectoryController.get_latest_directory()
print(IMAGE_ROOT_DIR)
if not IMAGE_ROOT_DIR:
    raise RuntimeError("No ROOT_DIR found in directory.env")


FACES_FOLDER = 'stored-faces'  
if not os.path.exists(FACES_FOLDER):
    os.makedirs(FACES_FOLDER)


# =================== TAGGING CONTROLLER ==============
# SAVE TAGS TO IMAGE
@app.route('/tagimage', methods = ['POST'])
def tagImage():
    try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404

        tags_str = request.form.get('tags')
        if not tags_str:
            return jsonify({'error': 'Tags not found'}), 400
        
        tags=json.loads(tags_str)

        return TaggingController.tagImage(file,tags)
    
    except Exception as exp:
        return jsonify({'error':str(exp)}), 500

# EXTRACT TAGS FROM IMAGE
@app.route('/extractImageTags', methods = ['POST'])
def extractImageTags():
    try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        
        return make_response(TaggingController.extractImageTags(file),201)
        
    except Exception as exp:
        return jsonify({'error':str(exp)}), 500

# =================== PICTURE CONTROLLER ==============

@app.route('/extract_face', methods=['POST'])
def extract_face():
     try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        # image_path = os.path.join('.',ASSETS_FOLDER,  str(uuid.uuid4().hex) + '.jpg')
        # print(image_path)
        image = Image.open(io.BytesIO(file.read()))
        # image.save(image_path)
        # image.save(image_path)
        temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(temp, format="JPEG")
        temp_path = temp.name
        temp.close()  # Close file so OpenCV can access it

        # Call your processing logic
        result = PersonController.extract_face(temp_path)

        # Clean up manually
        os.unlink(temp_path)

        return result
        #
     except Exception as exp:
        return jsonify({'error':str(exp)}), 500


@app.route('/recognize_person', methods=['POST'])
def recognize_person():
     
     try:
 
         # Get query parameters from the GET request
         image_path = request.args.get('image_path')
         person_name = request.args.get('name', None)

         if image_path:
             print(image_path)
            # Call the method from the PictureController class
             return PersonController.recognize_person(image_path, person_name)
 
         if 'file' in request.files:
         
             file = request.files['file']
             if file.filename == '':
                 return jsonify({'error':'filename is empty'}), 404
             
             person_name = request.form.get('name', person_name)
             print(person_name)

            #  image_path = os.path.join('.',ASSETS_FOLDER,  str(uuid.uuid4().hex) + '.jpg')
            #  print(image_path)
             image = Image.open(io.BytesIO(file.read()))
                # image.save(image_path)
             temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
             image.save(temp, format="JPEG")
             image_path = temp.name
             temp.close()
 
             return PersonController.recognize_person(image_path, person_name)
 
     except Exception as exp:
         return jsonify({'error':str(exp)}), 500


@app.route('/group_by_person', methods=['GET'])
def group_by_person():
    return PersonController.get_person_groups()


# /// mobile side 
@app.route('/get_person_groups_from_json', methods=['POST'])
def get_person_groups_from_json():
    try:
        json_data = request.get_json()  
        print(json_data)
        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        result = PersonController.get_person_groups_from_json(json_data)
        print(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get_all_person', methods=['GET'])
def get_all_person():
    return ImageController.get_all_person()

@app.route('/person/<int:person_id>', methods=['GET'])
def get_person_and_linked_as_list(person_id):
    return PersonController.get_person_and_linked_as_list(person_id)
  
#--------------------Link----------------
@app.route('/create_link', methods=['POST'])
def create_link():
        data = request.get_json()
        person1_id = data.get('person1_id')
        person2_id = data.get('person2_id')
        
        if not person1_id or not person2_id:
            return jsonify({'error': 'Both person1_id and person2_id are required'}), 400
        
        new_link = LinkController.insert_link(person1_id, person2_id)
        return jsonify({'message': 'Link created successfully'})

@app.route('/check_link', methods=['POST'])
def check_link():
        data = request.get_json()
        person1_id = data.get('person1_id')
        person2_id = data.get('person2_id')
        
        if not person1_id or not person2_id:
            return jsonify({'error': 'Both person1_id and person2_id are required'}), 400
        
        new_link = LinkController.link_exists(person1_id, person2_id)
        return jsonify(new_link)

# --------------------------IMAGE---------------------------------

@app.route('/edit_image', methods=['POST'])
def edit_Image():
    data = request.get_json(force=True, silent=True)  # Get JSON data from the request
    return ImageController.edit_image_data(data)

@app.route('/searching_on_image', methods=['POST'])
def searching():
    return ImageController.searching_on_image()

@app.route('/Load_images', methods=['POST'])
def Load_images():
    return ImageController.Load_images()
@app.route('/group_by_date',methods = ['GET'])
def group_by_date():
    return ImageController.group_by_date()


@app.route('/unedited_images', methods=['GET'])
def get_unedited_images_route():
    return ImageController.get_unedited_images()

# -----------------------------------------------------------

# --- ROUTE TO HANDLE IMAGE UPLOAD ---
# @app.route('/add_image', methods=['POST'])
# def add_image():
#     try:
#         # 1. Check if file is in request
#         if 'file' not in request.files:
#             return jsonify({'error': 'File not attached'}), 400
        
#         file = request.files['file']
        
#         if file.filename == '':
#             return jsonify({'error': 'Filename is empty'}), 400

#         original_filename = secure_filename(file.filename)

#         # 2. Read file bytes
#         file_bytes = file.read()

#         # 3. Convert to RGB if image is RGBA
#         image_obj = Image.open(io.BytesIO(file_bytes))
#         if image_obj.mode == 'RGBA':
#             image_obj = image_obj.convert('RGB')

#         # # 5. Save the image to Assets folder (or wherever you want)
#         # file_save_path = os.path.join(ASSETS_FOLDER, original_filename)
#         # with open(file_save_path, "wb") as f:
#         #     f.write(file_bytes)
#         path = request.form.get('path')

#         # 6. Get the hash from form
#         hash_value = request.form.get('hash')

#         if not hash_value:
#             return jsonify({'error': 'No hash provided'}), 400

#         # 7. Build the metadata dictionary
#         data = {
#             'path': path.replace("\\", "/"),  # Use relativePath properly (make sure it's using slashes /)
#             'hash': hash_value,
#             'is_sync': 0,
#             'capture_date': datetime.utcnow().isoformat(),
#             'event_date': None
#         }

#         # 8. Call Controller to save data
#         return ImageController.add_image(data)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



@app.route('/add_image', methods=['POST'])
def add_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'File not attached'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Filename is empty'}), 400

        original_filename = secure_filename(file.filename)

        # Load the image using file.stream (more memory-efficient)
        image_obj = Image.open(file.stream)
        if image_obj.mode == 'RGBA':
            image_obj = image_obj.convert('RGB')

        path = request.form.get('path')
        hash_value = request.form.get('hash')

        if not hash_value:
            return jsonify({'error': 'No hash provided'}), 400

        data = {
            'path': path.replace("\\", "/"),
            'hash': hash_value,
            'is_sync': 0,
            'capture_date': datetime.utcnow().isoformat(),
            'event_date': None
        }

        return ImageController.add_image(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500




# # Route to handle image uploads
# @app.route('/add_image', methods=['POST'])
# def add_image():
#     try:
#         # Check if the file is present in the request
#         if 'file' not in request.files:
#             return jsonify({'error': 'File not attached'}), 400

#         file = request.files['file']

#         # Check if the file is empty
#         if file.filename == '':
#             return jsonify({'error': 'Filename is empty'}), 400

#         # Get the original filename
#         original_filename = secure_filename(file.filename)  # Ensures filename safety

#         # Read file content once
#         file_bytes = file.read()

#         # Convert image if necessary
#         image = Image.open(io.BytesIO(file_bytes))
#         if image.mode == 'RGBA':
#             image = image.convert('RGB')
        
        
#         if not os.path.exists(ASSETS_FOLDER):
#             os.makedirs(ASSETS_FOLDER)


#         # Save the file to the 'Assets' folder with original filename
#         file_paths = os.path.join(ASSETS_FOLDER, original_filename)
#         file_path = "images/" + original_filename  # Relative path for database storage

#         with open(file_paths, "wb") as f:
#             f.write(file_bytes)

#         # Get JSON data from the request
#         json_data = request.form.get('data')
#         if not json_data:
#             return jsonify({'error': 'No JSON data provided'}), 400

#         # Parse the JSON data
#         data = json.loads(json_data)

#         # Add the file path to the data
#         data['path'] = file_path

#         # Call the ImageController.add_image method with the data
#         return ImageController.add_image(data)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# Get details of a specific Image (Read)
@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    return ImageController.get_image_details(image_id)

@app.route('/image_complete_details/<int:image_id>', methods=['GET'])
def get_image_complete_details(image_id):
    return jsonify(ImageController.get_image_complete_details(image_id))

# Delete an Image (Delete)
# @app.route('/images/<int:image_id>', methods=['DELETE'])
# def delete_image(image_id):
#     return ImageController.delete_image(image_id)

@app.route('/delete_metadata/<int:image_id>', methods=['DELETE'])
def delete_metadata(image_id):
    try:
        # Call the delete_metadata method from ImageController
        return ImageController.delete_metadata(image_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    return ImageController.delete_image(image_id)


# --------------------------EVENT---------------------------------
#done
@app.route('/fetch_events', methods = ['GET'])
def fetch_events():
    # print('am here')
    return EventController.fetch_all_events()

#add a new event 
@app.route('/addnewevent', methods=['POST'])
def addnewevent():
    #print("am in addnew event method")
    if request.is_json:
           
           json_data = request.get_json()
           
           if 'Name' not in json_data:
             return {"error": "Missing 'Name' in JSON data"}, 200
           #print("Received JSON data:", json_data)
    
    return EventController.addnewevent(json_data)

#add events to an image 
@app.route('/addevents', methods=['POST'])
def addevents():
    
    if request.is_json:
           
           json_data = request.get_json()
           
           if 'id' not in json_data or 'names' not in json_data:
             return {"error": "Missing 'name' in JSON data"}, 200
           print("Received JSON data:", json_data)
    
    return EventController.addevents(json_data)
#done

#sorting of events for Dropdown
@app.route('/groupbyevents', methods=['GET'])
def sortevents():
    return EventController.groupbyevents()

# ================Location=================

@app.route('/get_loc_from_lat_lon' , methods=['POST'])
def getlocation_from_lat_lon():
    

    data = request.get_json()
    latitude =data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and Longitude are required"}), 400
    else:
        return jsonify(LocationController.get_location_from_lat_lon(latitude,longitude))


@app.route('/addLocation' , methods=['POST'])
def addLocation():
    # # Extract latitude and longitude from query parameters
    # latitude = request.args.get('latitude', type=float)
    # longitude = request.args.get('longitude', type=float)

    data = request.get_json()
    latitude =data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and Longitude are required"}), 400
    else:
        return LocationController.addLocation(latitude,longitude)

@app.route('/group_by_location',methods = ['GET'])
def group_by_location():
    return LocationController.group_by_location() 
    
#     ######remove Metadata####################
# @app.route('/remove_metadata', methods=['POST'])
# def remove_metadata():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'File not attached'}), 400

#         file = request.files['file']
        
#         # Open the image file
#         image = Image.open(io.BytesIO(file.read()))

#         # Create a new image to strip metadata
#         img_io = io.BytesIO()

#         # Strip metadata by saving without Exif (using 'quality' argument for JPG)
#         image.save(img_io, format="JPEG", quality=95)  # JPEG without metadata
#         img_io.seek(0)

#         return send_file(img_io, mimetype='image/jpeg', download_name='image_without_metadata.jpg')

#     except Exception as e:
#         return jsonify({'error': f'Error processing image: {str(e)}'}), 500

#=====================dummy method after sync -------------------------

@app.route('/upload_image', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'File not attached'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Filename is empty'}), 400

        # Read file content once
        file_bytes = file.read()
        
        # Convert image if necessary
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Ensure 'assets' folder exists
        ASSETS_FOLDER = 'Assets'
        os.makedirs(ASSETS_FOLDER, exist_ok=True)
        data="" 
        file_paths = os.path.join(ASSETS_FOLDER,  str(uuid.uuid4().hex) + '.jpg')
        file_path="images/"+file.filename
        with open(file_paths, "wb") as f:
            f.write(file_bytes)
        
        ImageController.add_image({"path": file_path})
        return jsonify({"message": "File uploaded successfully", "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# NOTE: These methods should be at the end of the file

# Method 1: Append path to directory.env with incremented ROOT_DIR version
@app.route('/add-directory', methods=['POST'])
def add_directory_path():
    data = request.get_json()
    new_path = data.get("path")

    return DirectoryController.add_directory_path(new_path)


# [GET] http://127.0.0.1:5000/images/2




# @app.route('/images/<path:filename>', methods=['GET'])
# def get_image1(filename):
#     try:
#         print(IMAGE_ROOT_DIR,filename)
# #
#         return send_from_directory(IMAGE_ROOT_DIR, filename)
#     except FileNotFoundError:
#         return jsonify({"error": "Image not found"}), 404


@app.route('/images/<path:filepath>', methods=['GET'])
def get_image2(filepath):
    try:
        print("iamegsss")
        if not filepath:
            return jsonify({"error": "Missing file path"}), 400

        # Decode any URL-encoded characters
        decoded_path = urllib.parse.unquote(filepath)
        print("Decoded path:", decoded_path)

        # Normalize slashes
        normalized_path = decoded_path.replace("\\", "/")
        print("Normalized path:", normalized_path)

        if not os.path.exists(normalized_path):
            return jsonify({"error": "Image not found", "path": normalized_path}), 404

        directory = os.path.dirname(normalized_path)
        filename = os.path.basename(normalized_path)

        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/face_images/<filename>', methods=['GET'])
def get_face_image(filename):
    try:
        
        return send_from_directory(FACES_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404
    

@app.route('/get_merge_data', methods=['POST'])
def get_merge_data():
    try:
        data = request.get_json()
        person1 = data.get('person1')
        name = data.get('name')
        return ImageController.get_persons(person1,name)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404
    
@app.route('/merge_persons', methods=['POST'])
def merge_persons():
    try:
        data = request.get_json()
        person1 = data.get('person1_id')
        person2 = data.get('person2')
        
        return LinkController.merge_persons(person1, person2)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404
  

@app.route('/get_undo_data', methods=['GET'])
def get_undo_data():
    try:
        
        return ImageHistoryController.get_latest_inactive_non_deleted_images()
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404
 
#Aimen's mobile side code requests 

@app.route('/image_processing', methods=['POST'])
def image_processing():
     try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        # image_path = os.path.join('.',ASSETS_FOLDER,  str(uuid.uuid4().hex) + '.jpg')
        # print(image_path)
        image = Image.open(io.BytesIO(file.read()))
        # image.save(image_path)
        temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(temp, format="JPEG")
        temp_path = temp.name
        temp.close()  # Close file so OpenCV can access it

        # Call your processing logic
        result = ImageController.mobile_img_processing(temp_path)

        # Clean up manually
        os.unlink(temp_path)

        return result
        #return PersonController.extract_face(image_path)
     except Exception as exp:
        return jsonify({'error':str(exp)}), 500
     

@app.route('/get_person_images', methods=['POST'])
def get_person_images():
    json_data = request.get_json() 
    return ImageController.get_person_images(json_data)

@app.route('/load_embeddings', methods=['POST'])
def get_emb_names():
    data = request.get_json()
    persons= data.get("persons", [])
    links = data.get("links", [])
    emb_name = data.get("person1", [])
    personrecords= data.get("personrecords", [])
    return ImageController.get_emb_names(persons,links,emb_name,personrecords)


@app.route('/load_embeddings_for_recognition', methods=['POST'])
def get_emb_names_for_recognition():
    data = request.get_json()
    persons = data.get("persons", [])
    links = data.get("links", [])
    emb_name = data.get("person1", [])
    return ImageController.get_emb_names_for_recognition(persons,links,emb_name)


# =======================Shafia's Mobile side Requests========================================
@app.route('/add_mobile_image', methods=['POST'])
def add_mobile_image():
     try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        # image_path = os.path.join('.',ASSETS_FOLDER,  str(uuid.uuid4().hex) + '.jpg')
        # print(image_path)
        image = Image.open(io.BytesIO(file.read()))
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # image.save(image_path)
        temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(temp, format="JPEG")
        temp_path = temp.name
        temp.close()  # Close file so OpenCV can access it

        result = MobileSideController.add_mobile_image(temp_path)

        # Clean up manually
        os.unlink(temp_path)

        return result
     except Exception as exp:
        return jsonify({'error':str(exp)}), 500
     


@app.route('/get_mobile_person_groups', methods=['POST'])
def get_mobile_person_groups():
    try:
        # Ensure we have JSON data
        if not request.is_json:
            return jsonify({'error': 'Missing JSON in request'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Empty JSON data'}), 400
            
        # Get data with defaults
        persons = data.get("persons", [])
        links = data.get("links", [])
        image_persons = data.get("image_persons", [])
        image_ids = set(data.get("image_ids", []))
        
        # Debug logging
        print(f"Received data: persons={len(persons)}, links={len(links)}, "
              f"image_persons={len(image_persons)}, image_ids={len(image_ids)}")
        #MobileSideController ko bj rha ha list 4
        result = MobileSideController.get_person_groups_from_data(
            persons, links, image_persons, image_ids
        )
        return jsonify(result)
        
    except Exception as exp:
        # Log the full error
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(exp),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/get_unlinked_persons_by_id', methods=['POST'])
def get_unlinked_persons_by_id():
    try:
        # Ensure we have JSON data
        if not request.is_json:
            return jsonify({'error': 'Missing JSON in request'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Empty JSON data'}), 400
            
        # Get data with defaults
        personId = data.get("personId", None)
        persons = data.get("persons", [])
        links = data.get("links", [])
        
        # Debug logging
        print(f"Received data: personId={personId} persons={len(persons)}, links={len(links)}")
        
        result = MobileSideController.get_unlinked_persons_by_id(
            personId, persons, links
        )
        return jsonify(result)
        
    except Exception as exp:
        # Log the full error
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(exp),
            'traceback': traceback.format_exc()
        }), 500
    

@app.route('/get_unsync_images', methods=['POST'])
def get_unsync_images():

    # Ensure we have JSON data
    if not request.is_json:
        return jsonify({'error': 'Missing JSON in request'}), 400
            
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of image objects'}), 400
    ImageController.save_unsync_image_with_metadata(data)   
    return jsonify(MobileSideController.get_unsync_images())



@app.route('/health')
def health_check():
     return jsonify({"status": "healthy"}), 200

# only accept localhost
# if __name__ == '__main__':
#     app.run(debug=True)


# # Run on all addresses (0.0.0.0)
if __name__ == '__main__':
    # if not os.path.exists("temp"):
    #     os.makedirs("temp")
    app.run(host='0.0.0.0', port=5000, debug=True)
