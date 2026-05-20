import re
import os
import uuid
from werkzeug.utils import secure_filename


def validate_student_id(sid):
    """学号：10 位数字，以 22023 开头"""
    return bool(re.match(r'^22023\d{5}$', sid))


def validate_email(email):
    """邮箱：仅支持 @163.com 或 @qq.com"""
    if not bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email)):
        return False
    domain = email.split('@')[1].lower()
    return domain in ('163.com', 'qq.com')


def validate_password(password):
    """密码：6-64 位"""
    return 6 <= len(password) <= 64


def validate_price(price):
    """价格需为非负数且最多两位小数"""
    try:
        p = float(price)
        return p >= 0 and round(p, 2) == p
    except (ValueError, TypeError):
        return False


def validate_phone(phone):
    """手机号：11 位数字（可选）"""
    if not phone:
        return True
    return bool(re.match(r'^1\d{10}$', phone))


def validate_rating(rating):
    try:
        r = int(rating)
        return 1 <= r <= 5
    except (ValueError, TypeError):
        return False


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, upload_dir):
    """保存上传文件，返回相对 URL 路径"""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'{uuid.uuid4().hex}.{ext}'
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        return f'/uploads/{filename}'
    return None


def paginate(query, page, per_page=12):
    """通用分页辅助（兼容纯 SQLAlchemy，无 Flask-SQLAlchemy 依赖）"""
    page = max(1, page)
    total = query.count()
    offset = (page - 1) * per_page
    items = query.limit(per_page).offset(offset).all()
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    return {
        'items': [item.to_dict() for item in items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'has_next': page < pages,
        'has_prev': page > 1
    }
