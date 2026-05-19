from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Review, Transaction, User
from utils import validate_rating, paginate

review_bp = Blueprint('review', __name__)


@review_bp.route('/api/reviews', methods=['POST'])
@jwt_required()
def create_review():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get('transaction_id'):
        return jsonify({'error': '缺少交易ID'}), 400

    t = db.session.get(Transaction, data['transaction_id'])
    if not t:
        return jsonify({'error': '交易记录不存在'}), 404
    if t.status != 'completed':
        return jsonify({'error': '只能对已完成的交易进行评价'}), 400
    if t.buyer_id != user_id and t.seller_id != user_id:
        return jsonify({'error': '无权评价此交易'}), 403

    existing = Review.query.filter_by(transaction_id=t.id).first()
    if existing:
        return jsonify({'error': '该交易已评价过'}), 409

    rating = data.get('rating')
    if not validate_rating(rating):
        return jsonify({'error': '评分须为1-5的整数'}), 400

    # 被评价人：交易对方
    to_user = t.seller_id if user_id == t.buyer_id else t.buyer_id

    review = Review(
        transaction_id=t.id,
        from_user=user_id,
        to_user=to_user,
        rating=int(rating),
        content=(data.get('content') or '').strip()
    )
    db.session.add(review)

    # 更新信用分
    target = db.session.get(User, to_user)
    if target:
        # 简单算法：好评 +2，差评 -2
        if int(rating) >= 4:
            target.credit += 2
        elif int(rating) <= 2:
            target.credit = max(0, target.credit - 2)
        else:
            target.credit += 1
        target.credit = min(target.credit, 200)

    db.session.commit()
    return jsonify({'message': '评价成功', 'review': review.to_dict()}), 201


@review_bp.route('/api/users/<int:user_id>/reviews', methods=['GET'])
def list_reviews(user_id):
    """查看某个用户收到的评价"""
    page = request.args.get('page', 1, type=int)
    query = Review.query.filter_by(to_user=user_id).order_by(Review.created_at.desc())
    result = paginate(query, page)

    # 附带平均评分
    from sqlalchemy import func
    avg = db.session.query(func.avg(Review.rating)).filter(Review.to_user == user_id).scalar()
    result['avg_rating'] = round(float(avg), 1) if avg else None

    return jsonify(result), 200
