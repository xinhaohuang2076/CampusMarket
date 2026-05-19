"""管理员后台蓝图"""
from flask import Blueprint, jsonify, request
from models import db, User, Product, Transaction, Review
from utils import admin_required, paginate

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def dashboard_stats():
    """总览统计数据"""
    total_users = User.query.count()
    total_products = Product.query.count()
    total_transactions = Transaction.query.count()
    total_reviews = Review.query.count()

    # 商品状态分布
    products_by_status = {}
    for status in ['onsale', 'reserved', 'sold', 'removed']:
        products_by_status[status] = Product.query.filter(
            Product.status == status).count()

    # 最近注册的用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_users_data = [{
        'id': u.id,
        'student_id': u.student_id,
        'nickname': u.nickname,
        'role': u.role,
        'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for u in recent_users]

    # 最近交易
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()).limit(5).all()

    return jsonify({
        'total_users': total_users,
        'total_products': total_products,
        'total_transactions': total_transactions,
        'total_reviews': total_reviews,
        'products_by_status': products_by_status,
        'recent_users': recent_users_data,
        'recent_transactions': [t.to_dict() for t in recent_transactions]
    })


@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def list_users():
    """用户列表（分页 + 关键词搜索 + 角色筛选）"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '', type=str)
    role_filter = request.args.get('role', '', type=str)

    query = User.query
    if keyword:
        query = query.filter(
            db.or_(
                User.student_id.like(f'%{keyword}%'),
                User.nickname.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%')
            )
        )
    if role_filter:
        query = query.filter(User.role == role_filter)

    query = query.order_by(User.id.desc())
    return jsonify(paginate(query, page, per_page=20))


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """修改用户角色/信用分"""
    from flask_jwt_extended import get_jwt_identity

    current_admin_id = int(get_jwt_identity())
    if current_admin_id == user_id:
        return jsonify({'error': '不能修改自己的角色'}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json() or {}
    if 'role' in data:
        if data['role'] not in ('user', 'admin'):
            return jsonify({'error': '无效的角色值'}), 400
        user.role = data['role']
    if 'credit' in data:
        try:
            credit = int(data['credit'])
            user.credit = max(0, min(200, credit))
        except (ValueError, TypeError):
            return jsonify({'error': '信用分需为整数（0-200）'}), 400

    db.session.commit()
    return jsonify({'message': '更新成功', 'user': user.to_dict()})


@admin_bp.route('/api/admin/products', methods=['GET'])
@admin_required
def list_products():
    """所有商品列表（含已下架/已售）"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '', type=str)
    category = request.args.get('category', '', type=str)
    keyword = request.args.get('keyword', '', type=str)

    query = Product.query
    if status:
        query = query.filter(Product.status == status)
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        query = query.filter(
            db.or_(
                Product.title.like(f'%{keyword}%'),
                Product.description.like(f'%{keyword}%')
            )
        )

    query = query.order_by(Product.id.desc())
    return jsonify(paginate(query, page, per_page=20))


@admin_bp.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """强制删除商品"""
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': '商品已强制删除'})


@admin_bp.route('/api/admin/transactions', methods=['GET'])
@admin_required
def list_transactions():
    """全部交易记录"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '', type=str)

    query = Transaction.query
    if status:
        query = query.filter(Transaction.status == status)

    query = query.order_by(Transaction.id.desc())
    return jsonify(paginate(query, page, per_page=20))
