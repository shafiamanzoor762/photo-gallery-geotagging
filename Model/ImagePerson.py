from config import db
from Model import Person
class ImagePerson(db.Model):
    __tablename__ = 'imagePerson'
    
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)