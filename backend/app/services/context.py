"""Loads every medicine with its supplier, sales history and analysis."""
from collections import namedtuple
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models import Medicine, Supplier
from .analytics import analyze

Row = namedtuple("Row", "m sup h a")

def load(db):
    sups = {s.id: s for s in db.scalars(select(Supplier))}
    meds = db.scalars(select(Medicine).options(selectinload(Medicine.sales)).order_by(Medicine.name)).all()
    today = date.today()
    days = [today - timedelta(days=27 - i) for i in range(28)]      # rolling 28-day window
    rows = []
    for m in meds:
        by_day = {r.sale_date: r.quantity for r in m.sales}
        h = [by_day.get(d, 0) for d in days]                          # days with no sales count as 0
        a = analyze(m, sups[m.supplier_id], h)
        a["sold_today"] = h[-1]
        rows.append(Row(m, sups[m.supplier_id], h, a))
    return rows
