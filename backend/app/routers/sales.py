"""Recording sales: reduces stock and adds to today's sales total (which feeds the forecast)."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Medicine, SalesRecord
from ..schemas import SaleIn, BulkSalesIn

router = APIRouter()

def _check(m, qty):
    if m.expiry_days <= 0:
        raise HTTPException(400, f"{m.name} has expired and cannot be sold")
    if qty > m.stock:
        raise HTTPException(400, f"Only {m.stock} units of {m.name} in stock")

def _apply(db, m, qty, today):
    m.stock -= qty
    rec = db.scalar(select(SalesRecord).where(SalesRecord.medicine_id == m.id, SalesRecord.sale_date == today))
    if rec: rec.quantity += qty
    else: db.add(SalesRecord(medicine_id=m.id, sale_date=today, quantity=qty))

@router.post("/sales")
def record_sale(b: SaleIn, db: Session = Depends(get_db)):
    m = db.get(Medicine, b.medicine_id, with_for_update=True)     # row lock: two sales cannot oversell
    if not m: raise HTTPException(404, "Medicine not found")
    _check(m, b.quantity)
    _apply(db, m, b.quantity, date.today())
    db.commit()
    return {"stock": m.stock}

@router.post("/sales/bulk")
def record_bulk(b: BulkSalesIn, db: Session = Depends(get_db)):
    """All-or-nothing import: if any line is invalid, nothing is saved."""
    meds = db.scalars(select(Medicine).with_for_update()).all()
    by_name = {m.name.lower(): m for m in meds}
    totals, errors = {}, []
    for i, l in enumerate(b.lines, 1):
        m = by_name.get(l.medicine.strip().lower())
        if not m: errors.append(f"Line {i}: unknown medicine '{l.medicine}'"); continue
        totals[m.id] = totals.get(m.id, 0) + l.quantity
    by_id = {m.id: m for m in meds}
    for mid, q in totals.items():
        try: _check(by_id[mid], q)
        except HTTPException as e: errors.append(e.detail)
    if errors:
        raise HTTPException(400, "Nothing was imported. " + "; ".join(errors[:5]))
    for mid, q in totals.items(): _apply(db, by_id[mid], q, date.today())
    db.commit()
    return {"lines": len(b.lines), "medicines": len(totals)}
