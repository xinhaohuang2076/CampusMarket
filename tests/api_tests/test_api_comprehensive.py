"""
API 综合测试：覆盖所有接口的正向、异常、边界用例
运行: pytest tests/api_tests/ -v  (需先启动后端)
"""
import pytest
import requests

BASE = 'http://127.0.0.1:5000'

# ---- 工具函数 ----

def _reg(sid, email, pw='test123', nick='T'):
    r = requests.post(f'{BASE}/api/auth/register',
                      json={'student_id': sid, 'email': email, 'password': pw, 'nickname': nick})
    if r.status_code == 201:
        return r.json()['token']
    # already exists
    r = requests.post(f'{BASE}/api/auth/login',
                      json={'student_id': sid, 'password': pw})
    return r.json()['token']


def _create_product(token, title='P', price=10, category='教材', condition='九成新'):
    r = requests.post(f'{BASE}/api/products',
                      json={'title': title, 'price': price, 'category': category, 'condition': condition},
                      headers={'Authorization': f'Bearer {token}'})
    return r.json()['product']['id']


@pytest.fixture(scope='module')
def tokens():
    t1 = _reg('2202399995', 'tapi1@qq.com', nick='API-T1')
    t2 = _reg('2202399996', 'tapi2@qq.com', nick='API-T2')
    return {'t1': t1, 't2': t2}


# ===== 认证 =====

