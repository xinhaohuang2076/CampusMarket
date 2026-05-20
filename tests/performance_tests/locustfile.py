"""
Locust 性能测试脚本 — 综合场景版
启动: locust -f tests/performance_tests/locustfile.py
Web UI: http://localhost:8089

场景运行指南:
  # 1. 混合场景（默认，6类用户全开）
  locust -f tests/performance_tests/locustfile.py

  # 2. 只测某类用户（按 --tags 过滤）
  locust -f locustfile.py --tags browse         # 仅游客浏览
  locust -f locustfile.py --tags search         # 仅搜索行为
  locust -f locustfile.py --tags auth           # 仅认证相关
  locust -f locustfile.py --tags seller         # 仅卖家操作
  locust -f locustfile.py --tags admin          # 仅管理员操作

  # 3. 读写分离场景
  locust -f locustfile.py --tags read           # 读密集（浏览+搜索+详情）
  locust -f locustfile.py --tags write          # 写密集（发布+编辑+交易+评价）

共 6 类用户模拟，覆盖 27+ 种 API 行为

报告分组前缀说明:
  [读]    商品列表/搜索/详情/分类/健康检查 — 纯读取
  [写]    发布/编辑/下架/上传 — 数据写入
  [用户]  登录/个人信息/收藏/留言/交易/评价 — 用户交互
  [管理]  管理员后台操作
"""
import random
import json
import requests as _requests
from locust import HttpUser, task, between, tag

# ---- 预生成 Token 池（避免压测时大量登录请求撑爆服务器）----
_ADMIN_TOKEN = None
_AUTH_TOKENS = []
_SELLER_TOKENS = []
_TRANSACTION_TOKENS = []


