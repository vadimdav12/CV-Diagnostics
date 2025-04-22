from app import db


class Sensor_parameter(db.Model):
    __tablename__ = "sensor_parameter"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id"))
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameters.id"))