# # importing the cv2 library
# import cv2
# import os

# # importing the required libraries
# from flask import json
# import numpy as np
# from imgbeddings import imgbeddings
# from PIL import Image
# import pyodbc
# import os

# def getfaces():
#     # Load the Haar cascade algorithm
#     alg = "C:\\Users\\shafia2\\Downloads\\python-test\\haarcascade_frontalface_default.xml"
#     haar_cascade = cv2.CascadeClassifier(alg)

#     # Load the image path
#     file_name = "C:\\Users\\shafia2\\Downloads\\python-test\\kids.jpeg"

#     # Reading the image in grayscale mode (0 for grayscale)
#     img = cv2.imread(file_name, 0)

#     # Detecting faces in the image
#     faces = haar_cascade.detectMultiScale(
#         img, scaleFactor=1.05, minNeighbors=10, minSize=(100, 100)
#     )

#     # Create the directory for storing cropped faces if it doesn't exist
#     output_dir = 'stored-faces'
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Loop through each detected face and save the cropped image
#     i = 0
#     for x, y, w, h in faces:
#         # Crop the face from the image
#         cropped_image = img[y : y + h, x : x + w]
        
#         # Save the cropped face to the specified folder
#         target_file_name = os.path.join(output_dir, f'{i}.jpg')
#         cv2.imwrite(target_file_name, cropped_image)
#         i += 1

#     print(f"Detected and saved {i} face(s).")

# def embeddings():
#     # Connecting to the database using pyodbc
#     # conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-4S96KP6\\SQLEXPRESS;DATABASE=FypTask;UID=sa;PWD=12345'
#     conn = pyodbc.connect(
#         'DRIVER={SQL Server};'
#     r'SERVER=WINDOWS-QIGEF94\SQLEXPRESS;'  # Replace with your SQL Server name
#     'DATABASE=phototesting;'  # Replace with your database name
#     'Trusted_Connection=yes;'
#     )

#     # Create a cursor object to execute SQL queries
#     cur = conn.cursor()

#     # Fetch all existing embeddings from the database
#     cur.execute("SELECT embedding FROM pictures")
#     existing_embeddings = [row[0] for row in cur.fetchall()]  # Create a list of existing embeddings

#     # Loop through stored images
#     for filename in os.listdir("stored-faces"):
#         # Opening the image
#         img = Image.open("stored-faces/" + filename)

#         # Loading the imgbeddings (assuming the function exists)
#         ibed = imgbeddings()

#         # Calculating the embeddings
#         embedding = ibed.to_embeddings(img)

#         # Convert embedding to JSON
#         embedding_data = json.dumps(embedding[0].tolist())

#         # Check if the embedding exists using the == operator
#         if embedding_data in existing_embeddings:
#             print("Image already exists.")
#         else:
#             cur.execute("INSERT INTO pictures (filename, embedding) VALUES (?, ?)", (filename, embedding_data))
#             print(f"Inserted {filename} into database.")

#             # Commit the changes to the database
#             conn.commit()

#     # Close the connection
#     conn.close()





# def main():
#     getfaces()
#     embeddings()


# if __name__ == "__main__":
#     main()



# ############################

import cv2

# loading the haar case algorithm file into alg variable
alg = "haarcascade_frontalface_default.xml"
# passing the algorithm to OpenCV
haar_cascade = cv2.CascadeClassifier(alg)
# loading the image path into file_name variable - replace <INSERT YOUR IMAGE NAME HERE> with the path to your image
file_name = "kids.jpeg"
# reading the image
img = cv2.imread(file_name, 0)
# creating a black and white version of the image
gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
# detecting the faces
faces = haar_cascade.detectMultiScale(
    gray_img, scaleFactor=1.05, minNeighbors=13, minSize=(100, 100)
)

i = 8
# for each face detected
for x, y, w, h in faces:
    # crop the image to select only the face
    cropped_image = img[y : y + h, x : x + w]
    # loading the target image path into target_file_name variable  - replace <INSERT YOUR TARGET IMAGE NAME HERE> with the path to your target image
    target_file_name = 'stored-faces/' + str(i) + '.jpg'
    cv2.imwrite(
        target_file_name,
        cropped_image,
    )
    i = i + 1




# ###########################

# import numpy as np
# from imgbeddings import imgbeddings
# from PIL import Image
# import pyodbc
# import os

# # Set up the connection to Microsoft SQL Server
# # Update with your SQL Server details (server name, database, username, password)
# conn = pyodbc.connect(    'DRIVER={SQL Server};'
#     r'SERVER=WINDOWS-QIGEF94\SQLEXPRESS;'  # Replace with your SQL Server name
#     'DATABASE=phototesting;'  # Replace with your database name
#     'Trusted_Connection=yes;' )

