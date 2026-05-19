from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), default='')
    avatar = db.Column(db.String(256), default='')
    phone = db.Column(db.String(20), default='')
    credit = db.Column(db.Integer, default=100)
    role = db.Column(db.String(10), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='seller', lazy='dynamic',
                               foreign_keys='Product.user_id')
    received_reviews = db.relationship('Review', backref='seller',
                                       lazy='dynamic',
                                       foreign_keys='Review.to_user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'email': self.email,
            'nickname': self.nickname or self.student_id,
            'avatar': self.avatar,
            'phone': self.phone,
            'credit': self.credit,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
