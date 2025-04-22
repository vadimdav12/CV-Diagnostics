from datetime import datetime

from app import db


class Sensor_Record(db.Model):
    __tablename__ = "sensor_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    value = db.Column(db.DECIMAL(precision=10, scale=2))

    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id"))
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameters.id"))
    #использовать отношения, чтобы связать объекты без явного указания ID
    # sensors = db.relationship("Sensor", backref="sensor")
    # parameters = db.relationship("Parameter", backref="parameter")