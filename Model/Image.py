# from flask_sqlalchemy import SQLAlchemy
from config import db
from Model.Person import Person
from Model.ImageEvent import ImageEvent
from Model.ImagePerson import ImagePerson

class Image(db.Model):
    __tablename__ = 'image'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255), nullable=False)
    isSync = db.Column(db.Boolean, nullable=False)
    captureDate = db.Column(db.Date)
    eventDate = db.Column(db.Date)
    lastModified = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    
    persons = db.relationship('Person', secondary='image_person', back_populates='images')
    events = db.relationship('Event', secondary='image_event', back_populates='images')

    def __repr__(self):
        return f'<Image {self.path}>'
    