from config import db

class ImagePerson(db.Model):
    __tablename__ = 'image_person'
    
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)