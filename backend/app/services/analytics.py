"""Core inventory model: forecast, criticality rules, reorder point, status."""
import math
from .patterns import classify

Z = {"vital": 2.33, "essential": 1.65, "desirable": 1.28}   # service level per criticality
COVER = {"vital": 14, "essential": 7, "desirable": 3}        # minimum days of stock per criticality

def _mean(a): return sum(a) / len(a) if a else 0.0
def _std(a):
    m = _mean(a)
    return math.sqrt(_mean([(x - m) ** 2 for x in a]))

def analyze(m, sup, h):
    pat = classify(h)
    a, sd = _mean(h), _std(h)
    l7, p7 = _mean(h[-7:]), _mean(h[-14:-7])
    raw = min(3.0, max(0.3, l7 / p7)) if p7 > 0 else 1.0
    tr = min(1.4, max(0.8, raw))
    lt, zr = sup.lead_time_days, Z[m.criticality]
    if pat["label"] == "regular":
        base = max(l7, 0.1)
        fc = [round(base * tr ** ((i + 1) / 7), 1) for i in range(7)]
        ss = math.ceil(zr * sd * math.sqrt(lt))
        conf = max(60, round(100 - (sd / a * 40 if a else 0)))
        anom = [i for i, x in enumerate(h) if x > a + 2.2 * sd]
    else:
        base = max(pat["croston"], 0.05)
        fc = [round(base, 2)] * 7
        ss = math.ceil(max(h) * (1 + lt / 7) * zr / 1.65)
        conf, anom = 55, []
    min_stock = max(math.ceil(base * COVER[m.criticality]), ss)       # vital items get a higher floor
    rop = max(math.ceil(base * lt + ss), min_stock)
    dl = m.stock / base
    unsold = max(0, round(m.stock - base * m.expiry_days))
    need = m.stock <= rop + base * 3 or dl < lt + 7
    q_target = max(1, math.ceil(base * tr * (lt + 14) + ss - m.stock)) if need else 0
    q_min = max(1, min(q_target, math.ceil(rop - m.stock + base * lt))) if need else 0
    if m.expiry_days <= 0: st = "Expired"
    elif m.stock <= rop: st = "Critical" if dl < lt else "Low"
    elif unsold > 0 and m.expiry_days <= 60: st = "Expiring"
    elif dl > (365 if pat["label"] == "sporadic" else 150): st = "Overstock"
    else: st = "Healthy"
    return dict(id=m.id, name=m.name, category=m.category, criticality=m.criticality, stock=m.stock,
        unit_price=m.unit_price, expiry_days=m.expiry_days, storage_units=m.storage_units,
        supplier_id=sup.id, supplier=sup.name, lead_time=lt,
        pattern=pat["label"], pattern_degree=pat["degree"], pattern_adi=pat["adi"], pattern_cv2=pat["cv2"], pattern_rule=pat["rule"],
        avg_daily=round(base, 2), trend_raw=round(raw, 2), trend=round(tr, 2), forecast=fc, forecast_7d=round(sum(fc)),
        history=h, safety_stock=ss, reorder_point=rop, min_stock=min_stock, days_cover=round(dl, 1),
        unsold=unsold, value_at_risk=round(unsold * m.unit_price), confidence=conf, need_reorder=need,
        order_qty=q_target, order_qty_min=q_min, anomalies=anom, status=st)
