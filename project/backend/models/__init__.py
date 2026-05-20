from sqlalchemy import create_engine, or_ as or_, and_ as and_, func as func
from sqlalchemy.orm import Session, sessionmaker, declarative_base

engine = None
_session_factory = None
Base = declarative_base()


class _DBProxy:
    """兼容旧代码中 db.Column, db.String, db.Integer 等语法的代理"""
    Column = __import__('sqlalchemy', fromlist=['Column']).Column
    String = __import__('sqlalchemy', fromlist=['String']).String
    Integer = __import__('sqlalchemy', fromlist=['Integer']).Integer
    Float = __import__('sqlalchemy', fromlist=['Float']).Float
    Text = __import__('sqlalchemy', fromlist=['Text']).Text
    DateTime = __import__('sqlalchemy', fromlist=['DateTime']).DateTime
    Boolean = __import__('sqlalchemy', fromlist=['Boolean']).Boolean
    DECIMAL = __import__('sqlalchemy', fromlist=['DECIMAL']).DECIMAL
    ForeignKey = __import__('sqlalchemy', fromlist=['ForeignKey']).ForeignKey
    UniqueConstraint = __import__('sqlalchemy', fromlist=['UniqueConstraint']).UniqueConstraint

    _shared_session = None

    @property
    def session(self):
        global _session_factory
        if _session_factory is None:
            return None
        if _DBProxy._shared_session is None:
            _DBProxy._shared_session = _session_factory()
        return _DBProxy._shared_session

    @session.setter
    def session(self, value):
        pass

    @property
    def Model(self):
        return Base

    @property
    def relationship(self):
        return __import__('sqlalchemy.orm', fromlist=['relationship']).relationship

    @property
    def backref(self):
        return __import__('sqlalchemy.orm', fromlist=['backref']).backref

    def or_(self, *args):
        return or_(*args)

    def and_(self, *args):
        return and_(*args)

    @property
    def func(self):
        return func

    def drop_all(self):
        Base.metadata.drop_all(bind=engine)

    def create_all(self):
        Base.metadata.create_all(bind=engine)


db = _DBProxy()


def init_db(database_url):
    """初始化数据库连接"""
    global engine, _session_factory
    connect_args = {}
    if 'sqlite' in database_url:
        connect_args['check_same_thread'] = False
    engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
    _session_factory = sessionmaker(bind=engine)

    from sqlalchemy.orm import Query

    class _QueryProperty:
        def __get__(self, obj, cls):
            return Query(cls, db.session)

    Base.query = _QueryProperty()
    db.create_all()
    return db


def get_app_context():
    """兼容旧代码"""
    from contextlib import nullcontext
    return nullcontext()


from .user import User
from .product import Product
from .message import Message
from .favorite import Favorite
from .transaction import Transaction
from .review import Review

__all__ = ['db', 'User', 'Product', 'Message', 'Favorite', 'Transaction', 'Review',
           'init_db', 'get_app_context']
