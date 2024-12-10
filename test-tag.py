from PIL import Image
import piexif

# Open the image
img = Image.open("BabyGirl.jpeg")

# Create the custom EXIF data
exif_dict = {
    "0th": {
        piexif.ImageIFD.Artist: "John Doe",  # Name
        piexif.ImageIFD.ImageDescription: "Tech Conference",  # Event
        piexif.ImageIFD.Make: "New York",  # Location
    }
}

# Convert the EXIF dict to bytes
exif_bytes = piexif.dump(exif_dict)

# Save the image with the new EXIF data
img.save("image_with_metadata.jpg", "jpeg", exif=exif_bytes)

# Extract text 
exif_data = piexif.load("image_with_metadata.jpg")
name = exif_data["0th"].get(piexif.ImageIFD.Artist)
event = exif_data["0th"].get(piexif.ImageIFD.ImageDescription)
location = exif_data["0th"].get(piexif.ImageIFD.Make)

print(f"Name: {name}, Event: {event}, Location: {location}")