# # Create a cursor object
# cur = conn.cursor()

# # Loop through the images in the "stored-faces" folder and insert into SQL Server
# for filename in os.listdir("stored-faces"):
#     # Open the image
#     img = Image.open("stored-faces/" + filename)
    
#     # Load the imgbeddings
#     ibed = imgbeddings()
    
#     # Calculate the embeddings
#     embedding = ibed.to_embeddings(img)
    
#     # Convert the embedding array to a string (SQL Server does not support array types)
#     embedding_str = ",".join(map(str, embedding[0].tolist()))
    
#     # Insert the data into the pictures table (modify the table schema if necessary)
#     cur.execute("INSERT INTO pictures (filename, embedding) VALUES (?, ?)", (filename, embedding_str))
#     print(f"Inserted: {filename}")

# # Commit the transaction
# conn.commit()

# # Load the face image for comparison
# file_name = "kids.jpg"  # Replace <INSERT YOUR FACE FILE NAME> with the path to your image
# img = Image.open(file_name)

# # Load the imgbeddings and calculate the embedding
# ibed = imgbeddings()
# embedding = ibed.to_embeddings(img)

# # Convert the embedding array to a string
# embedding_str = ",".join(map(str, embedding[0].tolist()))


# from IPython.display import Image, display
# # Query to find the closest match using embeddings (SQL Server doesn't have native vector similarity search, so this is just a placeholder)
# cur.execute("""
#     SELECT TOP 1 filename FROM pictures
#     ORDER BY CAST(embedding AS VARCHAR(MAX)) <-> CAST(? AS VARCHAR(MAX));
# """, (embedding_str,))

# # Fetch and display the result
# row = cur.fetchone()
# if row:
#     # Display the closest matching image
#     display(Image(filename="stored-faces/" + row[0]))

# # Close the cursor and connection
# cur.close()
# conn.close()


















# #################################

# # importing the required libraries
# import numpy as np
# from imgbeddings import imgbeddings
# from PIL import Image
# import psycopg2
# import os

# # connecting to the database - replace the SERVICE URI with the service URI
# conn = psycopg2.connect("<SERVICE_URI>")

# for filename in os.listdir("stored-faces"):
#     # opening the image
#     img = Image.open("stored-faces/" + filename)
#     # loading the `imgbeddings`
#     ibed = imgbeddings()
#     # calculating the embeddings
#     embedding = ibed.to_embeddings(img)
#     cur = conn.cursor()
#     cur.execute("INSERT INTO pictures values (%s,%s)", (filename, embedding[0].tolist()))
#     print(filename)
# conn.commit()


# # loading the face image path into file_name variable
# file_name = "solo-image.png"  # replace <INSERT YOUR FACE FILE NAME> with the path to your image
# # opening the image
# img = Image.open(file_name)
# # loading the `imgbeddings`
# ibed = imgbeddings()
# # calculating the embeddings
# embedding = ibed.to_embeddings(img)


# from IPython.display import Image, display

# cur = conn.cursor()
# string_representation = "["+ ",".join(str(x) for x in embedding[0].tolist()) +"]"
# cur.execute("SELECT * FROM pictures ORDER BY embedding <-> %s LIMIT 1;", (string_representation,))
# rows = cur.fetchall()
# for row in rows:
#     display(Image(filename="stored-faces/"+row[0]))
# cur.close()

# ###########################

import pyodbc
import numpy as np
from imgbeddings import imgbeddings
from PIL import Image

# Define your connection string
conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=WINDOWS-QIGEF94\\SQLEXPRESS;'
    'DATABASE=phototesting;'
    'Trusted_Connection=yes;'
)

# Connecting to the SQL Server
conn = pyodbc.connect(conn_str)
cur = conn.cursor()

# Function to calculate Euclidean distance between two vectors
def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

# Get the embedding for the image you want to search for
file_name = "kids.jpeg"
img = Image.open(file_name)
ibed = imgbeddings()
embedding = ibed.to_embeddings(img)[0].tolist()

# Fetch all embeddings from the database
cur.execute("SELECT filename, embedding FROM pictures")
rows = cur.fetchall()

closest_filename = None
closest_distance = float('inf')

# Compare the embedding with all stored embeddings
for row in rows:
    filename = row[0]
    stored_embedding = eval(row[1])  # Convert string representation back to a list
    distance = euclidean_distance(embedding, stored_embedding)

    if distance < closest_distance:
        closest_distance = distance
        closest_filename = filename

# Print the closest match
if closest_filename:
    print(f"Closest match: {closest_filename}, Distance: {closest_distance}")
