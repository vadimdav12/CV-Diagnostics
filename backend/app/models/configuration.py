from app import db
from sqlalchemy.dialects.postgresql import JSONB


class Configuration(db.Model):
    __tablename__ = 'configurations'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    config = db.Column(JSONB, nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'equipment_id': self.equipment_id,
            'config': self.config,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }