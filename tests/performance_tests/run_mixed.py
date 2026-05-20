"""混合场景：所有 6 类用户全开（默认权重）"""
from locustfile import (
    BrowsingUser, SearchIntensiveUser, AuthenticatedUser,
    ActiveSeller, TransactionUser, AdminUser
)
