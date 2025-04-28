from app import db


class Sensor_type(db.Model):
    __tablename__ = "sensor_types"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    sensors= db.relationship("Sensor", backref="sensor_type", passive_deletes='RESTRICT')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
    }