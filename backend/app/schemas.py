"""Request bodies."""
from pydantic import BaseModel, Field

class MedicineIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str
    criticality: str = Field("essential", pattern="^(vital|essential|desirable)$")
    stock: int = Field(ge=0)
    unit_price: float = Field(ge=0)
    expiry_days: int = Field(ge=1)
    avg_daily_sales: float = Field(gt=0)
    supplier_id: int
    storage_units: float = Field(1, gt=0)

class StockChange(BaseModel):
    delta: int

class PlanRequest(BaseModel):
    budget: float = Field(gt=0)
    storage_limit: float = Field(gt=0)

class SaleIn(BaseModel):
    medicine_id: int
    quantity: int = Field(gt=0)

class SaleLine(BaseModel):
    medicine: str
    quantity: int = Field(gt=0)

class BulkSalesIn(BaseModel):
    lines: list[SaleLine] = Field(min_length=1)

class OrderLine(BaseModel):
    medicine_id: int
    quantity: int = Field(gt=0)

class OrdersIn(BaseModel):
    lines: list[OrderLine]
