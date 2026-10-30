"""Database tables."""
from datetime import datetime, date
from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    lead_time_days: Mapped[int]
    reliability_pct: Mapped[float]
    min_order_value: Mapped[float]          # supplier minimum order (Rs)

class Medicine(Base):
    __tablename__ = "medicines"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(60))
    criticality: Mapped[str] = mapped_column(String(12), default="essential")   # vital | essential | desirable
    stock: Mapped[int]
    unit_price: Mapped[float]
    expiry_days: Mapped[int]                # days until the current batch expires
    storage_units: Mapped[float] = mapped_column(default=1.0)   # shelf space used per unit
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    sales: Mapped[list["SalesRecord"]] = relationship(cascade="all, delete-orphan")
    orders: Mapped[list["PurchaseOrder"]] = relationship(cascade="all, delete-orphan")

class SalesRecord(Base):
    __tablename__ = "sales_records"
    __table_args__ = (UniqueConstraint("medicine_id", "sale_date"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="CASCADE"), index=True)
    sale_date: Mapped[date]                 # one row per medicine per day (total units sold)
    quantity: Mapped[int]

class Branch(Base):
    __tablename__ = "branches"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    absorb_rate: Mapped[float]              # share of surplus stock this branch can sell
    distance_km: Mapped[float]

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="CASCADE"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    quantity: Mapped[int]
    cost: Mapped[float]
    status: Mapped[str] = mapped_column(String(12), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    value: Mapped[float]
