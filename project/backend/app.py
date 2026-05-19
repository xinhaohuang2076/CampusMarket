import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db

# 在导入 routes 之前确保 db 已初始化
jwt = JWTManager()


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    # 确保目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 日志：记录错误到文件
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(module)s] %(message)s'))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.WARNING)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from routes import auth_bp, product_bp, message_bp, transaction_bp, review_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)

    # 上传文件访问
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # 健康检查
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': '接口不存在'}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': '文件过大（最大16MB）'}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': '服务器内部错误'}), 500

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    print(' * CampusMarket 后端服务启动: http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=True)
