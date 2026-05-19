from datetime import datetime
from . import db


class Transaction(db.Model):
    __tablename__ = 'transaction'

    VALID_STATUSES = {'pending', 'completed', 'cancelled'}

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
    seller = db.relationship('User', foreign_keys=[seller_id])
    buyer = db.relationship('User', foreign_keys=[buyer_id])

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'seller_id': self.seller_id,
            'seller_nickname': self.seller.nickname or self.seller.student_id if self.seller else '',
            'buyer_id': self.buyer_id,
            'buyer_nickname': self.buyer.nickname or self.buyer.student_id if self.buyer else '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
