from config import db

class Person(db.Model):
    __tablename__ = 'person'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255))
    
    images = db.relationship('Image', secondary='image_person', back_populates='persons')

    def __repr__(self):
        return f'<Person {self.name}>'