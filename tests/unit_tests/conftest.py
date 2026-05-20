"""pytest fixtures - 独立 tempfile SQLite，避免死锁"""
import sys
import os
import pytest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../project/backend')))

from fastapi import FastAPI
from models import init_db


@pytest.fixture(scope='function')
def app():
    """每个测试创建独立的 tempfile SQLite，互不污染"""
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp.close()
    init_db(f'sqlite:///{tmp.name}')

    application = FastAPI()

    from routes import auth_bp, product_bp, message_bp, transaction_bp, review_bp, admin_bp
    application.include_router(auth_bp)
    application.include_router(product_bp)
    application.include_router(message_bp)
    application.include_router(transaction_bp)
    application.include_router(review_bp)
    application.include_router(admin_bp)

    yield application

    # 清理共享 session
    from models import _DBProxy
    if _DBProxy._shared_session:
        try:
            _DBProxy._shared_session.close()
        except Exception:
            pass
        _DBProxy._shared_session = None

    # 删临时文件
    from models import engine
    if engine and hasattr(engine, 'url') and str(engine.url).startswith('sqlite'):
        db_path = engine.url.database
        if db_path and os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def session(app):
    from models import db as _db
    return _db.session
