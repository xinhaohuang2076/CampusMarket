"""管理员后台蓝图"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import db, User, Product, Transaction, Review
from utils import paginate, admin_required

admin_bp = APIRouter()


class UpdateUser(BaseModel):
    role: str | None = None
    credit: int | None = None


@admin_bp.get('/api/admin/stats')
def dashboard_stats(admin: User = Depends(admin_required)):
    total_users = User.query.count()
    total_products = Product.query.count()
    total_transactions = Transaction.query.count()
    total_reviews = Review.query.count()

    products_by_status = {}
    for status in ['onsale', 'reserved', 'sold', 'removed']:
        products_by_status[status] = Product.query.filter(Product.status == status).count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return {
        'total_users': total_users,
        'total_products': total_products,
        'total_transactions': total_transactions,
        'total_reviews': total_reviews,
        'products_by_status': products_by_status,
        'recent_users': [{
            'id': u.id, 'student_id': u.student_id, 'nickname': u.nickname,
            'role': u.role, 'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for u in recent_users],
        'recent_transactions': [
            t.to_dict() for t in Transaction.query.order_by(
                Transaction.created_at.desc()).limit(5).all()
        ]
    }


@admin_bp.get('/api/admin/users')
def list_users(page: int = 1, keyword: str = '', role: str = '',
               admin: User = Depends(admin_required)):
    query = User.query
    if keyword:
        query = query.filter(db.or_(
            User.student_id.like(f'%{keyword}%'),
            User.nickname.like(f'%{keyword}%'),
            User.email.like(f'%{keyword}%')
        ))
    if role:
        query = query.filter(User.role == role)
    query = query.order_by(User.id.desc())
    return paginate(query, page, per_page=20)


@admin_bp.put('/api/admin/users/{user_id}')
def update_user(user_id: int, data: UpdateUser, admin: User = Depends(admin_required)):
    if admin.id == user_id:
        raise HTTPException(403, '不能修改自己的角色')

    user = db.session.get(User, user_id)
    if not user:
        raise HTTPException(404, '用户不存在')

    if data.role is not None:
        if data.role not in ('user', 'admin'):
            raise HTTPException(400, '无效的角色值')
        user.role = data.role
    if data.credit is not None:
        user.credit = max(0, min(200, int(data.credit)))

    db.session.commit()
    return {'message': '更新成功', 'user': user.to_dict()}


@admin_bp.get('/api/admin/products')
def list_products(page: int = 1, status: str = '', category: str = '', keyword: str = '',
                  admin: User = Depends(admin_required)):
    query = Product.query
    if status:
        query = query.filter(Product.status == status)
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        query = query.filter(db.or_(
            Product.title.like(f'%{keyword}%'),
            Product.description.like(f'%{keyword}%')
        ))
    query = query.order_by(Product.id.desc())
    return paginate(query, page, per_page=20)


@admin_bp.delete('/api/admin/products/{product_id}')
def delete_product(product_id: int, admin: User = Depends(admin_required)):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')
    db.session.delete(product)
    db.session.commit()
    return {'message': '商品已强制删除'}


@admin_bp.get('/api/admin/transactions')
def list_transactions(page: int = 1, status: str = '',
                      admin: User = Depends(admin_required)):
    query = Transaction.query
    if status:
        query = query.filter(Transaction.status == status)
    query = query.order_by(Transaction.id.desc())
    return paginate(query, page, per_page=20)
