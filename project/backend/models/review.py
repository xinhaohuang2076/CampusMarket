from datetime import datetime
from . import db


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    content = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer = db.relationship('User', foreign_keys=[from_user])

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'from_user': self.from_user,
            'from_nickname': self.reviewer.nickname or self.reviewer.student_id if self.reviewer else '',
            'to_user': self.to_user,
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
