"""
Locust 性能测试脚本 — 综合场景版
启动: locust -f tests/performance_tests/locustfile.py
Web UI: http://localhost:8089

共 6 类用户模拟，覆盖 27+ 种 API 行为
"""
import random
import json
from locust import HttpUser, task, between, tag

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

    @tag('browse', 'list')
    @task(4)
    def browse_products(self):
        pages = [1, 2, 3]
        self.client.get(f'/api/products?page={random.choice(pages)}&sort=latest')

    @tag('browse', 'list')
    @task(2)
    def browse_with_sort(self):
        page = random.randint(1, 5)
        sort = random.choice(SORT_OPTIONS)
        self.client.get(f'/api/products?page={page}&sort={sort}')

    @tag('search')
    @task(4)
    def search_products(self):
        kw = random.choice(KEYWORDS)
        self.client.get(f'/api/products?keyword={kw}')

    @tag('search')
    @task(2)
    def search_empty_result(self):
        """边界：搜不可能存在的关键词"""
        self.client.get('/api/products?keyword=ZZZZZZZNOTEXIST')

    @tag('search')
    @task(1)
    def search_special_chars(self):
        """边界：特殊字符搜索"""
        self.client.get('/api/products?keyword=%21%40%23%24%25')
        self.client.get('/api/products?keyword=a%20b%20c')

    @tag('detail')
    @task(3)
    def view_product(self):
        pid = random.randint(1, 800)
        self.client.get(f'/api/products/{pid}', name='/api/products/[id]—正常')

    @tag('detail')
    @task(1)
    def view_nonexistent_product(self):
        """边界：不存在的商品（404 是预期响应，不计失败）"""
        with self.client.get('/api/products/999999', catch_response=True,
                             name='/api/products/[id]—不存在') as resp:
            if resp.status_code == 404:
                resp.success()
            else:
                resp.failure(f'预期 404，实际 {resp.status_code}')

    @tag('meta')
    @task(2)
    def get_categories(self):
        self.client.get('/api/categories')
        self.client.get('/api/conditions')

    @tag('filter')
    @task(2)
    def filter_by_category(self):
        cat = random.choice(CATEGORIES)
        # 分类 + 排序混合
        sort = random.choice(SORT_OPTIONS)
        self.client.get(f'/api/products?category={cat}&sort={sort}')

    @tag('filter')
    @task(1)
    def filter_full_search(self):
        """完整搜索：关键词 + 分类 + 排序"""
        kw = random.choice(KEYWORDS)
        cat = random.choice(CATEGORIES)
        sort = random.choice(SORT_OPTIONS)
        self.client.get(f'/api/products?keyword={kw}&category={cat}&sort={sort}')

    @tag('pagination')
    @task(1)
    def pagination_edge(self):
        """边界：超大页码、负数页码"""
        self.client.get('/api/products?page=9999', name='/api/products?page=9999')
        self.client.get('/api/products?page=-1', name='/api/products?page=-1')
        self.client.get('/api/products?page=0', name='/api/products?page=0')

    @tag('meta')
    @task(1)
    def check_health(self):
        self.client.get('/api/health')

    @tag('detail')
    @task(1)
    def view_multiple_products(self):
        """连续浏览多个商品"""
        for _ in range(3):
            pid = random.randint(1, 800)
            self.client.get(f'/api/products/{pid}', name='/api/products/[id]—连续浏览')


# ============================================================
# 用户类 2：搜索深度用户（重度搜索）
# ============================================================
class SearchIntensiveUser(HttpUser):
    """模拟反复搜索、切换分类、翻页的深度搜索用户"""
    wait_time = between(0.5, 2)

    @tag('search_intensive')
    @task(3)
    def deep_search(self):
        kw = random.choice(KEYWORDS)
        cat = random.choice(CATEGORIES)
        self.client.get(f'/api/products?keyword={kw}&category={cat}&sort=price_asc')

    @tag('search_intensive')
    @task(2)
    def pagination_walk(self):
        """逐页翻看"""
        for page in range(1, 6):
            self.client.get(f'/api/products?page={page}', name='/api/products?page=N—逐页')


