import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, Product, Favorite
from utils import validate_price, save_upload, paginate

product_bp = Blueprint('product', __name__)


@product_bp.route('/api/products', methods=['GET'])
def list_products():
    """商品列表，支持分页、搜索、分类筛选"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'latest')  # latest / price_asc / price_desc

    query = Product.query.filter(Product.status.in_(['onsale', 'reserved']))

    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            db.or_(Product.title.ilike(like), Product.description.ilike(like))
        )

    if category:
        query = query.filter(Product.category == category)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    result = paginate(query, page)
    return jsonify(result), 200


@product_bp.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': '商品标题不能为空'}), 400
    if len(title) > 100:
        return jsonify({'error': '标题不能超过100个字符'}), 400

    price = data.get('price')
    if price is None or not validate_price(price):
        return jsonify({'error': '价格格式不正确'}), 400

    category = data.get('category', '其他')
    if category not in Product.VALID_CATEGORIES:
        if category:
            return jsonify({'error': f'分类无效，可选：{", ".join(Product.VALID_CATEGORIES)}'}), 400
        category = '其他'

    condition = data.get('condition')
    if condition and condition not in Product.VALID_CONDITIONS:
        return jsonify({'error': f'成色无效，可选：{", ".join(Product.VALID_CONDITIONS)}'}), 400
    if not condition:
        condition = '九成新'

    product = Product(
        user_id=user_id,
        title=title,
        description=(data.get('description') or '').strip(),
        price=float(price),
        category=category,
        condition=condition,
        image_urls=json.dumps(data.get('image_urls', []), ensure_ascii=False)
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': '发布成功', 'product': product.to_dict()}), 201


@product_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404

    product.increment_view()
    db.session.commit()

    return jsonify({'product': product.to_dict()}), 200


@product_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    user_id = int(get_jwt_identity())
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    if product.user_id != user_id:
        return jsonify({'error': '无权修改此商品'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    title = data.get('title')
    if title is not None:
        title = title.strip()
        if not title:
            return jsonify({'error': '商品标题不能为空'}), 400
        if len(title) > 100:
            return jsonify({'error': '标题不能超过100个字符'}), 400
        product.title = title

    description = data.get('description')
    if description is not None:
        product.description = description.strip()

    price = data.get('price')
    if price is not None:
        if not validate_price(price):
            return jsonify({'error': '价格格式不正确'}), 400
        product.price = float(price)

    category = data.get('category')
    if category is not None:
        if category not in Product.VALID_CATEGORIES:
            return jsonify({'error': f'分类无效，可选：{", ".join(Product.VALID_CATEGORIES)}'}), 400
        product.category = category

    condition = data.get('condition')
    if condition is not None:
        if condition not in Product.VALID_CONDITIONS:
            return jsonify({'error': f'成色无效，可选：{", ".join(Product.VALID_CONDITIONS)}'}), 400
        product.condition = condition

    image_urls = data.get('image_urls')
    if image_urls is not None:
        product.image_urls = json.dumps(image_urls, ensure_ascii=False)

    db.session.commit()
    return jsonify({'message': '更新成功', 'product': product.to_dict()}), 200


@product_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_product(product_id):
    user_id = int(get_jwt_identity())
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    if product.user_id != user_id:
        return jsonify({'error': '无权操作此商品'}), 403

    product.transition_to('removed')
    db.session.commit()
    return jsonify({'message': '已下架'}), 200


@product_bp.route('/api/products/mine', methods=['GET'])
@jwt_required()
def my_products():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()

    query = Product.query.filter_by(user_id=user_id)
    if status:
        query = query.filter(Product.status == status)
    query = query.order_by(Product.created_at.desc())

    result = paginate(query, page)
    return jsonify(result), 200


# ---- 图片上传 ----

@product_bp.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400

    file = request.files['file']
    url = save_upload(file)
    if not url:
        return jsonify({'error': '不支持的文件格式（支持：png/jpg/jpeg/gif/webp）'}), 400

    return jsonify({'url': url}), 200


# ---- 收藏 ----

@product_bp.route('/api/products/<int:product_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite(product_id):
    user_id = int(get_jwt_identity())
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404

    fav = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'message': '已取消收藏', 'favorited': False}), 200
    else:
        fav = Favorite(user_id=user_id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'message': '已收藏', 'favorited': True}), 201


@product_bp.route('/api/favorites', methods=['GET'])
@jwt_required()
def list_favorites():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)

    query = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc())
    result = paginate(query, page)
    # 附带商品概要
    favs = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc())
    fav_result = paginate(favs, page)
    items = []
    for fav in fav_result['items']:
        f = db.session.get(Favorite, fav['id'])
        item = fav
        if f and f.product:
            item['product'] = f.product.to_dict()
        items.append(item)

    fav_result['items'] = items
    return jsonify(fav_result), 200


@product_bp.route('/api/categories', methods=['GET'])
def list_categories():
    return jsonify({'categories': sorted(Product.VALID_CATEGORIES)}), 200


@product_bp.route('/api/conditions', methods=['GET'])
def list_conditions():
    return jsonify({'conditions': list(Product.VALID_CONDITIONS)}), 200
