"""Constraint-based reorder planner endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Supplier
from ..schemas import PlanRequest
from ..services.context import load
from ..services.planner import plan

router = APIRouter()

@router.post("/planner/reorder")
def reorder_plan(req: PlanRequest, db: Session = Depends(get_db)):
    rows = load(db)
    used = sum(r.a["stock"] * r.a["storage_units"] for r in rows)
    sups = {s.id: {"name": s.name, "min_order_value": s.min_order_value} for s in db.scalars(select(Supplier))}
    items = [dict(id=r.a["id"], name=r.a["name"], supplier_id=r.a["supplier_id"], price=r.a["unit_price"],
                  storage_units=r.a["storage_units"], q_min=r.a["order_qty_min"], q_target=r.a["order_qty"],
                  status=r.a["status"], criticality=r.a["criticality"]) for r in rows if r.a["need_reorder"]]
    return plan(items, req.budget, req.storage_limit - used, sups)
