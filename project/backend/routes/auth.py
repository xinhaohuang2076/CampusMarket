from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import db, User
from utils import validate_student_id, validate_email, validate_password, create_token, get_current_user

auth_bp = APIRouter()


class RegisterRequest(BaseModel):
    student_id: str
    email: str
    password: str
    nickname: str = ''


class LoginRequest(BaseModel):
    student_id: str
    password: str


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    email: str | None = None
    phone: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@auth_bp.post('/api/auth/register', status_code=201)
def register(data: RegisterRequest):
    student_id = data.student_id.strip()
    email = data.email.strip()
    password = data.password

    if not student_id or not email or not password:
        raise HTTPException(400, '学号、邮箱、密码不能为空')

    if not validate_student_id(student_id):
        raise HTTPException(400, '学号格式错误（10位数字，以22023开头）')

    if not validate_email(email):
        raise HTTPException(400, '邮箱格式错误（仅支持@163.com和@qq.com）')

    if not validate_password(password):
        raise HTTPException(400, '密码长度须为6-64位')

    if User.query.filter_by(student_id=student_id).first():
        raise HTTPException(409, '该学号已注册')

    if User.query.filter_by(email=email).first():
        raise HTTPException(409, '该邮箱已注册')

    user = User(student_id=student_id, email=email,
                nickname=data.nickname.strip() or student_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_token(str(user.id))
    return {'message': '注册成功', 'token': token, 'user': user.to_dict()}


@auth_bp.post('/api/auth/login')
def login(data: LoginRequest):
    student_id = data.student_id.strip()
    password = data.password

    if not student_id or not password:
        raise HTTPException(400, '学号和密码不能为空')

    user = User.query.filter_by(student_id=student_id).first()
    if not user or not user.check_password(password):
        raise HTTPException(401, '学号或密码错误')

    token = create_token(str(user.id))
    return {'message': '登录成功', 'token': token, 'user': user.to_dict()}


@auth_bp.get('/api/user/profile')
def get_profile(current_user: User = Depends(get_current_user)):
    return {'user': current_user.to_dict()}


@auth_bp.put('/api/user/profile')
def update_profile(data: UpdateProfileRequest, current_user: User = Depends(get_current_user)):
    if data.nickname is not None:
        nickname = data.nickname.strip()
        if len(nickname) > 50:
            raise HTTPException(400, '昵称不能超过50个字符')
        current_user.nickname = nickname or current_user.student_id

    if data.email is not None:
        email = data.email.strip()
        if not validate_email(email):
            raise HTTPException(400, '邮箱格式错误（仅支持@163.com和@qq.com）')
        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(409, '该邮箱已被使用')
        current_user.email = email

    if data.phone is not None:
        from utils import validate_phone
        if data.phone and not validate_phone(data.phone):
            raise HTTPException(400, '手机号格式错误')
        current_user.phone = data.phone

    db.session.commit()
    return {'message': '更新成功', 'user': current_user.to_dict()}


@auth_bp.put('/api/user/password')
def change_password(data: ChangePasswordRequest, current_user: User = Depends(get_current_user)):
    if not data.old_password or not data.new_password:
        raise HTTPException(400, '旧密码和新密码不能为空')

    if not current_user.check_password(data.old_password):
        raise HTTPException(403, '旧密码错误')

    if not validate_password(data.new_password):
        raise HTTPException(400, '新密码长度须为6-64位')

    current_user.set_password(data.new_password)
    db.session.commit()
    return {'message': '密码修改成功'}