def _init_tokens():
    global _ADMIN_TOKEN

    def _login(sid, pw):
        r = _requests.post('http://127.0.0.1:5000/api/auth/login',
                           json={'student_id': sid, 'password': pw}, timeout=5)
        return r.json()['token'] if r.status_code == 200 else None

    _ADMIN_TOKEN = _login('2202300000', 'admin123')

    for i in [6, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
        sid = f'22023{i:05d}'
        t = _login(sid, sid)
        if t:
            _AUTH_TOKENS.append(t)

    for i in [6, 20, 40, 60, 80, 100]:
        sid = f'22023{i:05d}'
        t = _login(sid, sid)
        if t:
            _SELLER_TOKENS.append(t)

    for i in [200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]:
        sid = f'22023{i:05d}'
        t = _login(sid, sid)
        if t:
            _TRANSACTION_TOKENS.append(t)


_init_tokens()

# ---- 数据池 ----
KEYWORDS = ['数学', '英语', '教材', '电子', '生活', '体育', '考研', '二手',
            '计算机', '考研英语', '耳机', '键盘', '鼠标', '台灯', '风扇', '篮球']
CATEGORIES = ['教材', '电子产品', '生活用品', '体育器材', '服饰', '其他']
CONDITIONS = ['全新', '几乎全新', '九成新', '八成新', '七成新', '六成新及以下']
PRODUCT_TITLES = [
    '高等数学第七版', '大学英语四级真题', 'C语言程序设计', '考研英语词汇书',
    '二手iPad Air', '机械键盘青轴', '降噪耳机', 'USB-C扩展坞',
    '台灯护眼', '宿舍小风扇', '保温杯', '收纳箱',
    '羽毛球拍', '篮球斯伯丁', '瑜伽垫', '跳绳',
    '卫衣春秋款', '牛仔裤修身', '运动鞋', '书包双肩',
]
SORT_OPTIONS = ['latest', 'price_asc', 'price_desc']


# ============================================================
# 用户类 1：纯游客浏览（轻量级）
# ============================================================
class BrowsingUser(HttpUser):
    """模拟游客：浏览、搜索、翻页、看详情"""
    wait_time = between(1, 4)

    @tag('browse', 'list', 'read')
    @task(4)
    def browse_products(self):
        pages = [1, 2, 3]
        self.client.get(f'/api/products?page={random.choice(pages)}&sort=latest',
                        name='[读] 首页列表')

    @tag('browse', 'list', 'read')
    @task(2)
    def browse_with_sort(self):
        page = random.randint(1, 5)
        sort = random.choice(SORT_OPTIONS)
        self.client.get(f'/api/products?page={page}&sort={sort}',
                        name='[读] 列表+排序')

    @tag('search', 'read')
    @task(4)
    def search_products(self):
        kw = random.choice(KEYWORDS)
        self.client.get(f'/api/products?keyword={kw}',
                        name='[读] 搜索命中')

    @tag('search', 'read')
    @task(2)
    def search_empty_result(self):
        self.client.get('/api/products?keyword=ZZZZZZZNOTEXIST',
                        name='[读] 搜索无结果')

    @tag('search', 'read')
    @task(1)
    def search_special_chars(self):
        self.client.get('/api/products?keyword=%21%40%23%24%25',
                        name='[读] 搜索特殊字符')
        self.client.get('/api/products?keyword=a%20b%20c',
                        name='[读] 搜索特殊字符')

    @tag('detail', 'read')
    @task(3)
    def view_product(self):
        pid = random.randint(1, 800)
        self.client.get(f'/api/products/{pid}',
                        name='[读] 商品详情—正常')

    @tag('detail', 'read')
    @task(1)
    def view_nonexistent_product(self):
        with self.client.get('/api/products/999999', catch_response=True,
                             name='[读] 商品详情—不存在') as resp:
            if resp.status_code == 404:
                resp.success()
            else:
                resp.failure(f'预期 404，实际 {resp.status_code}')

    @tag('meta', 'read')
    @task(2)
    def get_categories(self):
        self.client.get('/api/categories', name='[读] 分类列表')
        self.client.get('/api/conditions', name='[读] 成色列表')

    @tag('filter', 'read')
    @task(2)
    def filter_by_category(self):
        cat = random.choice(CATEGORIES)
        sort = random.choice(SORT_OPTIONS)
        self.client.get(f'/api/products?category={cat}&sort={sort}',
                        name='[读] 分类筛选')

    @tag('filter', 'read')
    @task(1)
    def filter_full_search(self):
        kw = random.choice(KEYWORDS)
        cat = random.choice(CATEGORIES)
        sort = random.choice(SORT_OPTIONS)
        self.client.get(f'/api/products?keyword={kw}&category={cat}&sort={sort}',
                        name='[读] 组合搜索')

    @tag('pagination', 'read')
    @task(1)
    def pagination_edge(self):
        self.client.get('/api/products?page=9999', name='[读] 分页边界')
        self.client.get('/api/products?page=-1', name='[读] 分页边界')
        self.client.get('/api/products?page=0', name='[读] 分页边界')

    @tag('meta', 'read')
    @task(1)
    def check_health(self):
        self.client.get('/api/health', name='[读] 健康检查')

    @tag('detail', 'read')
    @task(1)
    def view_multiple_products(self):
        for _ in range(3):
            pid = random.randint(1, 800)
            self.client.get(f'/api/products/{pid}',
                            name='[读] 商品详情—连续浏览')


# ============================================================
# 用户类 2：搜索深度用户（重度搜索）
# ============================================================
class SearchIntensiveUser(HttpUser):
    """模拟反复搜索、切换分类、翻页的深度搜索用户"""
    wait_time = between(0.5, 2)

    @tag('search_intensive', 'read')
    @task(3)
    def deep_search(self):
        kw = random.choice(KEYWORDS)
        cat = random.choice(CATEGORIES)
        self.client.get(f'/api/products?keyword={kw}&category={cat}&sort=price_asc',
                        name='[读] 深度组合搜索')

    @tag('search_intensive', 'read')
    @task(2)
    def pagination_walk(self):
        for page in range(1, 6):
            self.client.get(f'/api/products?page={page}',
                            name='[读] 逐页翻看')


# ============================================================
# 用户类 3：登录用户日常操作（中度）
# ============================================================
class AuthenticatedUser(HttpUser):
    """模拟已登录用户：查看个人信息、管理商品、收藏"""
    wait_time = between(0.5, 2)

    def on_start(self):
        self.token = random.choice(_AUTH_TOKENS)
        self.headers = {'Authorization': f'Bearer {self.token}'}

    @tag('auth', 'profile', 'user')
    @task(2)
    def view_profile(self):
        if self.token:
            self.client.get('/api/user/profile', headers=self.headers,
                          name='[用户] 个人信息')

    @tag('auth', 'my_products', 'user')
    @task(2)
    def my_products(self):
        if self.token:
            self.client.get('/api/products/mine', headers=self.headers,
                          name='[用户] 我的商品')

    @tag('auth', 'my_products', 'user')
    @task(1)
    def my_products_filtered(self):
        if self.token:
            for status in ['onsale', 'sold', 'removed']:
                self.client.get(f'/api/products/mine?status={status}',
                              headers=self.headers, name='[用户] 商品筛选')

    @tag('auth', 'favorites', 'user')
    @task(2)
    def view_favorites(self):
        if self.token:
            self.client.get('/api/favorites', headers=self.headers,
                          name='[用户] 收藏列表')

    @tag('auth', 'transactions', 'user')
    @task(2)
    def view_transactions(self):
        if self.token:
            for role in ['all', 'buy', 'sell']:
                self.client.get(f'/api/transactions?role={role}',
                              headers=self.headers, name='[用户] 交易记录')

    @tag('auth', 'messages', 'user')
    @task(2)
    def view_messages(self):
        if self.token:
            for direction in ['received', 'sent']:
                self.client.get(f'/api/messages/mine?direction={direction}',
                              headers=self.headers, name='[用户] 留言列表')

    @tag('auth', 'reviews', 'user')
    @task(1)
    def view_reviews(self):
        target_id = random.randint(1, 200)
        self.client.get(f'/api/users/{target_id}/reviews',
                        name='[用户] 查看评价')


# ============================================================
# 用户类 4：活跃卖家（重度写操作）
# ============================================================
class ActiveSeller(HttpUser):
    """模拟卖家：发布、编辑、下架商品"""
    wait_time = between(0.5, 2)

    def on_start(self):
        self.token = random.choice(_SELLER_TOKENS)
        self.headers = {'Authorization': f'Bearer {self.token}'}
        self.my_products = []

    @tag('seller', 'create_product', 'write')
    @task(2)
    def create_product(self):
        if not self.token:
            return
        title = random.choice(PRODUCT_TITLES)
        cat = random.choice(CATEGORIES)
        cond = random.choice(CONDITIONS)
        price = round(random.uniform(5, 2000), 2)
        resp = self.client.post('/api/products', json={
            'title': title,
            'description': '闲置物品，价格可议',
            'price': price,
            'category': cat,
            'condition': cond,
        }, headers=self.headers, name='[写] 发布商品')
        if resp.status_code == 201:
            self.my_products.append(resp.json()['product']['id'])

    @tag('seller', 'edit_product', 'write')
    @task(1)
    def edit_product(self):
        if not self.token or not self.my_products:
            return
        pid = random.choice(self.my_products)
        self.client.put(f'/api/products/{pid}', json={
            'price': round(random.uniform(5, 2000), 2),
            'description': '已修改-性能测试',
        }, headers=self.headers, name='[写] 编辑商品')

    @tag('seller', 'remove_product', 'write')
    @task(1)
    def remove_product(self):
        if not self.token or not self.my_products:
            return
        pid = self.my_products.pop()
        self.client.delete(f'/api/products/{pid}', headers=self.headers,
                         name='[写] 下架商品')

    @tag('seller', 'upload', 'write')
    @task(1)
    def upload_image(self):
        if not self.token:
            return
        fake_img = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        self.client.post('/api/upload',
                        files={'file': ('test.png', fake_img, 'image/png')},
                        headers=self.headers, name='[写] 图片上传')


# ============================================================
# 用户类 5：交易用户（交易流程）
# ============================================================
class TransactionUser(HttpUser):
    """模拟买家：发起交易、留言、收藏、评价"""
    wait_time = between(0.5, 2)

    def on_start(self):
        self.token = random.choice(_TRANSACTION_TOKENS)
        self.headers = {'Authorization': f'Bearer {self.token}'}

    @tag('transaction', 'message', 'user')
    @task(2)
    def send_message(self):
        if not self.token:
            return
        pid = random.randint(1, 500)
        msgs = ['请问还在吗？', '能便宜点吗？', '什么时候方便看货？', '还在吗？想买']
        self.client.post(f'/api/products/{pid}/messages', json={
            'content': random.choice(msgs)
        }, headers=self.headers, name='[用户] 发送留言')

    @tag('transaction', 'favorite', 'user')
    @task(2)
    def toggle_favorite(self):
        if not self.token:
            return
        pid = random.randint(1, 600)
        self.client.post(f'/api/products/{pid}/favorite', headers=self.headers,
                        name='[用户] 收藏/取消')

    @tag('transaction', 'write')
    @task(1)
    def create_transaction(self):
        if not self.token:
            return
        pid = random.randint(1, 400)
        with self.client.post('/api/transactions', json={'product_id': pid},
                              headers=self.headers, catch_response=True,
                              name='[写] 发起交易') as resp:
            if resp.status_code in (400, 404, 409):
                resp.success()
            elif resp.status_code != 201:
                resp.failure(f'预期 201/400/404/409，实际 {resp.status_code}')

    @tag('transaction', 'write')
    @task(1)
    def create_review(self):
        if not self.token:
            return
        tid = random.randint(1, 115)
        rating = random.choices([5, 4, 3, 2, 1], weights=[40, 35, 15, 5, 5])[0]
        with self.client.post('/api/reviews', json={
            'transaction_id': tid,
            'rating': rating,
            'content': '自动性能测试评价',
        }, headers=self.headers, catch_response=True,
                name='[写] 提交评价') as resp:
            if resp.status_code in (400, 403, 409):
                resp.success()
            elif resp.status_code != 201:
                resp.failure(f'预期 201/400/403/409，实际 {resp.status_code}')


# ============================================================
# 用户类 6：管理员操作（数据统计）
# ============================================================
class AdminUser(HttpUser):
    """模拟管理员后台操作"""
    wait_time = between(0.5, 2)

    def on_start(self):
        self.token = _ADMIN_TOKEN
        self.headers = {'Authorization': f'Bearer {self.token}'}

    @tag('admin', 'manage')
    @task(2)
    def view_all_products(self):
        if not self.token:
            return
        for status in ['onsale', 'sold', 'removed', 'reserved']:
            self.client.get(f'/api/products/mine?status={status}',
                          headers=self.headers, name='[管理] 查看商品')

    @tag('admin', 'manage')
    @task(1)
    def view_all_users_reviews(self):
        if not self.token:
            return
        for uid in [1, 50, 100, 200, 500]:
            self.client.get(f'/api/users/{uid}/reviews',
                          name='[管理] 查看评价')
