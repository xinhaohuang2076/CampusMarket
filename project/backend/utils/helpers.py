import re
import os
import uuid
from functools import wraps
from werkzeug.utils import secure_filename
from flask import current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


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


def save_upload(file):
    """保存上传文件，返回相对 URL 路径"""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'{uuid.uuid4().hex}.{ext}'
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        return f'/uploads/{filename}'
    return None


def admin_required(fn):
    """装饰器：JWT 认证 + 管理员权限检查"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        from models import db, User
        user = db.session.get(User, int(get_jwt_identity()))
        if not user or user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


def paginate(query, page, per_page=None):
    """通用分页辅助"""
    if per_page is None:
        per_page = current_app.config.get('ITEMS_PER_PAGE', 12)
    page = max(1, page)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }
