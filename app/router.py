from flask import Flask, request, jsonify, send_file,make_response
from PIL import Image
import io
from io import BytesIO
import piexif
import json
from config import db,app
from sqlalchemy import text
import os

from Controller.PictureController import PictureController


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

@app.route('/recognize_person', methods=['GET'])
def recognize_person():
    return PictureController.recognize_person(request.get_json())


# only accept localhost
# if __name__ == '__main__':
#     app.run(debug=True)

# accept both local and ip Add
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
