"""单元测试：数据模型（状态机、关系、方法）"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../project/backend')))

import pytest
from models import User, Product, Transaction, Review, Message, Favorite


class TestProductStatusMachine:
    """商品状态机核心逻辑测试：状态转换白名单"""

    def test_onsale_can_transition(self):
        p = Product(status='onsale')
        assert p.can_transition_to('reserved') == True
        assert p.can_transition_to('sold') == True
        assert p.can_transition_to('removed') == True

    def test_onsale_cannot_transition_to_invalid(self):
        p = Product(status='onsale')
        assert p.can_transition_to('onsale') == False
        assert p.can_transition_to('pending') == False
        assert p.can_transition_to('') == False
        assert p.can_transition_to('deleted') == False

    def test_reserved_can_transition(self):
        p = Product(status='reserved')
        assert p.can_transition_to('sold') == True
        assert p.can_transition_to('onsale') == True
        assert p.can_transition_to('removed') == True

    def test_sold_is_terminal(self):
        p = Product(status='sold')
        assert p.can_transition_to('onsale') == False
        assert p.can_transition_to('reserved') == False
        assert p.can_transition_to('removed') == False
        assert p.can_transition_to('sold') == False

    def test_removed_is_terminal(self):
        p = Product(status='removed')
        assert p.can_transition_to('onsale') == False
        assert p.can_transition_to('sold') == False
        assert p.can_transition_to('removed') == False

    def test_transition_to_executes(self):
        p = Product(status='onsale')
        assert p.transition_to('reserved') == True
        assert p.status == 'reserved'

    def test_transition_to_rejects(self):
        p = Product(status='sold')
        assert p.transition_to('onsale') == False
        assert p.status == 'sold'

    def test_full_lifecycle(self):
        p = Product(status='onsale')
        assert p.transition_to('reserved') == True
        assert p.transition_to('sold') == True
        assert p.transition_to('removed') == False  # sold is terminal


class TestUserModel:
    def test_set_password_hashes(self):
        u = User()
        u.set_password('mypassword')
        assert u.password_hash != 'mypassword'
        assert len(u.password_hash) > 20

    def test_check_password_correct(self):
        u = User()
        u.set_password('mypassword')
        assert u.check_password('mypassword') == True

    def test_check_password_wrong(self):
        u = User()
        u.set_password('mypassword')
        assert u.check_password('wrongpassword') == False

    def test_to_dict_contains_keys(self, session):
        from datetime import datetime
        u = User(student_id='2202300001', email='test@qq.com', nickname='测试',
                 credit=100, role='user', created_at=datetime.utcnow())
        d = u.to_dict()
        assert 'student_id' in d
        assert 'email' in d
        assert 'nickname' in d
        assert 'credit' in d
        assert d['student_id'] == '2202300001'
        assert d['nickname'] == '测试'

    def test_default_credit(self, session):
        from random import randint
        sid = f'22023{randint(10000, 99999)}'
        u = User(student_id=sid, email=f'{sid}@qq.com')
        u.set_password('test123')
        session.add(u)
        session.flush()
        assert u.credit == 100

    def test_default_role(self, session):
        from random import randint
        sid = f'22023{randint(10000, 99999)}'
        u = User(student_id=sid, email=f'{sid}@163.com')
        u.set_password('test123')
        session.add(u)
        session.flush()
        assert u.role == 'user'


class TestReviewRatingBoundary:
    def test_valid_categories(self):
        assert '教材' in Product.VALID_CATEGORIES
        assert '电子产品' in Product.VALID_CATEGORIES
        assert '其他' in Product.VALID_CATEGORIES
        assert len(Product.VALID_CATEGORIES) >= 5

    def test_valid_conditions(self):
        assert '全新' in Product.VALID_CONDITIONS
        assert '九成新' in Product.VALID_CONDITIONS
        assert '六成新及以下' in Product.VALID_CONDITIONS
