from flask import Flask, request, jsonify, send_file,make_response
from PIL import Image
import io
from io import BytesIO
import piexif
import json
from config import db,app
import os
import base64

from Controller.PictureController import PictureController
from Controller.EventController import EventController
from Controller.ImageController import ImageController

@app.route('/tagimage', methods = ['POST'])
def tagImage():
    try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        image = Image.open(io.BytesIO(file.read()))
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        tags_str = request.form.get('tags')
        if not tags_str:
            return jsonify({'error': 'Tags not found'}), 400
        
        tags=json.loads(tags_str)

        exif_dict = {
            "0th": {
                piexif.ImageIFD.Artist: tags.get('name','No Name'),  # Name
                piexif.ImageIFD.ImageDescription: tags.get('event','No Event'),  # Event
                piexif.ImageIFD.Make: tags.get('location','No Location'),  # Location
            }
        }
        exif_bytes = piexif.dump(exif_dict)

        img_io = BytesIO()
        image.save(img_io, format="JPEG", exif=exif_bytes)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg', download_name='image_with_metadata.jpg')
    
    except Exception as exp:
        return jsonify({'error':str(exp)}), 500

@app.route('/extractImageTags', methods = ['POST'])
def extractImageTags():
    try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        image = Image.open(io.BytesIO(file.read()))
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        exif_data = piexif.load(image.info.get('exif', b""))
        name = exif_data["0th"].get(piexif.ImageIFD.Artist, b'').decode('utf-8', errors='ignore')
        event = exif_data["0th"].get(piexif.ImageIFD.ImageDescription, b'').decode('utf-8', errors='ignore')
        location = exif_data["0th"].get(piexif.ImageIFD.Make, b'').decode('utf-8', errors='ignore')
        print(f"Name: {name}, Event: {event}, Location: {location}")
        response={
            'name': name if name else 'Unknown',
            'event': event if event else 'no event',
            'location': location if location else 'no location'
        }
        return make_response(jsonify(response), 201)
        
    except Exception as exp:
        return jsonify({'error':str(exp)}), 500

ASSETS_FOLDER = 'Assets'  # Specify your uploads folder
if not os.path.exists(ASSETS_FOLDER):
    os.makedirs(ASSETS_FOLDER)

@app.route('/extract_face', methods=['POST'])
def extract_face():
     try:
        if 'file' not in request.files:
            return jsonify({'error':'file not attatched'}), 404
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'filename is empty'}), 404
        
        image_path = os.path.join('.',ASSETS_FOLDER, file.filename)
        print(image_path)
        image = Image.open(io.BytesIO(file.read()))
        image.save(image_path)
        return PictureController.extract_face(image_path)
     except Exception as exp:
        return jsonify({'error':str(exp)}), 500

# @app.route('/recognize_person', methods = ['GET'])
# def recognize_person():
#     return PictureController.recognize_person(request.get_json())

@app.route('/recognize_person', methods=['GET'])
def recognize_person():
    # Get query parameters from the GET request
    image_path = request.args.get('image_path')
    person_name = request.args.get('name', None)

    if not image_path:
        return make_response(jsonify({'error': 'Missing required parameters'}), 400)

    # Call the method from the PictureController class
    return PictureController.recognize_person(image_path, person_name)

# --------------------------IMAGE---------------------------------

@app.route('/group_by_date',methods = ['GET'])
def group_by_date():
    return ImageController.group_by_date()

@app.route('/group_by_location',methods = ['GET'])
def group_by_location():
    return ImageController.group_by_location()

# -----------------------------------------------------------

@app.route('/images', methods=['POST'])
def add_image():
    data = request.get_json()
    if 'path' not in data or 'isSync' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    return ImageController.add_image(data)


@app.route('/images/<int:image_id>', methods=['PUT'])
def edit_image(image_id):
    data = request.get_json()
    return ImageController.edit_image(image_id, data)

# Get details of a specific Image (Read)
@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    return ImageController.get_image_details(image_id)

# Delete an Image (Delete)
@app.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    return ImageController.delete_image(image_id)

# --------------------------EVENT---------------------------------
@app.route('/fetch_events', methods = ['GET'])
def fetch_events():
    print('am here')
    return ImageController.fetch_all_events()

#add a new event 
@app.route('/addnewevent', methods=['POST'])
def addnewevent():
    print("am in addnew event method")
    if request.is_json:
           
           json_data = request.get_json()
           
           if 'name' not in json_data:
             return {"error": "Missing 'name' in JSON data"}, 200
           print("Received JSON data:", json_data)
    
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

#sorting of events for Dropdown
@app.route('/sortevents', methods=['POST'])
def sortevents():
    
    if request.is_json:
           
           json_data = request.get_json()
           
           if 'name' not in json_data :
             return {"error": "Missing 'name' in JSON data"}, 200
           print("Received JSON data:", json_data)
    
    return EventController.sortevents(json_data)


# ==================TEMPORARY====================


@app.route('/save_record', methods=['POST'])
def save_record():
    data = request.get_json()

    if not data or 'directory_path' not in data:
        return jsonify({'error': 'Directory path is required'}), 400
    
    directory_path = data['directory_path']

    if not os.path.isdir(directory_path):
        return jsonify({'error': 'Provided path is not a valid directory'}), 400

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing {filename}...")

            result = PictureController.extract_face(file_path)
            print(result)

    return jsonify({'status': 'Processing complete'}), 200

# ==================GROUPBY PERSON UNKNOWN CLUSTERS====================
@app.route('/recognize_person_bulk', methods=['POST'])
def recognize_person_bulk():
    try:
        if request.content_length:
          app.logger.info(f"Request size: {request.content_length} bytes")
        files = request.files.getlist("images")
        print(f"Received files: {[file.filename for file in files]}")
        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        results = []
        for file in files:
            try:
                file_data = file.read()
                file_base64 = base64.b64encode(file_data).decode("utf-8")
                print(f"Base64 encoding for {file.filename}: {file_base64[:30]}...")
                filename = file.filename
                temp_path = os.path.join("temp", filename)

                with open(temp_path, "wb") as temp_file:
                    temp_file.write(file_data)

                try:
                    recognition_response = PictureController.recognize_person(temp_path)
                    print(f"Recognition response for {filename}: {recognition_response}")

                    if recognition_response.get('status_code') == 400:
                        print(f"Error in recognition for {filename}: {recognition_response['error']}")
                        continue

                    recognition_results = recognition_response.get('results', [])
                    for result in recognition_results:
                        result["original_image"] = file_base64 if file_base64 else None
                        result["image_name"] = filename

                    results.extend(recognition_results)
                finally:
                    os.remove(temp_path)
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")


        grouped_results = {}
        for result in results:
          file_name = result.get("file", "").split("/")[-1]
          name = result.get("name", "unknown")

          key = f"{file_name}_{name}"

          if key not in grouped_results:
            grouped_results[key] = []

          grouped_results[key].append(result)


        return jsonify(grouped_results)

    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500




# only accept localhost
# if __name__ == '__main__':
#     app.run(debug=True)


# accept both local and ip Add
if __name__ == '__main__':
    if not os.path.exists("temp"):
        os.makedirs("temp")
    app.run(host='0.0.0.0', port=5000, debug=True)

