from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import db, Message, Product, User
from utils import paginate, get_current_user

message_bp = APIRouter()


class SendMessage(BaseModel):
    content: str
    parent_id: int | None = None


@message_bp.get('/api/products/{product_id}/messages')
def list_messages(product_id: int, page: int = 1):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')

    query = Message.query.filter_by(product_id=product_id, parent_id=None)\
        .order_by(Message.created_at.desc())
    result = paginate(query, page)
    for item in result['items']:
        msg = db.session.get(Message, item['id'])
        if msg:
            item['replies'] = [r.to_dict() for r in msg.replies]
    return result


@message_bp.post('/api/products/{product_id}/messages', status_code=201)
def send_message(product_id: int, data: SendMessage,
                 current_user: User = Depends(get_current_user)):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')
    if product.status not in ('onsale', 'reserved'):
        raise HTTPException(400, '该商品已下架或售出')
    if not data.content:
        raise HTTPException(400, '留言内容不能为空')

    msg = Message(
        product_id=product_id,
        from_user=current_user.id,
        to_user=product.user_id,
        content=data.content,
        parent_id=data.parent_id
    )
    db.session.add(msg)
    db.session.commit()
    return {'message': '留言成功', 'msg': msg.to_dict()}


@message_bp.get('/api/messages/mine')
def my_messages(direction: str = 'received', page: int = 1,
                current_user: User = Depends(get_current_user)):
    if direction == 'sent':
        query = Message.query.filter_by(from_user=current_user.id, parent_id=None)
    else:
        query = Message.query.filter_by(to_user=current_user.id, parent_id=None)

    query = query.order_by(Message.created_at.desc())
    result = paginate(query, page)
    for item in result['items']:
        msg = db.session.get(Message, item['id'])
        if msg and msg.product:
            item['product_title'] = msg.product.title
    return result
