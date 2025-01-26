from config import db

class ImageEvent(db.Model):
    __tablename__ = 'imageEvent'
    
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)