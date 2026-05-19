from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .product import Product
from .message import Message
from .favorite import Favorite
from .transaction import Transaction
from .review import Review

__all__ = ['db', 'User', 'Product', 'Message', 'Favorite', 'Transaction', 'Review']
