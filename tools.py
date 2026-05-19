"""
CampusMarket 诊断工具集
快速检查前后端状态、重置数据、验证 API 一致性
"""
import sys
import os
import requests

BASE = 'http://127.0.0.1:5000'
FRONTEND = 'http://localhost:5173'


def check_backend():
    """快速健康检查 + 关键数据统计"""
    print('=== 后端诊断 ===')
    try:
        r = requests.get(f'{BASE}/api/health', timeout=3)
        print(f'  服务: {"✅" if r.ok else "❌"} ({r.status_code})')
    except:
        print('  服务: ❌ (连接失败)')
        return

    # 登录测试
    r = requests.post(f'{BASE}/api/auth/login',
                      json={'student_id': '2202300001', 'password': '123456'})
    if r.status_code == 200:
        token = r.json()['token']
        print(f'  登录: ✅ (用户ID: {r.json()["user"]["id"]})')

        # 关键接口快速验证
        checks = [
            ('商品列表', requests.get(f'{BASE}/api/products').status_code == 200),
            ('分类', requests.get(f'{BASE}/api/categories').status_code == 200),
            ('商品1详情', requests.get(f'{BASE}/api/products/1').status_code == 200),
            ('个人信息', requests.get(f'{BASE}/api/user/profile',
                                     headers={'Authorization': f'Bearer {token}'}).status_code == 200),
            ('我的商品', requests.get(f'{BASE}/api/products/mine',
                                    headers={'Authorization': f'Bearer {token}'}).status_code == 200),
        ]
        for name, ok in checks:
            print(f'  {name}: {"✅" if ok else "❌"}')
    else:
        print(f'  登录: ❌ (密码不对或用户不存在，需重新 seed)')


def check_frontend():
    """检查前端是否可访问"""
    print('\n=== 前端诊断 ===')
    try:
        r = requests.get(FRONTEND, timeout=3)
        print(f'  服务: {"✅" if r.ok else "❌"} ({r.status_code})')
    except:
        print('  服务: ❌ (连接失败)')


def reset_db():
    """重置数据库到初始种子状态（警告：会删除所有新增数据）"""
    print('=== 重置数据库 ===')
    from app import create_app
    app = create_app()
    with app.app_context():
        from models import db
        db.drop_all()
        db.create_all()
    print('  空表已重建，请运行 seed.py 填充数据')


def validate_api_consistency():
    """验证所有 API 响应格式一致性"""
    print('\n=== API 一致性检查 ===')
    try:
        r = requests.post(f'{BASE}/api/auth/login',
                          json={'student_id': '2202300001', 'password': '123456'})
        if r.status_code != 200:
            print('  ❌ 无法登录，跳过')
            return
        token = r.json()['token']
        h = {'Authorization': f'Bearer {token}'}
    except:
        print('  ❌ 后端未运行')
        return

    endpoints = [
        ('GET', '/api/products', None),
        ('GET', '/api/categories', None),
        ('GET', '/api/conditions', None),
        ('GET', '/api/user/profile', h),
        ('GET', '/api/products/mine', h),
        ('GET', '/api/favorites', h),
        ('GET', '/api/transactions', h),
        ('GET', '/api/messages/mine', h),
        ('GET', '/api/users/1/reviews', None),
    ]

    ok = 0
    for method, path, headers in endpoints:
        try:
            r = requests.request(method, f'{BASE}{path}', headers=headers, timeout=3)
            data = r.json()
            # 检查是否返回 JSON（而非 HTML 错误页）
            assert isinstance(data, dict), '非 JSON 响应'
            ok += 1
        except Exception as e:
            print(f'  ❌ {path}: {e}')

    print(f'  {ok}/{len(endpoints)} 接口返回有效 JSON')


def check_all():
    """一键全检"""
    check_backend()
    check_frontend()
    validate_api_consistency()


if __name__ == '__main__':
    # 确保能找到后端模块
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project/backend'))
    check_all()
