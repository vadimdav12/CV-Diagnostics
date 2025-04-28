from app import db


class Parameter(db.Model):
    __tablename__ = "parameters"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    unit = db.Column(db.String(30))
    # использовать отношения, чтобы связать объекты без явного указания ID
    sensor_parameter = db.relationship("Sensor_parameter", backref="parameter", passive_deletes='RESTRICT')
    parameter_record = db.relationship("Sensor_Record", backref="parameter", passive_deletes='RESTRICT')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit
    }