"""pytest fixtures - truly isolated in-memory SQLite, won't touch seed db"""
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../project/backend')))

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db as _db


TEST_SECRET = 'test-secret-for-pytest-only'


@pytest.fixture(scope='function')
def app():
    """Create a fresh app with in-memory SQLite, independent of seed db."""
    application = Flask(__name__)
    application.config['TESTING'] = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SECRET_KEY'] = TEST_SECRET
    application.config['JWT_SECRET_KEY'] = TEST_SECRET
    application.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400

    _db.init_app(application)
    JWTManager(application)

    # 注册蓝图（路由测试需要）
    from routes import auth_bp, product_bp, message_bp, transaction_bp, review_bp, admin_bp
    application.register_blueprint(auth_bp)
    application.register_blueprint(product_bp)
    application.register_blueprint(message_bp)
    application.register_blueprint(transaction_bp)
    application.register_blueprint(review_bp)
    application.register_blueprint(admin_bp)

    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def session(app):
    with app.app_context():
        yield _db.session
