"""种子数据脚本：生成 1000 名学生及示例数据"""
import sys
import os
import json
from random import choice, randint, sample, shuffle
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models import db, User, Product, Message, Favorite, Transaction, Review, init_db

init_db(Config.SQLALCHEMY_DATABASE_URI)

BATCH = 100

NICKNAMES = [
    '小明', '小红', '小刚', '小丽', '阿强', '大伟', '佳琪', '思涵',
    '子轩', '雨桐', '皓宇', '若曦', '逸辰', '语嫣', '泽宇', '静怡',
    '星辰', '沐晴', '凯文', '梓涵', '俊杰', '芷若', '天佑', '诗涵',
    '明哲', '晓彤', '昊然', '欣怡', '俊豪', '紫萱', '浩宇', '雅琴',
    '子涵', '思远', '一鸣', '文静', '志强', '美琪', '嘉懿', '婉婷'
]

CATEGORIES = ['教材', '电子产品', '生活用品', '体育器材', '服饰', '其他']

PRODUCT_TEMPLATES = [
    ('高等数学第七版', '教材', 25.00),
    ('大学英语四级真题', '教材', 15.00),
    ('线性代数辅导书', '教材', 18.00),
    ('C语言程序设计', '教材', 30.00),
    ('考研英语词汇书', '教材', 20.00),
    ('二手iPad Air', '电子产品', 1800.00),
    ('机械键盘青轴', '电子产品', 89.00),
    ('降噪耳机', '电子产品', 299.00),
    ('USB-C扩展坞', '电子产品', 65.00),
    ('蓝牙鼠标', '电子产品', 45.00),
    ('台灯护眼', '生活用品', 35.00),
    ('宿舍小风扇', '生活用品', 28.00),
    ('保温杯500ml', '生活用品', 40.00),
    ('收纳箱大号', '生活用品', 22.00),
    ('床上桌', '生活用品', 55.00),
    ('羽毛球拍', '体育器材', 120.00),
    ('篮球斯伯丁', '体育器材', 180.00),
    ('瑜伽垫', '体育器材', 45.00),
    ('跳绳计数', '体育器材', 25.00),
    ('乒乓球拍双拍', '体育器材', 60.00),
    ('卫衣春秋款', '服饰', 89.00),
    ('牛仔裤修身', '服饰', 99.00),
    ('运动鞋42码', '服饰', 159.00),
    ('书包双肩', '服饰', 65.00),
    ('帽子棒球帽', '服饰', 29.00),
]

DESCRIPTIONS = [
    '用了半年，九成新，功能正常',
    '买来没用过几次，几乎全新',
    '考研结束了便宜出',
    '毕业清仓，所有物品价格可议',
    '室友送的，不适合我，全新未拆封',
    '上学期买的，这学期课少用不上',
    '闲置物品，有需要的同学联系',
    '商品完好，附赠充电线',
]

COMMENTS = [
    '请问这个还有吗？',
    '能便宜点吗？',
    '什么时候方便看货？',
    '哪个宿舍的？我去拿',
    '还在吗？想买',
]

REPLIES = [
    '还在的',
    '最低XX元了',
    '今天晚上都行',
    'X栋XXX宿舍',
    '好的，私聊',
]

CONDITIONS = ['全新', '几乎全新', '九成新', '八成新', '七成新', '六成新及以下']

