from config import db

class Image(db.Model):
    __tablename__ = 'image'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255), nullable=False)
    is_sync = db.Column(db.Boolean, nullable=False)
    capture_date = db.Column(db.Date)
    event_date = db.Column(db.Date)
    last_modified = db.Column(db.DateTime)
    hash = db.Column(db.String(255), unique=True, nullable=False)  # <-- Important

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    # is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    
    # New 'is_deleted' column
    is_deleted = db.Column(db.Boolean, default=False)  # Added 'is_deleted' field
    
    persons = db.relationship('Person', secondary='imagePerson', back_populates='images')
    events = db.relationship('Event', secondary='imageEvent', back_populates='images', lazy='dynamic')

    
    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'is_sync': self.is_sync,
            'capture_date': self.capture_date.strftime('%Y-%m-%d') if self.capture_date else None,
            'event_date': self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None,
            'location_id': self.location_id,
            'is_deleted':self.is_deleted
        }
    
    def __repr__(self):
        return f'<Image {self.path}>'