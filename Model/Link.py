from config import db

class Link(db.Model):
    __tablename__ = 'link'
    
    person1_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False, primary_key=True)
    person2_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False, primary_key=True)
    