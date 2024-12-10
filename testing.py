# importing the cv2 library
import cv2
import os

# importing the required libraries
from flask import json
import numpy as np
from imgbeddings import imgbeddings
from PIL import Image
import pyodbc
import os

def getfaces():
    # Load the Haar cascade algorithm
    alg = "C:\\Users\\shafia2\\Downloads\\python-test\\haarcascade_frontalface_default.xml"
    haar_cascade = cv2.CascadeClassifier(alg)

    # Load the image path
    file_name = "C:\\Users\\shafia2\\Downloads\\python-test\\kids.jpeg"

    # Reading the image in grayscale mode (0 for grayscale)
    img = cv2.imread(file_name, 0)

    # Detecting faces in the image
    faces = haar_cascade.detectMultiScale(
        img, scaleFactor=1.05, minNeighbors=10, minSize=(100, 100)
    )

    # Create the directory for storing cropped faces if it doesn't exist
    output_dir = 'stored-faces'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop through each detected face and save the cropped image
    i = 0
    for x, y, w, h in faces:
        # Crop the face from the image
        cropped_image = img[y : y + h, x : x + w]
        
        # Save the cropped face to the specified folder
        target_file_name = os.path.join(output_dir, f'{i}.jpg')
        cv2.imwrite(target_file_name, cropped_image)
        i += 1

    print(f"Detected and saved {i} face(s).")

def embeddings():
    # Connecting to the database using pyodbc
    # conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-4S96KP6\\SQLEXPRESS;DATABASE=FypTask;UID=sa;PWD=12345'
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
    r'SERVER=WINDOWS-QIGEF94\SQLEXPRESS;'  # Replace with your SQL Server name
    'DATABASE=phototesting;'  # Replace with your database name
    'Trusted_Connection=yes;'
    )

    # Create a cursor object to execute SQL queries
    cur = conn.cursor()

    # Fetch all existing embeddings from the database
    cur.execute("SELECT embedding FROM pictures")
    existing_embeddings = [row[0] for row in cur.fetchall()]  # Create a list of existing embeddings

    # Loop through stored images
    for filename in os.listdir("stored-faces"):
        # Opening the image
        img = Image.open("stored-faces/" + filename)

        # Loading the imgbeddings (assuming the function exists)
        ibed = imgbeddings()

        # Calculating the embeddings
        embedding = ibed.to_embeddings(img)

        # Convert embedding to JSON
        embedding_data = json.dumps(embedding[0].tolist())

        # Check if the embedding exists using the == operator
        if embedding_data in existing_embeddings:
            print("Image already exists.")
        else:
            cur.execute("INSERT INTO pictures (filename, embedding) VALUES (?, ?)", (filename, embedding_data))
            print(f"Inserted {filename} into database.")

            # Commit the changes to the database
            conn.commit()

    # Close the connection
    conn.close()





def main():
    getfaces()
    embeddings()


if __name__ == "__main__":
    main()
