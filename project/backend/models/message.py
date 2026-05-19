from datetime import datetime
from . import db


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    replies = db.relationship('Message', backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic', cascade='all, delete-orphan')
    sender = db.relationship('User', foreign_keys=[from_user])
    receiver = db.relationship('User', foreign_keys=[to_user])

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'from_user': self.from_user,
            'from_nickname': self.sender.nickname or self.sender.student_id,
            'to_user': self.to_user,
            'to_nickname': self.receiver.nickname or self.receiver.student_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
