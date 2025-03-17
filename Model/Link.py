from config import db

class Link(db.Model):
    __tablename__ = 'link'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person1_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    person2_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    
    person1 = db.relationship('Person', foreign_keys=[person1_id], backref='linked_as_person1')
    person2 = db.relationship('Person', foreign_keys=[person2_id], backref='linked_as_person2')
    
    def __repr__(self):
        return f'<Link {self.person1_id} - {self.person2_id}>'