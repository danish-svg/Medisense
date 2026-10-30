"""Dashboard, alerts, forecast, substitutes and expiry planning."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Branch
from ..services import alerts, bayes, evidence, expiry, substitutes
from ..services.context import load

router = APIRouter()
month = lambda: date.today().month

def _find(rows, mid):
    r = next((r for r in rows if r.a["id"] == mid), None)
    if not r: raise HTTPException(404, "Medicine not found")
    return r

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    rows = load(db); A = [r.a for r in rows]
    n = min(len(a["history"]) for a in A) if A else 0
    cats = {}
    for a in A: cats[a["category"]] = cats.get(a["category"], 0) + a["stock"] * a["unit_price"]
    return {"kpis": {"tracked": len(A), "stock_value": sum(a["stock"] * a["unit_price"] for a in A),
                     "need_reorder": sum(a["need_reorder"] for a in A),
                     "at_risk": sum(a["status"] in ("Critical", "Low") for a in A),
                     "expiring_30": sum(0 < a["expiry_days"] <= 30 for a in A),
                     "waste_risk": sum(a["value_at_risk"] for a in A if a["expiry_days"] <= 90),
                     "confidence": round(sum(a["confidence"] for a in A) / max(len(A), 1))},
            "history": [sum(a["history"][len(a["history"]) - n + i] for a in A) for i in range(n)],
            "forecast": [round(sum(a["forecast"][i] for a in A), 1) for i in range(7)],
            "categories": cats, "alerts": alerts.build(rows, month())[:6]}

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    return alerts.build(load(db), month())

@router.get("/medicines/{mid}/forecast")
def forecast(mid: int, db: Session = Depends(get_db)):
    r = _find(load(db), mid)
    return {"medicine": r.a, "bayes": bayes.assess(r.sup, r.a), "evidence": evidence.assess(r.a["category"], r.a["trend_raw"], month())}

@router.get("/medicines/{mid}/substitutes")
def get_substitutes(mid: int, db: Session = Depends(get_db)):
    rows = load(db)
    return substitutes.find(_find(rows, mid), rows)

@router.get("/expiry")
def expiry_plans(db: Session = Depends(get_db)):
    branches = db.scalars(select(Branch)).all()
    best = max(branches, key=lambda b: b.absorb_rate)
    out = []
    for r in sorted(load(db), key=lambda r: r.a["expiry_days"]):
        a = r.a
        if a["expiry_days"] <= 0 and a["stock"] > 0:
            v = round(a["stock"] * a["unit_price"])
            out.append({"medicine_id": a["id"], "name": a["name"], "expiry_days": a["expiry_days"], "units": a["stock"],
                        "plan": {"action": "Dispose of expired stock", "option": "Dispose", "expected_loss": v,
                                 "plan": [{"step": "Remove from shelf and dispose safely", "cost": v}],
                                 "options": [], "steps": [], "value": v}})
        elif a["unsold"] > 0 and a["expiry_days"] <= 90:
            p = expiry.plan(a["unsold"], a["unit_price"], a["expiry_days"], best.name, best.absorb_rate)
            out.append({"medicine_id": a["id"], "name": a["name"], "expiry_days": a["expiry_days"], "units": a["unsold"], "plan": p})
    return out