class TestAuth:
    def test_health(self):
        assert requests.get(f'{BASE}/api/health').json()['status'] == 'ok'

    def test_register(self):
        """注册成功 - 使用不重复的学号"""
        r = requests.post(f'{BASE}/api/auth/register', json={
            'student_id': '2202399881', 'email': 'freshe1@qq.com',
            'password': 'pass123', 'nickname': '新用户'})
        assert r.status_code == 201
        assert 'token' in r.json()

    def test_register_dup_sid(self):
        """重复学号应返回 409"""
        sid, email = '2202399882', 'dup_sid@qq.com'
        requests.post(f'{BASE}/api/auth/register', json={'student_id': sid, 'email': email, 'password': 'pass123'})
        r = requests.post(f'{BASE}/api/auth/register',
                          json={'student_id': sid, 'email': 'other@qq.com', 'password': 'pass123'})
        assert r.status_code == 409

    def test_register_dup_email(self):
        """重复邮箱应返回 409"""
        sid, email = '2202399883', 'dup_email@qq.com'
        requests.post(f'{BASE}/api/auth/register', json={'student_id': sid, 'email': email, 'password': 'pass123'})
        r = requests.post(f'{BASE}/api/auth/register',
                          json={'student_id': '2202399884', 'email': email, 'password': 'pass123'})
        assert r.status_code == 409

    def test_register_bad_sid(self):
        r = requests.post(f'{BASE}/api/auth/register',
                          json={'student_id': '123', 'email': 'x@qq.com', 'password': 'pass123'})
        assert r.status_code == 400

    def test_register_bad_email(self):
        r = requests.post(f'{BASE}/api/auth/register',
                          json={'student_id': '2202399903', 'email': 'x@gmail.com', 'password': 'pass123'})
        assert r.status_code == 400

    def test_register_short_pw(self):
        r = requests.post(f'{BASE}/api/auth/register',
                          json={'student_id': '2202399904', 'email': 'x@qq.com', 'password': '12345'})
        assert r.status_code == 400

    def test_login(self, tokens):
        r = requests.post(f'{BASE}/api/auth/login',
                          json={'student_id': '2202399995', 'password': 'test123'})
        assert r.status_code == 200

    def test_login_wrong_pw(self):
        r = requests.post(f'{BASE}/api/auth/login',
                          json={'student_id': '2202399995', 'password': 'wrong'})
        assert r.status_code == 401

    def test_login_empty(self):
        r = requests.post(f'{BASE}/api/auth/login', json={'student_id': '', 'password': ''})
        assert r.status_code == 400

    def test_profile(self, tokens):
        r = requests.get(f'{BASE}/api/user/profile', headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 200

    def test_profile_unauth(self):
        assert requests.get(f'{BASE}/api/user/profile').status_code == 401

    def test_update_profile(self, tokens):
        r = requests.put(f'{BASE}/api/user/profile', json={'nickname': '改名了'},
                         headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 200

    def test_change_password(self, tokens):
        # Change → login new → change back
        h = {'Authorization': f'Bearer {tokens["t1"]}'}
        requests.put(f'{BASE}/api/user/password', json={'old_password': 'test123', 'new_password': 'tmp123'}, headers=h)
        r = requests.post(f'{BASE}/api/auth/login', json={'student_id': '2202399995', 'password': 'tmp123'})
        assert r.status_code == 200
        t = r.json()['token']
        requests.put(f'{BASE}/api/user/password', json={'old_password': 'tmp123', 'new_password': 'test123'},
                     headers={'Authorization': f'Bearer {t}'})


# ===== 商品 =====

class TestProduct:
    def test_list(self):
        r = requests.get(f'{BASE}/api/products')
        assert r.status_code == 200 and 'items' in r.json()

    def test_list_page(self):
        assert requests.get(f'{BASE}/api/products?page=1').json()['page'] == 1

    def test_list_neg_page(self):
        assert requests.get(f'{BASE}/api/products?page=-1').json()['page'] == 1

    def test_search_hit(self):
        assert requests.get(f'{BASE}/api/products?keyword=数学').json()['total'] > 0

    def test_search_miss(self):
        assert requests.get(f'{BASE}/api/products?keyword=ZZZZNOPE').json()['total'] == 0

    def test_create(self, tokens):
        pid = _create_product(tokens['t1'], 'API测试')
        assert pid > 0

    def test_create_missing_title(self, tokens):
        r = requests.post(f'{BASE}/api/products', json={'price': 10},
                          headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 400

    def test_create_invalid_price(self, tokens):
        r = requests.post(f'{BASE}/api/products', json={'title': 'x', 'price': -1},
                          headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 400

    def test_create_free(self, tokens):
        r = requests.post(f'{BASE}/api/products', json={'title': '免费', 'price': 0, 'category': '其他'},
                          headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 201

    def test_get_detail(self, tokens):
        pid = _create_product(tokens['t1'], '查看测试')
        r = requests.get(f'{BASE}/api/products/{pid}')
        assert r.json()['product']['title'] == '查看测试'

    def test_get_404(self):
        assert requests.get(f'{BASE}/api/products/999999').status_code == 404

    def test_update(self, tokens):
        pid = _create_product(tokens['t1'], '改前')
        requests.put(f'{BASE}/api/products/{pid}', json={'title': '改后'},
                     headers={'Authorization': f'Bearer {tokens["t1"]}'})
        r = requests.get(f'{BASE}/api/products/{pid}')
        assert r.json()['product']['title'] == '改后'

    def test_update_forbidden(self, tokens):
        pid = _create_product(tokens['t1'], '别改')
        r = requests.put(f'{BASE}/api/products/{pid}', json={'title': 'hack'},
                         headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 403

    def test_remove(self, tokens):
        pid = _create_product(tokens['t1'], '删')
        requests.delete(f'{BASE}/api/products/{pid}', headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert requests.get(f'{BASE}/api/products/{pid}').json()['product']['status'] == 'removed'

    def test_remove_forbidden(self, tokens):
        pid = _create_product(tokens['t1'], '别删')
        r = requests.delete(f'{BASE}/api/products/{pid}', headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 403

    def test_mine(self, tokens):
        r = requests.get(f'{BASE}/api/products/mine', headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 200

    def test_categories(self):
        assert len(requests.get(f'{BASE}/api/categories').json()['categories']) > 0

    def test_conditions(self):
        assert len(requests.get(f'{BASE}/api/conditions').json()['conditions']) > 0

    def test_upload_unauth(self):
        assert requests.post(f'{BASE}/api/upload', files={'file': ('x.png', b'', 'image/png')}).status_code == 401


# ===== 收藏 =====

class TestFavorite:
    def test_add(self, tokens):
        pid = _create_product(tokens['t1'], '收')
        r = requests.post(f'{BASE}/api/products/{pid}/favorite',
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 201 and r.json()['favorited'] == True

    def test_remove(self, tokens):
        pid = _create_product(tokens['t1'], '取收')
        h = {'Authorization': f'Bearer {tokens["t2"]}'}
        requests.post(f'{BASE}/api/products/{pid}/favorite', headers=h)
        r = requests.post(f'{BASE}/api/products/{pid}/favorite', headers=h)
        assert r.status_code == 200 and r.json()['favorited'] == False

    def test_list(self, tokens):
        r = requests.get(f'{BASE}/api/favorites', headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 200

    def test_404(self, tokens):
        r = requests.post(f'{BASE}/api/products/999999/favorite',
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 404


# ===== 留言 =====

class TestMessage:
    def test_send(self, tokens):
        pid = _create_product(tokens['t1'], '留言测')
        r = requests.post(f'{BASE}/api/products/{pid}/messages', json={'content': '在吗'},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 201

    def test_send_empty(self, tokens):
        pid = _create_product(tokens['t1'], '空留言')
        r = requests.post(f'{BASE}/api/products/{pid}/messages', json={'content': ''},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 400

    def test_list(self, tokens):
        pid = _create_product(tokens['t1'], '查留')
        r = requests.get(f'{BASE}/api/products/{pid}/messages')
        assert r.status_code == 200

    def test_mine(self, tokens):
        r = requests.get(f'{BASE}/api/messages/mine', headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 200

    def test_removed_product(self, tokens):
        pid = _create_product(tokens['t1'], '下架留')
        requests.delete(f'{BASE}/api/products/{pid}', headers={'Authorization': f'Bearer {tokens["t1"]}'})
        r = requests.post(f'{BASE}/api/products/{pid}/messages', json={'content': 'test'},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 400


# ===== 交易 =====

class TestTransaction:
    def test_create(self, tokens):
        pid = _create_product(tokens['t1'], '交易测')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 201

    def test_duplicate(self, tokens):
        pid = _create_product(tokens['t1'], '重复交')
        h = {'Authorization': f'Bearer {tokens["t2"]}'}
        requests.post(f'{BASE}/api/transactions', json={'product_id': pid}, headers=h)
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid}, headers=h)
        assert r.status_code == 409

    def test_buy_own(self, tokens):
        pid = _create_product(tokens['t1'], '自买')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 400

    def test_complete(self, tokens):
        pid = _create_product(tokens['t1'], '完成交')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        tid = r.json()['transaction']['id']
        r = requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'complete'},
                         headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 200
        assert requests.get(f'{BASE}/api/products/{pid}').json()['product']['status'] == 'sold'

    def test_cancel(self, tokens):
        pid = _create_product(tokens['t1'], '取消交')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        tid = r.json()['transaction']['id']
        r = requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'cancel'},
                         headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 200


# ===== 评价 =====

class TestReview:
    def test_create(self, tokens):
        pid = _create_product(tokens['t1'], '评价测')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        tid = r.json()['transaction']['id']
        requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'complete'},
                     headers={'Authorization': f'Bearer {tokens["t1"]}'})
        r = requests.post(f'{BASE}/api/reviews', json={'transaction_id': tid, 'rating': 5, 'content': '好'},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 201

    def test_duplicate(self, tokens):
        pid = _create_product(tokens['t1'], '重复评')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        tid = r.json()['transaction']['id']
        requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'complete'},
                     headers={'Authorization': f'Bearer {tokens["t1"]}'})
        h = {'Authorization': f'Bearer {tokens["t2"]}'}
        requests.post(f'{BASE}/api/reviews', json={'transaction_id': tid, 'rating': 5}, headers=h)
        r = requests.post(f'{BASE}/api/reviews', json={'transaction_id': tid, 'rating': 4}, headers=h)
        assert r.status_code == 409

    def test_invalid_rating(self, tokens):
        pid = _create_product(tokens['t1'], '评分测')
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        tid = r.json()['transaction']['id']
        requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'complete'},
                     headers={'Authorization': f'Bearer {tokens["t1"]}'})
        r = requests.post(f'{BASE}/api/reviews', json={'transaction_id': tid, 'rating': 0},
                          headers={'Authorization': f'Bearer {tokens["t2"]}'})
        assert r.status_code == 400

    def test_user_reviews(self):
        r = requests.get(f'{BASE}/api/users/1/reviews')
        assert r.status_code == 200 and 'avg_rating' in r.json()

    def test_seller_can_review_buyer(self, tokens):
        """卖家也可以评价买家（双方互评）"""
        pid = _create_product(tokens['t1'], '互评')
        h1 = {'Authorization': f'Bearer {tokens["t1"]}'}
        h2 = {'Authorization': f'Bearer {tokens["t2"]}'}
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid}, headers=h2)
        tid = r.json()['transaction']['id']
        requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'complete'}, headers=h1)
        # 卖家评价买家
        r = requests.post(f'{BASE}/api/reviews', json={'transaction_id': tid, 'rating': 4, 'content': '好买家'},
                          headers=h1)
        assert r.status_code == 201

    def test_credit_updated(self, tokens):
        pid = _create_product(tokens['t1'], '信用测')
        h1 = {'Authorization': f'Bearer {tokens["t1"]}'}
        h2 = {'Authorization': f'Bearer {tokens["t2"]}'}
        credit_before = requests.get(f'{BASE}/api/user/profile', headers=h1).json()['user']['credit']
        r = requests.post(f'{BASE}/api/transactions', json={'product_id': pid}, headers=h2)
        tid = r.json()['transaction']['id']
        requests.put(f'{BASE}/api/transactions/{tid}', json={'action': 'complete'}, headers=h1)
        requests.post(f'{BASE}/api/reviews', json={'transaction_id': tid, 'rating': 4}, headers=h2)
        credit_after = requests.get(f'{BASE}/api/user/profile', headers=h1).json()['user']['credit']
        assert credit_after >= credit_before + 1


# ===== 管理员 =====

@pytest.fixture(scope='module')
def admin_token():
    r = requests.post(f'{BASE}/api/auth/login',
                      json={'student_id': '2202300000', 'password': 'admin123'})
    assert r.status_code == 200, '管理员登录失败'
    return r.json()['token']


class TestAdmin:
    """管理员后台 API 测试"""

    def test_stats(self, admin_token):
        r = requests.get(f'{BASE}/api/admin/stats',
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        d = r.json()
        assert d['total_users'] >= 1000
        assert d['total_products'] >= 700
        assert 'products_by_status' in d

    def test_stats_unauth(self):
        """未登录不能访问"""
        r = requests.get(f'{BASE}/api/admin/stats')
        assert r.status_code == 401

    def test_stats_forbidden(self, tokens):
        """普通用户不能访问"""
        r = requests.get(f'{BASE}/api/admin/stats',
                         headers={'Authorization': f'Bearer {tokens["t1"]}'})
        assert r.status_code == 403

    def test_users_list(self, admin_token):
        r = requests.get(f'{BASE}/api/admin/users?page=1',
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        d = r.json()
        assert d['total'] >= 1000
        assert len(d['items']) == 20

    def test_users_search(self, admin_token):
        r = requests.get(f'{BASE}/api/admin/users?keyword=admin',
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        assert r.json()['total'] >= 1

    def test_users_update_credit(self, admin_token):
        """管理员修改普通用户信用分"""
        r = requests.get(f'{BASE}/api/admin/users?page=1',
                         headers={'Authorization': f'Bearer {admin_token}'})
        uid = r.json()['items'][0]['id']
        r = requests.put(f'{BASE}/api/admin/users/{uid}', json={'credit': 150},
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        assert r.json()['user']['credit'] == 150

    def test_users_cannot_modify_self(self, admin_token):
        """管理员不能修改自己"""
        r = requests.get(f'{BASE}/api/admin/users?page=1&keyword=2202300000',
                         headers={'Authorization': f'Bearer {admin_token}'})
        uid = r.json()['items'][0]['id']
        r = requests.put(f'{BASE}/api/admin/users/{uid}', json={'role': 'user'},
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 403

    def test_products_list(self, admin_token):
        r = requests.get(f'{BASE}/api/admin/products?page=1',
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        d = r.json()
        assert d['total'] >= 700
        assert 'items' in d

    def test_transactions_list(self, admin_token):
        r = requests.get(f'{BASE}/api/admin/transactions?page=1',
                         headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        assert 'items' in r.json()
