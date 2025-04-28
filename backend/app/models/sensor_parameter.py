from app import db


class Sensor_parameter(db.Model):
    __tablename__ = "sensor_parameter"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete='CASCADE'))
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameters.id", ondelete='RESTRICT'))
    key = db.Column(db.String(30))

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'parameter_id': self.parameter_id,
            'key': self.key
    }