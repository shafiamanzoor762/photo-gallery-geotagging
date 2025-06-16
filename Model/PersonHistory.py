from config import db
from datetime import datetime

class PersonHistory(db.Model):
    __tablename__ = 'PersonHistory'

    sr_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer)  # Original person ID
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    gender = db.Column(db.String(1))  # 'M', 'F', 'U' — enforced by a CHECK constraint in SQL
    dob = db.Column(db.Date, nullable=True)  # 👈 New column for Date of Birth (nullable)
    age = db.Column(db.Integer,nullable=True)
    version_no = db.Column(db.Integer)
    is_Active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'sr_no': self.sr_no,
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'gender': self.gender,
            'version_no': self.version_no,
            'is_Active': self.is_Active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<PersonHistory id={self.id}, version={self.version_no}, name={self.name}>'
