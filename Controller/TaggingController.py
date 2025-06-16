from PIL import Image
import piexif,io
import piexif.helper
import json
from io import BytesIO
from flask import jsonify, send_file

class TaggingController:

    # @staticmethod
    # def tagImage(file,tags):
    #     image = Image.open(io.BytesIO(file.read()))
    #     if image.mode == 'RGBA':
    #         image = image.convert('RGB')

    #     exif_dict = {
    #         "0th": {
    #             piexif.ImageIFD.Artist: tags.get('name','No Name'),  # Name
    #             piexif.ImageIFD.ImageDescription: tags.get('event','No Event'),  # Event
    #             piexif.ImageIFD.Make: tags.get('location','No Location'),  # Location
    #         }
    #     }
    #     exif_bytes = piexif.dump(exif_dict)

    #     img_io = BytesIO()
    #     image.save(img_io, format="JPEG", exif=exif_bytes)
    #     img_io.seek(0)

    #     return send_file(img_io, mimetype='image/jpeg', download_name='image_with_metadata1.jpg')



    
    # @staticmethod
    # def extractImageTags(file):
    
    #     image = Image.open(io.BytesIO(file.read()))
    #     if image.mode == 'RGBA':
    #         image = image.convert('RGB')

    #     exif_data = piexif.load(image.info.get('exif', b""))
    #     name = exif_data["0th"].get(piexif.ImageIFD.Artist, b'').decode('utf-8', errors='ignore')
    #     event = exif_data["0th"].get(piexif.ImageIFD.ImageDescription, b'').decode('utf-8', errors='ignore')
    #     location = exif_data["0th"].get(piexif.ImageIFD.Make, b'').decode('utf-8', errors='ignore')
    #     print(f"Name: {name}, Event: {event}, Location: {location}")
    #     response={
    #         'name': name if name else 'Unknown',
    #         'event': event if event else 'no event',
    #         'location': location if location else 'no location'
    #     }
    #     return jsonify(response)


# ======================================================

# http://127.0.0.1:5000/tagimage

# form-data:
# file: <file object>
# tags:
# {
#     "persons": {
#         "1": {
#             "name": "Aliya",
#             "gender": "F",
#             "path": "cropped/aliya.jpg"
#         },
#         "2": {
#             "name": "Ali",
#             "gender": "M",
#             "path": "cropped/ali.jpg"
#         }
#     },
#     "event": ["Convocation","Graduation"],
#     "location": "Islamabad"
#    "event_date": "2023-10-01"
# }
 

    @staticmethod
    def tagImage(file, tags):
      try:
        image = Image.open(BytesIO(file.read()))
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Serialize metadata with UTF-16 encoding (EXIF standard)
        metadata_json = json.dumps(tags, ensure_ascii=False)
        user_comment = piexif.helper.UserComment.dump(
            metadata_json,
            encoding="unicode"
        )

        exif_dict = {
            "Exif": {
                piexif.ExifIFD.UserComment: user_comment
            }
        }

        exif_bytes = piexif.dump(exif_dict)

        img_io = BytesIO()
        image.save(img_io, format="JPEG", exif=exif_bytes)
        img_io.seek(0)

        # Return raw image bytes for internal use
        return img_io

      except Exception as e:
        print(f"Tagging error: {str(e)}")
        return None

      

# http://127.0.0.1:5000//extractImageTags

# form-data:
# file: <file object>

    @staticmethod
    def extractImageTags(file):
      try:
        image = Image.open(BytesIO(file.read()))
        exif_data = piexif.load(image.info.get('exif', b''))
        
        # Initialize response with correct field names
        response = {
            "persons": {},
            "event": "",  # Changed from "events"
            "location": "",
            "event_date": ""
        }

        if "Exif" in exif_data:
            user_comment = exif_data["Exif"].get(piexif.ExifIFD.UserComment, b'')
            if user_comment:
                try:
                    # Decode with proper EXIF UTF-16 handling
                    metadata_str = piexif.helper.UserComment.load(user_comment)
                    metadata = json.loads(metadata_str)
                    
                    # Map fields correctly
                    response.update({
                        "persons": metadata.get("persons", {}),
                        "event": metadata.get("event", ""),
                        "location": metadata.get("location", ""),
                        "event_date": metadata.get("event_date", "")
                    })
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error: {str(e)}")
                    response["error"] = "Malformed metadata"

        print(f"Extracted Metadata: {json.dumps(response, indent=2)}")
        return jsonify(response)

      except Exception as e:
        print(f"Error extracting metadata: {str(e)}")
        return jsonify({
            "error": "Metadata extraction failed",
            "details": str(e)
        }), 500