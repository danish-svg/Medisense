"""Small Bayesian network, exact inference by enumeration.
   Demand Up, Supplier Delay -> Stock-out      Near Expiry, Low Sales -> Waste"""
import math

CPT_STOCKOUT = {(1, 1): .85, (1, 0): .45, (0, 1): .30, (0, 0): .05}   # P(Stock-out | DemandUp, SupplierDelay)
CPT_WASTE    = {(1, 1): .80, (1, 0): .35, (0, 1): .15, (0, 0): .02}   # P(Waste | NearExpiry, LowSales)

def _marginal(cpt, p1, p2):
    return sum(cpt[(x, y)] * (p1 if x else 1 - p1) * (p2 if y else 1 - p2) for x in (0, 1) for y in (0, 1))

def _level(p): return "High" if p > .5 else "Medium" if p > .25 else "Low"

def assess(sup, a):
    p_demand = 1 / (1 + math.exp(-12 * (a["trend_raw"] - 1.1)))
    p_delay = min(.95, (100 - sup.reliability_pct) / 100 * 2 + sup.lead_time_days * .02)
    d = a["expiry_days"]
    p_expiry = 1.0 if d <= 30 else .6 if d <= 60 else .2 if d <= 90 else .02
    p_slow = min(.95, max(.05, a["unsold"] / a["stock"])) if a["stock"] else .05
    p_out, p_waste = _marginal(CPT_STOCKOUT, p_demand, p_delay), _marginal(CPT_WASTE, p_expiry, p_slow)
    r = lambda x: round(x, 3)
    return {"demand_up": r(p_demand), "supplier_delay": r(p_delay), "near_expiry": r(p_expiry), "low_sales": r(p_slow),
            "stockout": r(p_out), "waste": r(p_waste), "stockout_level": _level(p_out), "waste_level": _level(p_waste)}
