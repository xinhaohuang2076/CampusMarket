from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from utils import validate_student_id, validate_email, validate_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    student_id = (data.get('student_id') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password', '')

    if not student_id or not email or not password:
        return jsonify({'error': '学号、邮箱、密码不能为空'}), 400

    if not validate_student_id(student_id):
        return jsonify({'error': '学号格式错误（10位数字，以22023开头）'}), 400

    if not validate_email(email):
        return jsonify({'error': '邮箱格式错误（仅支持@163.com和@qq.com）'}), 400

    if not validate_password(password):
        return jsonify({'error': '密码长度须为6-64位'}), 400

    if User.query.filter_by(student_id=student_id).first():
        return jsonify({'error': '该学号已注册'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': '该邮箱已注册'}), 409

    user = User(student_id=student_id, email=email,
                nickname=data.get('nickname', '').strip() or student_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'message': '注册成功', 'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    student_id = (data.get('student_id') or '').strip()
    password = data.get('password', '')

    if not student_id or not password:
        return jsonify({'error': '学号和密码不能为空'}), 400

    user = User.query.filter_by(student_id=student_id).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '学号或密码错误'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'message': '登录成功', 'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    nickname = data.get('nickname')
    email = data.get('email')
    phone = data.get('phone')

    if nickname is not None:
        nickname = nickname.strip()
        if len(nickname) > 50:
            return jsonify({'error': '昵称不能超过50个字符'}), 400
        user.nickname = nickname or user.student_id

    if email is not None:
        email = email.strip()
        if not validate_email(email):
            return jsonify({'error': '邮箱格式错误（仅支持@163.com和@qq.com）'}), 400
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return jsonify({'error': '该邮箱已被使用'}), 409
        user.email = email

    if phone is not None:
        if phone and not validate_phone(phone):
            return jsonify({'error': '手机号格式错误'}), 400
        user.phone = phone

    db.session.commit()
    return jsonify({'message': '更新成功', 'user': user.to_dict()}), 200


@auth_bp.route('/api/user/password', methods=['PUT'])
@jwt_required()
def change_password():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    old_pw = data.get('old_password', '')
    new_pw = data.get('new_password', '')

    if not old_pw or not new_pw:
        return jsonify({'error': '旧密码和新密码不能为空'}), 400

    if not user.check_password(old_pw):
        return jsonify({'error': '旧密码错误'}), 403

    if not validate_password(new_pw):
        return jsonify({'error': '新密码长度须为6-64位'}), 400

    user.set_password(new_pw)
    db.session.commit()
    return jsonify({'message': '密码修改成功'}), 200