# ============================================================
# 用户类 3：登录用户日常操作（中度）
# ============================================================
class AuthenticatedUser(HttpUser):
    """模拟已登录用户：查看个人信息、管理商品、收藏"""
    wait_time = between(2, 6)

    def on_start(self):
        """每个虚拟用户启动时用种子账号登录"""
        sid_num = random.randint(1, 1000)
        sid = f'22023{sid_num:05d}'
        resp = self.client.post('/api/auth/login', json={
            'student_id': sid, 'password': sid
        })
        if resp.status_code == 200:
            data = resp.json()
            self.token = data['token']
            self.user_id = data['user']['id']
            self.headers = {'Authorization': f'Bearer {self.token}'}
            self.nickname = data['user']['nickname']
        else:
            self.token = None

    @tag('profile')
    @task(2)
    def view_profile(self):
        if self.token:
            self.client.get('/api/user/profile', headers=self.headers,
                          name='/api/user/profile')

    @tag('my_products')
    @task(2)
    def my_products(self):
        if self.token:
            self.client.get('/api/products/mine', headers=self.headers,
                          name='/api/products/mine')

    @tag('my_products')
    @task(1)
    def my_products_filtered(self):
        """按状态筛选自己发布的商品"""
        if self.token:
            for status in ['onsale', 'sold', 'removed']:
                self.client.get(f'/api/products/mine?status={status}',
                              headers=self.headers, name='/api/products/mine—筛选')

    @tag('favorites')
    @task(2)
    def view_favorites(self):
        if self.token:
            self.client.get('/api/favorites', headers=self.headers)

    @tag('transactions')
    @task(2)
    def view_transactions(self):
        if self.token:
            for role in ['all', 'buy', 'sell']:
                self.client.get(f'/api/transactions?role={role}',
                              headers=self.headers, name='/api/transactions—{role}')

    @tag('messages')
    @task(2)
    def view_messages(self):
        if self.token:
            for direction in ['received', 'sent']:
                self.client.get(f'/api/messages/mine?direction={direction}',
                              headers=self.headers, name='/api/messages/mine—{direction}')

    @tag('messages')
    @task(1)
    def view_reviews(self):
        """查看其他用户的评价"""
        target_id = random.randint(1, 200)
        self.client.get(f'/api/users/{target_id}/reviews', name='/api/users/[id]/reviews')


# ============================================================
# 用户类 4：活跃卖家（重度写操作）
# ============================================================
class ActiveSeller(HttpUser):
    """模拟卖家：发布、编辑、下架商品"""
    wait_time = between(3, 8)

    def on_start(self):
        sid_num = random.randint(1, 100)
        sid = f'22023{sid_num:05d}'
        resp = self.client.post('/api/auth/login', json={
            'student_id': sid, 'password': sid
        })
        if resp.status_code == 200:
            self.token = resp.json()['token']
            self.headers = {'Authorization': f'Bearer {self.token}'}
            self.my_products = []
        else:
            self.token = None

    @tag('create_product')
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
        }, headers=self.headers, name='/api/products—发布')
        if resp.status_code == 201:
            self.my_products.append(resp.json()['product']['id'])

    @tag('edit_product')
    @task(1)
    def edit_product(self):
        """编辑已发布的商品"""
        if not self.token or not self.my_products:
            return
        pid = random.choice(self.my_products)
        self.client.put(f'/api/products/{pid}', json={
            'price': round(random.uniform(5, 2000), 2),
            'description': '已修改-性能测试',
        }, headers=self.headers, name='/api/products/[id]—编辑')

    @tag('remove_product')
    @task(1)
    def remove_product(self):
        """下架商品"""
        if not self.token or not self.my_products:
            return
        pid = self.my_products.pop()
        self.client.delete(f'/api/products/{pid}', headers=self.headers,
                         name='/api/products/[id]—下架')

    @tag('upload')
    @task(1)
    def upload_image(self):
        """模拟图片上传"""
        if not self.token:
            return
        fake_img = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        self.client.post('/api/upload',
                        files={'file': ('test.png', fake_img, 'image/png')},
                        headers=self.headers, name='/api/upload')