else:
    print("No match found.")

cur.close()
conn.close()


# #############################

# import pyodbc
# import numpy as np
# from imgbeddings import imgbeddings
# from PIL import Image

# # Define your connection string (no change needed here)
# conn_str = (
#     'DRIVER={SQL Server};'
#     r'SERVER=WINDOWS-QIGEF94\SQLEXPRESS;'  # Ensure raw string to handle backslashes
#     'DATABASE=phototesting;'
#     'Trusted_Connection=yes;'
# )

# # Connecting to the SQL Server
# conn = pyodbc.connect(conn_str)
# cur = conn.cursor()

# # Function to calculate Euclidean distance between two vectors
# def euclidean_distance(vector1, vector2):
#     return np.linalg.norm(np.array(vector1) - np.array(vector2))

# # Get the embedding for the image you want to search for
# file_name = "kids.jpeg"
# img = Image.open(file_name)
# ibed = imgbeddings()
# embedding = ibed.to_embeddings(img)[0].tolist()

# # Fetch all embeddings from the database
# cur.execute("SELECT filename, embedding FROM pictures")
# rows = cur.fetchall()

# closest_filename = None
# closest_distance = float('inf')

# # Compare the embedding with all stored embeddings
# for row in rows:
#     filename = row[0]
#     stored_embedding = eval(row[1])  # Convert string representation back to a list
#     distance = euclidean_distance(embedding, stored_embedding)

#     if distance < closest_distance:
#         closest_distance = distance
#         closest_filename = filename

# # Print the closest match
# if closest_filename:
#     print(f"Closest match: {closest_filename}, Distance: {closest_distance}")
# else:
#     print("No match found.")

# cur.close()
# conn.close()


# #########################################



# # Importing the required libraries
# import numpy as np
# from imgbeddings import imgbeddings
# from PIL import Image
# import pyodbc  # SQL Server connection
# import os


# # Connecting to SQL Server
# conn_str = (
#     'DRIVER={SQL Server};'
#     r'SERVER=WINDOWS-QIGEF94\SQLEXPRESS;'  # Replace with your SQL Server name
#     'DATABASE=phototesting;'  # Replace with your database name
#     'Trusted_Connection=yes;'  # Or provide username and password if not using Windows Authentication
# )
# conn = pyodbc.connect(conn_str)

# # Inserting embeddings into the database
# for filename in os.listdir("stored-faces"):
#     # Opening the image
#     img = Image.open("stored-faces/" + filename)
    
#     # Loading the `imgbeddings`
#     ibed = imgbeddings()
    
#     # Calculating the embeddings
#     embedding = ibed.to_embeddings(img)[0].tolist()
    
#     # Convert embedding list to string for SQL insertion
#     embedding_str = str(embedding)
    
#     cur = conn.cursor()
    
#     # Insert filename and embedding into the pictures table
#     cur.execute("INSERT INTO pictures (filename, embedding) VALUES (?, ?)", (filename, embedding_str))
#     print(f"Inserted: {filename}")
    
# conn.commit()

# # Loading the face image path into file_name variable
# file_name = "BabyGirl.jpeg"  # Replace with your image file name
# # Opening the image
# img = Image.open(file_name)
# # Loading the `imgbeddings`
# ibed = imgbeddings()
# # Calculating the embeddings
# embedding = ibed.to_embeddings(img)[0].tolist()

# # Convert the embedding to string format for comparison
# string_representation = str(embedding)

# from IPython.display import Image, display
# # Query to find the closest match using SQL Server's built-in functionality (Note: No <-> operator in SQL Server)
# cur = conn.cursor()

# # In SQL Server, the <-> (similarity operator) is not available, so you need to fetch all embeddings and calculate distance manually in Python
# cur.execute("SELECT filename, embedding FROM pictures")
# rows = cur.fetchall()

# # Function to calculate Euclidean distance between two vectors
# def euclidean_distance(vector1, vector2):
#     return np.linalg.norm(np.array(vector1) - np.array(vector2))

# closest_filename = None
# closest_distance = float('inf')

# # Compare the embedding with all stored embeddings
# for row in rows:
#     filename = row[0]
#     stored_embedding = eval(row[1])  # Convert string representation back to a list
#     distance = euclidean_distance(embedding, stored_embedding)

#     if distance < closest_distance:
#         closest_distance = distance
#         closest_filename = filename

# # Display the closest match
# if closest_filename:
#     print(f"Closest match: {closest_filename}, Distance: {closest_distance}")
#     display(Image(filename="stored-faces/" + closest_filename))
# else:
#     print("No match found.")

# cur.close()
# conn.close()


