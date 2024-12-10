from config import db
from Model.Image import Image
from Model.ImageEvent import ImageEvent


class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    
    images = db.relationship('Image', secondary='image_event', back_populates='events', lazy='dynamic')


    def __repr__(self):
        return f'<Event {self.name}>'