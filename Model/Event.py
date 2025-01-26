from config import db

class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    # event_date = db.Column(db.Date, nullable=False)  # New event_date column  ..... CONFIRM THAT THIS COLUMN WHERE EXISTS
    
    images = db.relationship('Image', secondary='imageEvent', back_populates='events', lazy='dynamic')
    
    def __repr__(self):
        return f'<Event {self.name}, Date: {self.event_date}>'
