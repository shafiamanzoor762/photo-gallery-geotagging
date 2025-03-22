from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import the text function

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Configure your database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:12345@DESKTOP-4S96KP6\SQLEXPRESS/PhotoGallery1?driver=ODBC+Driver+17+for+SQL+Server'


# Don't Distrub ---Shafia's Database Connection String
# Configure your database URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:123@WINDOWS-R5NK4VK\SQLEXPRESS/PhotoGallery?driver=ODBC+Driver+17+for+SQL+Server'

#aimen db connection string 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:123@DESKTOP-R50Q2I1\\SQLEXPRESS/PhotoGallery?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&autocommit=True'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
