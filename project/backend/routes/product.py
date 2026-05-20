import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from models import db, Product, Favorite, User
from utils import paginate, get_current_user, admin_required, save_upload

product_bp = APIRouter()
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')


class ProductCreate(BaseModel):
    title: str
    description: str = ''
    price: float
    category: str
    condition: str = '八成新'
    image_urls: list[str] = []


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    condition: str | None = None
    image_urls: list[str] | None = None


@product_bp.get('/api/products')
def list_products(
    page: int = Query(1),
    keyword: str = Query(''),
    category: str = Query(''),
    sort: str = Query('latest'),
):
    valid_categories = {'教材', '电子产品', '生活用品', '体育器材', '服饰', '其他'}
    if category and category not in valid_categories:
        category = ''

    valid_sorts = {'latest', 'price_asc', 'price_desc'}
    if sort not in valid_sorts:
        sort = 'latest'

    query = Product.query.filter(Product.status.in_(['onsale', 'reserved']))

    if keyword:
        like = f'%{keyword}%'
        query = query.filter(db.or_(Product.title.like(like), Product.description.like(like)))

    if category:
        query = query.filter(Product.category == category)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.desc())

    return paginate(query, page)


@product_bp.post('/api/products', status_code=201)
def create_product(data: ProductCreate, current_user: User = Depends(get_current_user)):
    from utils import validate_price
    if not data.title:
        raise HTTPException(400, '商品标题不能为空')
    if not validate_price(data.price):
        raise HTTPException(400, '价格无效')
    if not data.category:
        raise HTTPException(400, '分类不能为空')

    product = Product(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        price=data.price,
        category=data.category,
        condition=data.condition,
        image_urls=json.dumps(data.image_urls),
        status='onsale'
    )
    db.session.add(product)
    db.session.commit()
    return {'message': '发布成功', 'product': product.to_dict()}


@product_bp.get('/api/products/mine')
def my_products(page: int = 1, status: str = '',
                current_user: User = Depends(get_current_user)):
    query = Product.query.filter(Product.user_id == current_user.id)
    if status:
        query = query.filter(Product.status == status)
    query = query.order_by(Product.id.desc())
    return paginate(query, page)


@product_bp.get('/api/products/{product_id}')
def get_product(product_id: int):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')
    product.increment_view()
    db.session.commit()
    return {'product': product.to_dict()}


@product_bp.put('/api/products/{product_id}')
def update_product(product_id: int, data: ProductUpdate,
                   current_user: User = Depends(get_current_user)):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')
    if product.user_id != current_user.id:
        raise HTTPException(403, '无权修改此商品')

    if data.title is not None:
        product.title = data.title
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        from utils import validate_price
        if not validate_price(data.price):
            raise HTTPException(400, '价格无效')
        product.price = data.price
    if data.category is not None:
        product.category = data.category
    if data.condition is not None:
        product.condition = data.condition
    if data.image_urls is not None:
        product.image_urls = json.dumps(data.image_urls)

    db.session.commit()
    return {'message': '更新成功', 'product': product.to_dict()}


@product_bp.delete('/api/products/{product_id}')
def remove_product(product_id: int, current_user: User = Depends(get_current_user)):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')
    if product.user_id != current_user.id:
        raise HTTPException(403, '无权操作此商品')

    product.transition_to('removed')
    db.session.commit()
    return {'message': '已下架'}


@product_bp.post('/api/upload')
def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    url = save_upload(file, UPLOAD_FOLDER)
    if not url:
        raise HTTPException(400, '不支持的文件格式（支持：png/jpg/jpeg/gif/webp）')
    return {'url': url}


@product_bp.post('/api/products/{product_id}/favorite', status_code=201)
def toggle_favorite(product_id: int, current_user: User = Depends(get_current_user)):
    product = db.session.get(Product, product_id)
    if not product:
        raise HTTPException(404, '商品不存在')

    fav = Favorite.query.filter_by(
        user_id=current_user.id, product_id=product_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return {'message': '已取消收藏', 'favorited': False}
    else:
        fav = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        return {'message': '已收藏', 'favorited': True}


@product_bp.get('/api/favorites')
def list_favorites(page: int = Query(1), current_user: User = Depends(get_current_user)):
    query = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.id.desc())
    result = paginate(query, page)
    # 附加商品数据
    for item in result['items']:
        product = db.session.get(Product, item['product_id'])
        item['product'] = product.to_dict() if product else None
    return result


@product_bp.get('/api/categories')
def get_categories():
    return {'categories': ['教材', '电子产品', '生活用品', '体育器材', '服饰', '其他']}


@product_bp.get('/api/conditions')
def get_conditions():
    return {'conditions': ['全新', '几乎全新', '九成新', '八成新', '七成新', '六成新及以下']}