IMAGE_MAP = {
    '高等数学第七版': ['/uploads/textbook-math.jpg'],
    '大学英语四级真题': ['/uploads/textbook-english.jpg'],
    '线性代数辅导书': ['/uploads/textbook-linear-algebra.jpg'],
    'C语言程序设计': ['/uploads/textbook-c-programming.jpg'],
    '考研英语词汇书': ['/uploads/textbook-postgraduate-english.jpg'],
    '二手iPad Air': ['/uploads/electronics-ipad.jpg'],
    '机械键盘青轴': ['/uploads/electronics-keyboard.jpg'],
    '降噪耳机': ['/uploads/electronics-headphone.jpg'],
    'USB-C扩展坞': ['/uploads/electronics-dock.jpg'],
    '蓝牙鼠标': ['/uploads/electronics-mouse.jpg'],
    '台灯护眼': ['/uploads/daily-lamp.jpg'],
    '宿舍小风扇': ['/uploads/daily-fan.jpg'],
    '保温杯500ml': ['/uploads/daily-cup.jpg'],
    '收纳箱大号': ['/uploads/daily-storage-box.jpg'],
    '床上桌': ['/uploads/daily-desk-table.jpg'],
    '羽毛球拍': ['/uploads/sports-badminton.jpg'],
    '篮球斯伯丁': ['/uploads/sports-basketball.jpg'],
    '瑜伽垫': ['/uploads/sports-yoga-mat.jpg'],
    '跳绳计数': ['/uploads/sports-jump-rope.jpg'],
    '乒乓球拍双拍': ['/uploads/sports-table-tennis.jpg'],
    '卫衣春秋款': ['/uploads/clothing-hoodie.jpg'],
    '牛仔裤修身': ['/uploads/clothing-jeans.jpg'],
    '运动鞋42码': ['/uploads/clothing-shoes.jpg'],
    '书包双肩': ['/uploads/clothing-backpack.jpg'],
    '帽子棒球帽': ['/uploads/clothing-cap.jpg'],
}


def seed_users():
    print('正在生成 1000 名学生...')
    email_domains = ['@qq.com', '@163.com']
    count = 0
    for i in range(1, 1001):
        sid = f'22023{i:05d}'
        domain = choice(email_domains)
        local = f'student{sid}'
        u = User(
            student_id=sid,
            email=f'{local}{domain}',
            nickname=choice(NICKNAMES) + str(randint(1, 99)),
            credit=randint(80, 120),
            created_at=datetime.utcnow() - timedelta(days=randint(1, 60))
        )
        if i <= 5:
            u.set_password('123456')
        else:
            u.set_password(sid)
        db.session.add(u)
        count += 1
        if count % BATCH == 0:
            db.session.commit()
    db.session.commit()
    print(f'  已创建 {User.query.count()} 个用户')


def seed_products():
    print('正在生成商品数据...')
    users = User.query.limit(800).all()
    count = 0
    for idx, seller in enumerate(users):
        tmpl = PRODUCT_TEMPLATES[idx % len(PRODUCT_TEMPLATES)]
        title, cat, price = tmpl
        price = round(price * (0.8 + randint(0, 40) / 100), 2)
        status = 'sold' if idx % 7 == 0 else choice(['onsale', 'onsale', 'onsale', 'reserved'])
        p = Product(
            user_id=seller.id,
            title=title,
            description=choice(DESCRIPTIONS),
            price=price,
            category=cat,
            condition=choice(CONDITIONS),
            status=status,
            image_urls=json.dumps(IMAGE_MAP.get(title, [])),
            view_count=randint(0, 200),
            created_at=datetime.utcnow() - timedelta(hours=randint(1, 720)),
            updated_at=datetime.utcnow() - timedelta(hours=randint(0, 48))
        )
        db.session.add(p)
        count += 1
        if count % BATCH == 0:
            db.session.commit()
    db.session.commit()
    total = Product.query.count()
    onsale = Product.query.filter(Product.status == 'onsale').count()
    print(f'  已创建 {total} 件商品（在售 {onsale} 件）')


def seed_favorites():
    print('正在生成收藏数据...')
    users = User.query.limit(600).all()
    prods = Product.query.limit(500).all()
    count = 0
    for u in users:
        targets = sample(prods, min(randint(0, 5), len(prods)))
        for p in targets:
            f = Favorite(user_id=u.id, product_id=p.id)
            db.session.add(f)
            count += 1
        if count % BATCH == 0 and count > 0:
            db.session.commit()
    db.session.commit()
    print(f'  已创建 {Favorite.query.count()} 条收藏')


