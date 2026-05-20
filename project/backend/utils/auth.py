"""FastAPI JWT 认证依赖"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from models import db, User

SECRET_KEY = 'campus-market-secret-key-change-in-production'
ALGORITHM = 'HS256'
bearer_scheme = HTTPBearer(auto_error=False)


def create_token(user_id):
    """生成 JWT token"""
    from datetime import datetime, timedelta
    payload = {
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """FastAPI 依赖：从 Authorization header 解析当前用户"""
    if credentials is None:
        raise HTTPException(status_code=401, detail='Missing Authorization Header')
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get('sub'))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail='Invalid token')

    user = db.session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


async def admin_required(current_user: User = Depends(get_current_user)):
    """FastAPI 依赖：管理员权限检查"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='需要管理员权限')
    return current_user
