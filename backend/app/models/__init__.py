"""DB 테이블 모델. API 응답 모양(app/schemas/)과는 따로 둔다.

여기서 모든 모델을 import 해야 Alembic --autogenerate 가 테이블을 빠짐없이 찾는다.
"""

from app.models.customer import Customer
from app.models.inquiry import Inquiry, InquiryStatus
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.stats import (
    DailyMetric,
    HourlyVisit,
    MonthlyCategorySale,
    MonthlyMetric,
    MonthlyTrafficSource,
)

__all__ = [
    "Customer",
    "DailyMetric",
    "HourlyVisit",
    "Inquiry",
    "InquiryStatus",
    "MonthlyCategorySale",
    "MonthlyMetric",
    "MonthlyTrafficSource",
    "Order",
    "OrderStatus",
    "Product",
]
