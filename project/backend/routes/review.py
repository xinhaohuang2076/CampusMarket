from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import db, Review, Transaction, User
from utils import validate_rating, paginate, get_current_user

review_bp = APIRouter()


class CreateReview(BaseModel):
    transaction_id: int
    rating: int
    content: str = ''


@review_bp.post('/api/reviews', status_code=201)
def create_review(data: CreateReview, current_user: User = Depends(get_current_user)):
    t = db.session.get(Transaction, data.transaction_id)
    if not t:
        raise HTTPException(404, '交易不存在')
    if t.status != 'completed':
        raise HTTPException(400, '只能评价已完成的交易')
    if current_user.id not in (t.buyer_id, t.seller_id):
        raise HTTPException(403, '不是此交易的参与者')
    if not validate_rating(data.rating):
        raise HTTPException(400, '评分须为1-5的整数')

    existing = Review.query.filter_by(transaction_id=data.transaction_id,
                                       from_user=current_user.id).first()
    if existing:
        raise HTTPException(409, '已评价过此交易')

    to_user_id = t.seller_id if current_user.id == t.buyer_id else t.buyer_id
    rev = Review(
        transaction_id=data.transaction_id,
        from_user=current_user.id,
        to_user=to_user_id,
        rating=data.rating,
        content=data.content
    )
    db.session.add(rev)

    seller = db.session.get(User, to_user_id)
    if seller:
        if data.rating >= 4:
            seller.credit += 2
        elif data.rating <= 2:
            seller.credit -= 2
        else:
            seller.credit += 1
        seller.credit = max(0, min(200, seller.credit))

    db.session.commit()
    return {'message': '评价成功', 'review': rev.to_dict()}


@review_bp.get('/api/users/{user_id}/reviews')
def user_reviews(user_id: int, page: int = 1):
    user = db.session.get(User, user_id)
    if not user:
        raise HTTPException(404, '用户不存在')

    query = Review.query.filter_by(to_user=user_id).order_by(Review.id.desc())
    result = paginate(query, page)
    # 附加评价者信息
    for item in result['items']:
        rev = db.session.get(Review, item['id'])
        if rev and rev.reviewer:
            item['from_nickname'] = rev.reviewer.nickname
    # 计算平均评分
    from sqlalchemy import func
    avg = db.session.query(func.avg(Review.rating)).filter(
        Review.to_user == user_id).scalar()
    result['avg_rating'] = round(avg, 1) if avg else 0
    return result
