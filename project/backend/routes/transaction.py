from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import db, Transaction, Product, User
from utils import paginate, get_current_user

transaction_bp = APIRouter()


class CreateTransaction(BaseModel):
    product_id: int


class UpdateTransaction(BaseModel):
    action: str


@transaction_bp.post('/api/transactions', status_code=201)
def create_transaction(data: CreateTransaction, current_user: User = Depends(get_current_user)):
    product = db.session.get(Product, data.product_id)
    if not product:
        raise HTTPException(404, '商品不存在')

    if product.user_id == current_user.id:
        raise HTTPException(400, '不能对自己发布商品发起交易')

    if product.status not in ('onsale', 'reserved'):
        raise HTTPException(400, '该商品已下架或售出')

    existing = Transaction.query.filter_by(
        product_id=data.product_id, buyer_id=current_user.id,
        status='pending').first()
    if existing:
        raise HTTPException(409, '已对此商品发起过交易意向')

    t = Transaction(
        product_id=data.product_id,
        seller_id=product.user_id,
        buyer_id=current_user.id,
        status='pending'
    )
    product.status = 'reserved'
    db.session.add(t)
    db.session.commit()
    return {'message': '交易意向已发送', 'transaction': t.to_dict()}


@transaction_bp.put('/api/transactions/{transaction_id}')
def update_transaction(transaction_id: int, data: UpdateTransaction,
                       current_user: User = Depends(get_current_user)):
    t = db.session.get(Transaction, transaction_id)
    if not t:
        raise HTTPException(404, '交易不存在')
    if t.seller_id != current_user.id:
        raise HTTPException(403, '只有卖家可以操作此交易')

    if data.action == 'complete':
        t.status = 'completed'
        product = db.session.get(Product, t.product_id)
        if product:
            product.status = 'sold'
    elif data.action == 'cancel':
        t.status = 'cancelled'
        product = db.session.get(Product, t.product_id)
        if product:
            product.status = 'onsale'
    else:
        raise HTTPException(400, '无效的操作（complete/cancel）')

    db.session.commit()
    label = '完成' if data.action == 'complete' else '取消'
    return {'message': f'交易已{label}', 'transaction': t.to_dict()}


@transaction_bp.get('/api/transactions')
def list_transactions(role: str = 'all', page: int = 1,
                      current_user: User = Depends(get_current_user)):
    query = Transaction.query
    if role == 'buy':
        query = query.filter(Transaction.buyer_id == current_user.id)
    elif role == 'sell':
        query = query.filter(Transaction.seller_id == current_user.id)
    else:
        query = query.filter(db.or_(
            Transaction.buyer_id == current_user.id,
            Transaction.seller_id == current_user.id
        ))
    query = query.order_by(Transaction.id.desc())
    return paginate(query, page)
