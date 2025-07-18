from config import db
from datetime import datetime

# Define the imageEventHistory association table
imageEventHistory = db.Table('imageEventHistory',
    db.Column('image_id', db.Integer, db.ForeignKey('ImageHistory.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)  # optional if used in query
)

class ImageHistory(db.Model):
    __tablename__ = 'ImageHistory'

    sr_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer)
    path = db.Column(db.String(255), nullable=False)
    is_sync = db.Column(db.Boolean)
    capture_date = db.Column(db.Date)
    event_date = db.Column(db.Date)
    last_modified = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    version_no = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    # is_Active = db.Column('is_active', db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relationship using existing 'imagePerson' table
    personhistory = db.relationship(
        'PersonHistory',
        secondary='imagePerson',
        primaryjoin='ImageHistory.id == imagePerson.c.image_id',
        secondaryjoin='PersonHistory.id == imagePerson.c.person_id',
        viewonly=True
    )

    # ✅ Relationship using defined 'imageEventHistory' table
    eventshistory = db.relationship(
    'Event',
    secondary=imageEventHistory,
    backref=db.backref('imagehistories', lazy='dynamic'),  # ✅ auto-creates reverse
    lazy='dynamic'
)




    def to_dict(self):
        return {
            'sr_no': self.sr_no,
            'id': self.id,
            'path': self.path,
            'is_sync': self.is_sync,
            'capture_date': self.capture_date.strftime('%Y-%m-%d') if self.capture_date else None,
            'event_date': self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d') if self.last_modified else None,
            'location_id': self.location_id,
            'version_no': self.version_no,
            'is_deleted': self.is_deleted,
            'hash': self.hash,
            'is_Active': self.is_Active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<ImageHistory {self.path} - Version {self.version_no}>'