# ============================================================
# 用户类 5：交易用户（交易流程）
# ============================================================
class TransactionUser(HttpUser):
    """模拟买家：发起交易、留言、收藏、评价"""
    wait_time = between(4, 10)

    def on_start(self):
        sid_num = random.randint(200, 400)
        sid = f'22023{sid_num:05d}'
        resp = self.client.post('/api/auth/login', json={
            'student_id': sid, 'password': sid
        })
        if resp.status_code == 200:
            self.token = resp.json()['token']
            self.headers = {'Authorization': f'Bearer {self.token}'}
        else:
            self.token = None

    @tag('message')
    @task(2)
    def send_message(self):
        """对商品留言"""
        if not self.token:
            return
        pid = random.randint(1, 500)
        msgs = ['请问还在吗？', '能便宜点吗？', '什么时候方便看货？', '还在吗？想买']
        self.client.post(f'/api/products/{pid}/messages', json={
            'content': random.choice(msgs)
        }, headers=self.headers, name='/api/products/[id]/messages—留言')

    @tag('favorite')
    @task(2)
    def toggle_favorite(self):
        if not self.token:
            return
        pid = random.randint(1, 600)
        self.client.post(f'/api/products/{pid}/favorite', headers=self.headers,
                        name='/api/products/[id]/favorite—收藏')

    @tag('transaction')
    @task(1)
    def create_transaction(self):
        """发起交易意向（400/409 是预期拒绝，不计失败）"""
        if not self.token:
            return
        pid = random.randint(1, 400)
        with self.client.post('/api/transactions', json={'product_id': pid},
                              headers=self.headers, catch_response=True,
                              name='/api/transactions—发起') as resp:
            if resp.status_code in (400, 409):
                resp.success()
            elif resp.status_code != 201:
                resp.failure(f'预期 201/400/409，实际 {resp.status_code}')

    @tag('review')
    @task(1)
    def create_review(self):
        """评价已完成交易"""
        if not self.token:
            return
        tid = random.randint(1, 115)
        rating = random.choices([5, 4, 3, 2, 1], weights=[40, 35, 15, 5, 5])[0]
        self.client.post('/api/reviews', json={
            'transaction_id': tid,
            'rating': rating,
            'content': '自动性能测试评价',
        }, headers=self.headers, name='/api/reviews—评价')


# ============================================================
# 用户类 6：管理员操作（数据统计）
# ============================================================
class AdminUser(HttpUser):
    """模拟管理员后台操作"""
    wait_time = between(3, 7)

    def on_start(self):
        resp = self.client.post('/api/auth/login', json={
            'student_id': '2202300000', 'password': 'admin123'
        })
        if resp.status_code == 200:
            self.token = resp.json()['token']
            self.headers = {'Authorization': f'Bearer {self.token}'}
        else:
            self.token = None

    @tag('admin')
    @task(2)
    def view_all_products(self):
        """管理员查看全部商品（含已下架）"""
        if not self.token:
            return
        for status in ['onsale', 'sold', 'removed', 'reserved']:
            self.client.get(f'/api/products/mine?status={status}',
                          headers=self.headers, name='/api/products—管理员查看')

    @tag('admin')
    @task(1)
    def view_all_users_reviews(self):
        if not self.token:
            return
        for uid in [1, 50, 100, 200, 500]:
            self.client.get(f'/api/users/{uid}/reviews', name='/api/users/[id]/reviews—批量')
