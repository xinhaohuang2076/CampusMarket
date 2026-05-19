from datetime import datetime
from . import db


class Product(db.Model):
    __tablename__ = 'product'

    VALID_STATUSES = {'onsale', 'reserved', 'sold', 'removed'}
    VALID_CATEGORIES = {'教材', '电子产品', '生活用品', '体育器材', '服饰', '其他'}
    VALID_CONDITIONS = {'全新', '几乎全新', '九成新', '八成新', '七成新', '六成新及以下'}

    # 状态转换白名单
    _STATUS_TRANSITIONS = {
        'onsale': {'reserved', 'sold', 'removed'},
        'reserved': {'sold', 'onsale', 'removed'},
        'sold': set(),
        'removed': set(),
    }

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(30), default='其他')
    condition = db.Column(db.String(20), default='九成新')
    status = db.Column(db.String(10), default='onsale', index=True)
    image_urls = db.Column(db.Text, default='[]')  # JSON array
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship('Message', backref='product', lazy='dynamic',
                               cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='product', lazy='dynamic',
                                cascade='all, delete-orphan')

    def can_transition_to(self, new_status):
        return new_status in self._STATUS_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status):
        if not self.can_transition_to(new_status):
            return False
        self.status = new_status
        self.updated_at = datetime.utcnow()
        return True

    def increment_view(self):
        self.view_count = (self.view_count or 0) + 1

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'seller_nickname': self.seller.nickname or self.seller.student_id,
            'seller_credit': self.seller.credit,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'condition': self.condition,
            'status': self.status,
            'image_urls': json.loads(self.image_urls) if self.image_urls else [],
            'view_count': self.view_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
