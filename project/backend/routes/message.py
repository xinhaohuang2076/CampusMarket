from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Message, Product
from utils import paginate

message_bp = Blueprint('message', __name__)


@message_bp.route('/api/products/<int:product_id>/messages', methods=['GET'])
def list_messages(product_id):
    """获取某个商品的所有留言（含回复）"""
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404

    page = request.args.get('page', 1, type=int)
    query = Message.query.filter_by(product_id=product_id, parent_id=None) \
        .order_by(Message.created_at.asc())
    result = paginate(query, page)

    # 为每条顶级留言附上回复
    for msg in result['items']:
        m = db.session.get(Message, msg['id'])
        if m:
            replies = Message.query.filter_by(parent_id=msg['id']) \
                .order_by(Message.created_at.asc()).all()
            msg['replies'] = [r.to_dict() for r in replies]

    return jsonify(result), 200


@message_bp.route('/api/products/<int:product_id>/messages', methods=['POST'])
@jwt_required()
def send_message(product_id):
    user_id = int(get_jwt_identity())
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404

    if product.status == 'removed':
        return jsonify({'error': '该商品已下架'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'error': '留言内容不能为空'}), 400
    if len(content) > 1000:
        return jsonify({'error': '留言内容不能超过1000个字符'}), 400

    msg = Message(
        product_id=product_id,
        from_user=user_id,
        to_user=product.user_id,
        content=content,
        parent_id=data.get('parent_id')
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({'message': '发送成功', 'msg': msg.to_dict()}), 201


@message_bp.route('/api/messages/mine', methods=['GET'])
@jwt_required()
def my_messages():
    """我收到的/发出的留言"""
    user_id = int(get_jwt_identity())
    direction = request.args.get('direction', 'received')  # received / sent
    page = request.args.get('page', 1, type=int)

    if direction == 'sent':
        query = Message.query.filter_by(from_user=user_id)
    else:
        query = Message.query.filter_by(to_user=user_id)

    query = query.order_by(Message.created_at.desc())
    result = paginate(query, page)

    return jsonify(result), 200
