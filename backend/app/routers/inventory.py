"""Medicines, suppliers, purchase orders and settings."""
import random
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Medicine, Supplier, PurchaseOrder, Setting
from ..schemas import MedicineIn, StockChange, OrdersIn, PlanRequest
from ..seed import make_history, history_records
from ..services.context import load

router = APIRouter()

@router.get("/medicines")
def list_medicines(db: Session = Depends(get_db)):
    return [r.a for r in load(db)]

@router.post("/medicines", status_code=201)
def add_medicine(b: MedicineIn, db: Session = Depends(get_db)):
    if not db.get(Supplier, b.supplier_id):
        raise HTTPException(400, "Unknown supplier")
    m = Medicine(**b.model_dump(exclude={"avg_daily_sales"}))
    # no sales yet for a new item: start from the entered average, with small daily variation
    m.sales = history_records(make_history(b.avg_daily_sales, random.Random(m.name), "regular"))
    db.add(m)
    try:
        db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "A medicine with this name already exists")
    return {"id": m.id}

@router.patch("/medicines/{mid}/stock")
def change_stock(mid: int, b: StockChange, db: Session = Depends(get_db)):
    m = db.get(Medicine, mid)
    if not m: raise HTTPException(404, "Medicine not found")
    m.stock = max(0, m.stock + b.delta); db.commit()
    return {"stock": m.stock}

@router.delete("/medicines/{mid}", status_code=204)
def delete_medicine(mid: int, db: Session = Depends(get_db)):
    m = db.get(Medicine, mid)
    if not m: raise HTTPException(404, "Medicine not found")
    db.delete(m); db.commit()
    return Response(status_code=204)

@router.get("/suppliers")
def suppliers(db: Session = Depends(get_db)):
    count = {}
    for m in db.scalars(select(Medicine)): count[m.supplier_id] = count.get(m.supplier_id, 0) + 1
    out = [{"id": s.id, "name": s.name, "lead_time_days": s.lead_time_days, "reliability_pct": s.reliability_pct,
            "min_order_value": s.min_order_value, "medicines": count.get(s.id, 0),
            "score": round(s.reliability_pct * .65 + (10 - s.lead_time_days) * 3.5)} for s in db.scalars(select(Supplier))]
    return sorted(out, key=lambda x: -x["score"])

@router.get("/orders")
def orders(db: Session = Depends(get_db)):
    q = select(PurchaseOrder, Medicine.name, Supplier.name).join(Medicine, Medicine.id == PurchaseOrder.medicine_id) \
        .join(Supplier, Supplier.id == PurchaseOrder.supplier_id).order_by(PurchaseOrder.id.desc())
    return [{"id": o.id, "medicine": mn, "supplier": sn, "quantity": o.quantity, "cost": o.cost, "status": o.status,
             "created_at": o.created_at.isoformat()} for o, mn, sn in db.execute(q)]

@router.post("/orders", status_code=201)
def create_orders(b: OrdersIn, db: Session = Depends(get_db)):
    for l in b.lines:
        m = db.get(Medicine, l.medicine_id)
        if not m: raise HTTPException(404, f"Medicine {l.medicine_id} not found")
        db.add(PurchaseOrder(medicine_id=m.id, supplier_id=m.supplier_id, quantity=l.quantity, cost=l.quantity * m.unit_price))
    db.commit()
    return {"created": len(b.lines)}

@router.post("/orders/{oid}/receive")
def receive(oid: int, db: Session = Depends(get_db)):
    o = db.get(PurchaseOrder, oid)
    if not o or o.status != "pending": raise HTTPException(404, "No pending order with this id")
    db.get(Medicine, o.medicine_id).stock += o.quantity
    o.status = "received"; db.commit()
    return {"ok": True}

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return {s.key: s.value for s in db.scalars(select(Setting))}

@router.put("/settings")
def put_settings(b: PlanRequest, db: Session = Depends(get_db)):
    for k, v in b.model_dump().items():
        row = db.get(Setting, k)
        if row: row.value = v
        else: db.add(Setting(key=k, value=v))
    db.commit()
    return b
