from flask import Flask, request, jsonify, send_file,make_response, send_from_directory
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
from Controller.LocationController import LocationController

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

        return send_file(img_io, mimetype='image/jpeg', download_name='image_with_metadata1.jpg')
    
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

ASSETS_FOLDER = 'Assets'  
if not os.path.exists(ASSETS_FOLDER):
    os.makedirs(ASSETS_FOLDER)
# =================== PICTURE CONTROLLER ==============

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


@app.route('/recognize_person', methods=['GET'])
def recognize_person():
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

        name = request.form.get('name')
        if not name:
            return jsonify({'error': 'Name not found'}), 400

        # Call the method from the PictureController class
        return PictureController.recognize_person(image_path, name)
    except Exception as exp:
        return jsonify({'error':str(exp)}), 500

@app.route('/group_by_person', methods=['GET'])
def group_by_person():
    return PictureController.group_by_person()

        

# --------------------------IMAGE---------------------------------

@app.route('/edit_image', methods=['PUT'])
def edit_Image():
    return ImageController.edit_image_data()

@app.route('/searching_on_image', methods=['GET'])
def searching():
    return ImageController.searching_on_image()

@app.route('/group_by_date',methods = ['GET'])
def group_by_date():
    return ImageController.group_by_date()


# -----------------------------------------------------------

@app.route('/add_image', methods=['POST'])
def add_image():
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

        metadata = request.form.get('metadata')
        data=""
        if metadata:
            data=json.loads(metadata)
        
        return ImageController.add_image(image_path,data)
    except Exception as exp:
        return jsonify({'error':str(exp)}), 500



@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    return ImageController.get_image_details(image_id)

@app.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    return ImageController.delete_image(image_id)

@app.route('/sync_images', methods=['GET'])
def sync_images():
    return ImageController.sync_images()

# --------------------------EVENT---------------------------------
@app.route('/fetch_events', methods = ['GET'])
def fetch_events():
    return EventController.fetch_all_events()



# [POST] http://127.0.0.1:5000/addnewevent
# BODY - raw (JSON)
# {
#     "name": "New Year Party",
  
# }
#add a new event 
@app.route('/addnewevent', methods=['POST'])
def addnewevent():
    if request.is_json:
           
           json_data = request.get_json()
           
           if 'name' not in json_data:
             return {"error": "Missing 'name' in JSON data"}, 200
    
    return EventController.addnewevent(json_data)



# {
#     "id":"5",
#     "names":"Birthday Party, abc"
# }
  

#add events to an image 
@app.route('/addevents', methods=['POST'])
def addevents():
    
    if request.is_json:
           
           json_data = request.get_json()
           
           if 'id' not in json_data or 'names' not in json_data:
             return {"error": "Missing 'name' in JSON data"}, 200
           print("Received JSON data:", json_data)
    
    return EventController.addevents(json_data)

#sorting of events for making folders
@app.route('/groupbyevents', methods=['GET'])
def sortevents():
    
    
    return EventController.groupbyevents()

# ================Location=================

@app.route('/get_loc_from_lat_lon' , methods=['GET'])
def getlocation_from_lat_lon():
    

    data = request.get_json()
    latitude =data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and Longitude are required"}), 400
    else:
        return LocationController.get_location_from_lat_lon(latitude,longitude)

# add location
@app.route('/addLocation' , methods=['POST'])
def addLocation():
    

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


# [GET] http://127.0.0.1:5000/images/2

# Route to serve images
@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    try:
        # Serve the image from the Assets folder
        return send_from_directory(ASSETS_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404

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

        file_path = os.path.join(ASSETS_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        ImageController.add_image({"path": file_path})
        return jsonify({"message": "File uploaded successfully", "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# only accept localhost
if __name__ == '__main__':
    app.run(debug=True)


# accept both local and ip Add
# if __name__ == '__main__':
#     if not os.path.exists("temp"):
#         os.makedirs("temp")
#     app.run(host='0.0.0.0', port=5000, debug=True)

