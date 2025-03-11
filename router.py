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
    # Get query parameters from the GET request
    image_path = request.args.get('image_path')
    person_name = request.args.get('name', None)

    if not image_path:
        return make_response(jsonify({'error': 'Missing required parameters'}), 400)

    # Call the method from the PictureController class
    return PictureController.recognize_person(image_path, person_name)


@app.route('/group_by_person', methods=['GET'])
def group_by_person():
    return PictureController.group_by_person()

        

# --------------------------IMAGE---------------------------------

@app.route('/edit_image', methods=['POST'])
def edit_Image():
    return ImageController.edit_image_data()

@app.route('/searching_on_image', methods=['POST'])
def searching():
    return ImageController.searching_on_image()

@app.route('/Load_images', methods=['POST'])
def Load_images():
    return ImageController.Load_images()
@app.route('/group_by_date',methods = ['GET'])
def group_by_date():
    return ImageController.group_by_date()


@app.route('/unedited-images', methods=['GET'])
def get_unedited_images_route():
    return ImageController.get_unedited_images()


# -----------------------------------------------------------
#done
@app.route('/add_image', methods=['POST'])
def add_image():
    data = request.get_json()
    if 'path' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    return ImageController.add_image(data)


# Get details of a specific Image (Read)
@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    return ImageController.get_image_details(image_id)

@app.route('/image_complete_details/<int:image_id>', methods=['GET'])
def get_image_complete_details(image_id):
    return ImageController.get_image_complete_details(image_id)

# Delete an Image (Delete)
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
             return {"error": "Missing 'name' in JSON data"}, 200
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


# [GET] http://127.0.0.1:5000/images/2


@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    try:
        
        return send_from_directory(ASSETS_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404
    
    ######remove Metadata####################
@app.route('/remove_metadata', methods=['POST'])
def remove_metadata():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'File not attached'}), 400

        file = request.files['file']
        
        # Open the image file
        image = Image.open(io.BytesIO(file.read()))

        # Create a new image to strip metadata
        img_io = io.BytesIO()

        # Strip metadata by saving without Exif (using 'quality' argument for JPG)
        image.save(img_io, format="JPEG", quality=95)  # JPEG without metadata
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg', download_name='image_without_metadata.jpg')

    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

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
        file_paths = os.path.join(ASSETS_FOLDER, file.filename)
        file_path="images/"+file.filename
        with open(file_paths, "wb") as f:
            f.write(file_bytes)
        
        ImageController.add_image({"path": file_path})
        return jsonify({"message": "File uploaded successfully", "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# only accept localhost
if __name__ == '__main__':
    app.run(debug=True)



# if __name__ == '__main__':
#     if not os.path.exists("temp"):
#         os.makedirs("temp")
#     app.run(host='0.0.0.0', port=5000, debug=True)

