from PIL import Image
import piexif,io
from io import BytesIO
from flask import jsonify, send_file

class TaggingController:

    @staticmethod
    def tagImage(file,tags):
        image = Image.open(io.BytesIO(file.read()))
        if image.mode == 'RGBA':
            image = image.convert('RGB')

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
    

    def extractImageTags(file):
    
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
        return jsonify(response)