import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from config import Config
from models import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库，关闭时清理"""
    db_url = os.getenv('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    init_db(db_url)
    yield
    # 关闭数据库连接
    from models import engine
    if engine:
        engine.dispose()


def create_app():
    """创建 FastAPI 应用"""
    app = FastAPI(title='CampusMarket', lifespan=lifespan)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # 静态文件（上传目录）
    upload_dir = Config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)
    app.mount('/uploads', StaticFiles(directory=upload_dir), name='uploads')

    # 注册请求后回滚 session 中间件（防止脏 session 污染后续请求）
    @app.middleware("http")
    async def db_rollback_middleware(request: Request, call_next):
        from models import _DBProxy
        response = await call_next(request)
        if _DBProxy._shared_session:
            try:
                _DBProxy._shared_session.rollback()
            except Exception:
                pass
        return response

    # 注册路由
    from routes import auth_bp, product_bp, message_bp, transaction_bp, review_bp, admin_bp
    app.include_router(auth_bp)
    app.include_router(product_bp)
    app.include_router(message_bp)
    app.include_router(transaction_bp)
    app.include_router(review_bp)
    app.include_router(admin_bp)

    # 健康检查
    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    # 全局异常处理
    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        logger.warning('404: %s', request.url)
        return JSONResponse(status_code=404, content={'error': '接口不存在'})

    @app.exception_handler(500)
    async def server_error(request: Request, exc):
        logger.error('500: %s - %s', request.url, str(exc)[:200])
        return JSONResponse(status_code=500, content={'error': '服务器内部错误'})

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn
    env = os.getenv('ENV', 'development')
    if env == 'production':
        workers = int(os.getenv('UVICORN_WORKERS', '4'))
        port = int(os.getenv('PORT', '5000'))
        print(f' * CampusMarket 生产模式启动: http://127.0.0.1:{port} (workers={workers})')
        uvicorn.run('app:app', host='127.0.0.1', port=port, workers=workers)
    else:
        port = int(os.getenv('PORT', '5000'))
        print(f' * CampusMarket 开发模式启动: http://127.0.0.1:{port}')
        uvicorn.run('app:app', host='127.0.0.1', port=port, reload=True)