def seed_messages():
    print('正在生成留言数据...')
    products = Product.query.all()
    shuffle(products)
    users = User.query.all()
    count = 0

    # 前 750 件商品每件至少 1 条留言（确保绝大多数商品有留言）
    for p in products[:750]:
        buyer = choice(users[200:])
        while buyer.id == p.user_id:
            buyer = choice(users[200:])
        m = Message(
            product_id=p.id,
            from_user=buyer.id,
            to_user=p.user_id,
            content=choice(COMMENTS),
            created_at=datetime.utcnow() - timedelta(hours=randint(1, 168))
        )
        db.session.add(m)
        count += 1
        if randint(0, 1):
            reply = Message(
                product_id=p.id,
                from_user=p.user_id,
                to_user=buyer.id,
                content=choice(REPLIES),
                parent_id=m.id,
                created_at=m.created_at + timedelta(hours=randint(1, 24))
            )
            db.session.add(reply)
            count += 1
        if count % BATCH == 0:
            db.session.commit()

    # 部分商品额外追加留言（让留言总数保持在 600+）
    for p in products[:200]:
        extra = randint(0, 2)
        for _ in range(extra):
            buyer = choice(users[200:])
            while buyer.id == p.user_id:
                buyer = choice(users[200:])
            db.session.add(Message(
                product_id=p.id, from_user=buyer.id, to_user=p.user_id,
                content=choice(COMMENTS),
                created_at=datetime.utcnow() - timedelta(hours=randint(1, 168))
            ))
            count += 1
        if count % BATCH == 0:
            db.session.commit()

    db.session.commit()
    # 统计无留言商品数
    from sqlalchemy import func
    all_ids = set(p.id for p in products)
    has_msgs = set(r[0] for r in Message.query.with_entities(Message.product_id).distinct().all())
    no_msg = len(all_ids - has_msgs)
    print(f'  已创建 {Message.query.count()} 条留言（含回复，无留言商品: {no_msg} 件）')


def seed_transactions_and_reviews():
    print('正在生成交易与评价数据...')
    sold = Product.query.filter(Product.status == 'sold').limit(200).all()
    users = User.query.all()
    t_count = 0
    for p in sold:
        buyer = choice(users[200:800])
        if buyer.id == p.user_id:
            continue
        t = Transaction(
            product_id=p.id,
            seller_id=p.user_id,
            buyer_id=buyer.id,
            status='completed',
            created_at=datetime.utcnow() - timedelta(days=randint(1, 30))
        )
        db.session.add(t)
        db.session.flush()

        rating = randint(3, 5)
        rev = Review(
            transaction_id=t.id,
            from_user=buyer.id,
            to_user=p.user_id,
            rating=rating,
            content='交易顺利，很满意' if rating >= 4 else '还行吧',
            created_at=t.created_at + timedelta(hours=randint(1, 48))
        )
        db.session.add(rev)
        seller = db.session.get(User, p.user_id)
        if seller:
            seller.credit += (2 if rating >= 4 else 1)
        t_count += 1
        if t_count % BATCH == 0:
            db.session.commit()
    db.session.commit()
    print(f'  已创建 {Transaction.query.count()} 笔交易, {Review.query.count()} 条评价')


def seed_admin():
    admin = User(
        student_id='2202300000',
        email='admin@qq.com',
        nickname='hxin2076',
        role='admin',
        credit=999
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('  已创建管理员账号: 2202300000 / admin123')


def seed():
    db.drop_all()
    db.create_all()

    seed_users()
    seed_products()
    seed_favorites()
    seed_messages()
    seed_transactions_and_reviews()
    seed_admin()

    print()
    print('=' * 40)
    print('种子数据生成完成！')
    print(f'  用户: {User.query.count()} 人')
    print(f'  商品: {Product.query.count()} 件')
    print(f'  收藏: {Favorite.query.count()} 条')
    print(f'  留言: {Message.query.count()} 条')
    print(f'  交易: {Transaction.query.count()} 笔')
    print(f'  评价: {Review.query.count()} 条')
    print('=' * 40)
    print()
    print('测试账号:')
    print('  学号 2202300001 ~ 2202300005, 密码 123456')
    print('  管理员 2202300000, 密码 admin123')
    print('  其他学生: 学号=密码')


if __name__ == '__main__':
    seed()
