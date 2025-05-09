from app import db


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    sensors = db.relationship("Sensor", backref="equipment", passive_deletes='RESTRICT')
    config = db.relationship("Configuration", backref="equipment", cascade='all, delete-orphan')
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
    }