from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    evaluations = db.relationship('Evaluation', backref='patient', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Avaliações
    session_rating = db.Column(db.Integer)
    doctor_rating = db.Column(db.Integer)
    nurse_rating = db.Column(db.Integer)
    technician_rating = db.Column(db.Integer)
    food_rating = db.Column(db.Integer)
    cleaning_rating = db.Column(db.Integer)
    transport_rating = db.Column(db.Integer)
    
    # Profissionais
    doctor_name = db.Column(db.String(100))
    nurse_name = db.Column(db.String(100))
    technician_name = db.Column(db.String(100))
    
    # Comentários
    comments = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name,
            'session_date': self.session_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'ratings': {
                'session': self.session_rating,
                'doctor': self.doctor_rating,
                'nurse': self.nurse_rating,
                'technician': self.technician_rating,
                'food': self.food_rating,
                'cleaning': self.cleaning_rating,
                'transport': self.transport_rating
            },
            'professionals': {
                'doctor': self.doctor_name,
                'nurse': self.nurse_name,
                'technician': self.technician_name
            },
            'comments': self.comments
        }
