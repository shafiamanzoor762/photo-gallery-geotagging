from config import db
from datetime import datetime

class ImageEventHistory(db.Model):
    __tablename__ = 'ImageEventHistory'

    sr_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    version_no = db.Column(db.Integer)
    is_Active = db.Column('is_active', db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: Relationships (if needed in your app)
    image = db.relationship('Image', backref='event_history', lazy='joined')
    event = db.relationship('Event', backref='image_history', lazy='joined')

    def to_dict(self):
        return {
            'sr_no': self.sr_no,
            'image_id': self.image_id,
            'event_id': self.event_id,
            'version_no': self.version_no,
            'is_Active': self.is_Active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<ImageEventHistory image_id={self.image_id}, event_id={self.event_id}, version={self.version_no}>'
