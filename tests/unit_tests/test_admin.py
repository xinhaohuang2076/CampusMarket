"""单元测试：admin_required 装饰器和管理员权限"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../project/backend')))

import pytest
from models import db as _db, User


@pytest.fixture(autouse=True)
def setup_users(app):
    """在每个测试前创建管理员和普通用户"""
    with app.app_context():
        admin = User(
            student_id='2202300000', email='admin@test.com',
            nickname='admin', role='admin', credit=999
        )
        admin.set_password('admin123')

        user = User(
            student_id='2202300001', email='user@test.com',
            nickname='user', role='user', credit=100
        )
        user.set_password('123456')

        _db.session.add_all([admin, user])
        _db.session.commit()

        yield

        _db.session.rollback()


def admin_token(client):
    """获取管理员 JWT"""
    resp = client.post('/api/auth/login', json={
        'student_id': '2202300000', 'password': 'admin123'
    })
    return resp.get_json()['token']


def user_token(client):
    """获取普通用户 JWT"""
    resp = client.post('/api/auth/login', json={
        'student_id': '2202300001', 'password': '123456'
    })
    return resp.get_json()['token']


class TestAdminRequired:
    """测试 admin_required 装饰器权限控制"""

    def test_admin_can_access_stats(self, client):
        """管理员可以访问管理接口"""
        token = admin_token(client)
        resp = client.get('/api/admin/stats',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total_users'] == 2  # admin + user
        assert 'total_products' in data
        assert 'total_transactions' in data

    def test_non_admin_blocked(self, client):
        """普通用户访问返回 403"""
        token = user_token(client)
        resp = client.get('/api/admin/stats',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 403
        assert resp.get_json()['error'] == '需要管理员权限'

    def test_no_auth_returns_401(self, client):
        """未登录访问返回 401"""
        resp = client.get('/api/admin/stats')
        assert resp.status_code == 401

    def test_admin_users_list(self, client):
        """管理员可以查看用户列表"""
        token = admin_token(client)
        resp = client.get('/api/admin/users?page=1',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total'] >= 2
        assert len(data['items']) >= 2

    def test_admin_can_modify_user(self, client):
        """管理员可以修改用户角色和信用分"""
        token = admin_token(client)
        # 修改 user (id=2) 的信用分
        resp = client.put('/api/admin/users/2', json={'credit': 200},
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        assert resp.get_json()['user']['credit'] == 200

    def test_admin_cannot_modify_self(self, client):
        """管理员不能修改自己的角色"""
        token = admin_token(client)
        resp = client.put('/api/admin/users/1', json={'role': 'user'},
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 403
        assert '不能修改自己的角色' in resp.get_json()['error']

    def test_admin_products_list(self, client):
        """管理员可以查看所有商品"""
        token = admin_token(client)
        resp = client.get('/api/admin/products?page=1',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200

    def test_admin_transactions_list(self, client):
        """管理员可以查看所有交易"""
        token = admin_token(client)
        resp = client.get('/api/admin/transactions?page=1',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
