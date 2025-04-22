from app import db


class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    data_source = db.Column(db.String(255))

    sensor_type_id = db.Column(db.Integer, db.ForeignKey("sensor_types.id", ondelete='RESTRICT'))
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id", ondelete='RESTRICT'))
    #использовать отношения, чтобы связать объекты без явного указания ID
    equipment = db.relationship("Equipment", backref="sensor")

    sensor_parameter = db.relationship("Sensor_parameter", backref="sensor")
    sensor_record = db.relationship("Sensor_Record", backref="sensor")


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'data_source': self.data_source,
            'sensor_type_id': self.sensor_type_id,
            'equipment_id': self.equipment_id
    }