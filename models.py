from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class ProductMapping(Base):
    __tablename__ = "product_mappings"
    id = Column(Integer, primary_key=True)
    sku = Column(String, index=True, nullable=False)       # internal SKU
    shopee_item_id = Column(String, index=True, nullable=True)
    loyverse_item_id = Column(String, index=True, nullable=True)
    extra = Column(JSON, default={})
    __table_args__ = (UniqueConstraint("sku", name="uq_sku"),)

class ProcessedOrder(Base):
    __tablename__ = "processed_orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)  # e.g., "shopee"
    processed_at = Column(DateTime, default=datetime.datetime.utcnow)
    raw = Column(JSON, nullable=True)

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True)
    level = Column(String, default="INFO")
    message = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    meta = Column(JSON, default={})
