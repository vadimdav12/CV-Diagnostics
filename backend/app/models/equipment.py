from app import db


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
    }