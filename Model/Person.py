from config import db
from Model import ImagePerson

class Person(db.Model):
    __tablename__ = 'person'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255))
    gender = db.Column(db.String(1), nullable=False)  # Adding Gender column
    dob = db.Column(db.Date, nullable=True)  # 👈 New column for Date of Birth (nullable)
    age = db.Column(db.Integer,nullable=True)


    
    images = db.relationship('Image', secondary='imagePerson', back_populates='persons')

    def __repr__(self):
        return f'<Person {self.name}>'