from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Transaction, Product, User
from utils import paginate

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/api/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    """买家发起交易意向"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get('product_id'):
        return jsonify({'error': '缺少商品ID'}), 400

    product = db.session.get(Product, data['product_id'])
    if not product:
        return jsonify({'error': '商品不存在'}), 404

    if product.user_id == user_id:
        return jsonify({'error': '不能购买自己的商品'}), 400

    if product.status not in ('onsale', 'reserved'):
        return jsonify({'error': '该商品当前不可交易'}), 400

    existing = Transaction.query.filter_by(
        product_id=product.id, buyer_id=user_id, status='pending'
    ).first()
    if existing:
        return jsonify({'error': '你已发起过交易意向'}), 409

    t = Transaction(
        product_id=product.id,
        seller_id=product.user_id,
        buyer_id=user_id,
        status='pending'
    )
    db.session.add(t)
    db.session.commit()

    return jsonify({'message': '交易意向已发送', 'transaction': t.to_dict()}), 201


@transaction_bp.route('/api/transactions/<int:tid>', methods=['PUT'])
@jwt_required()
def update_transaction(tid):
    """卖家确认/取消交易"""
    user_id = int(get_jwt_identity())
    t = db.session.get(Transaction, tid)
    if not t:
        return jsonify({'error': '交易记录不存在'}), 404

    if t.seller_id != user_id:
        return jsonify({'error': '无权操作此交易'}), 403

    data = request.get_json()
    action = data.get('action')  # complete / cancel

    if action == 'complete':
        if t.status != 'pending':
            return jsonify({'error': '当前状态无法完成交易'}), 400
        t.status = 'completed'
        product = db.session.get(Product, t.product_id)
        if product:
            product.transition_to('sold')
    elif action == 'cancel':
        if t.status != 'pending':
            return jsonify({'error': '当前状态无法取消交易'}), 400
        t.status = 'cancelled'
    else:
        return jsonify({'error': '无效操作，可选：complete / cancel'}), 400

    db.session.commit()
    return jsonify({'message': '操作成功', 'transaction': t.to_dict()}), 200


@transaction_bp.route('/api/transactions', methods=['GET'])
@jwt_required()
def list_transactions():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', 'all')  # buy / sell / all

    if role == 'buy':
        query = Transaction.query.filter_by(buyer_id=user_id)
    elif role == 'sell':
        query = Transaction.query.filter_by(seller_id=user_id)
    else:
        query = Transaction.query.filter(
            db.or_(Transaction.buyer_id == user_id, Transaction.seller_id == user_id)
        )

    query = query.order_by(Transaction.created_at.desc())
    result = paginate(query, page)

    return jsonify(result), 200
