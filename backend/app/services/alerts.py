"""Builds alerts. Every alert carries a plain-language 'why' list (the rules and facts that fired)."""
from . import bayes, evidence

def build(rows, month):
    out = []
    def add(a, sev, typ, msg, why):
        out.append({"medicine_id": a["id"], "medicine": a["name"], "severity": sev, "type": typ, "message": msg, "why": why})
    for r in rows:
        a, sup = r.a, r.sup
        cover = f'{a["stock"]} units on hand and about {a["avg_daily"]} sold per day gives roughly {a["days_cover"]} days of cover.'
        floor = f'As a {a["criticality"]} medicine its minimum stock is {a["min_stock"]} units and its reorder point is {a["reorder_point"]}.'
        if a["status"] == "Critical":
            add(a, "high", "stockout", f'will run out in about {max(1, round(a["days_cover"]))} days, before the {sup.lead_time_days}-day delivery from {sup.name}. Order {a["order_qty"]} units now.',
                [cover, f'{sup.name} needs {sup.lead_time_days} days to deliver, which is longer than the cover.', floor, "Stock is at or below the reorder point, so a reorder is recommended."])
        elif a["status"] == "Low":
            add(a, "medium", "low", f'is below its reorder point ({a["reorder_point"]}). Suggested order: {a["order_qty"]} units.',
                [cover, floor, "Stock has fallen to or below the reorder point."])
        if a["status"] == "Expired":
            add(a, "high", "expired", f'has expired. Remove {a["stock"]} units from the shelf.', ["The batch expiry date has passed."])
        elif a["unsold"] > 0 and a["expiry_days"] <= 60:
            add(a, "medium", "expiry", f'about {a["unsold"]} units may expire unsold in {a["expiry_days"]} days (Rs {a["value_at_risk"]}). See the Expiry planner.',
                [f'Expected sales in {a["expiry_days"]} days are about {round(a["avg_daily"] * a["expiry_days"])} units, but {a["stock"]} units are in stock.', "The excess stock will pass its expiry date unless it is moved."])
        if a["trend"] > 1.15:
            add(a, "info", "surge", f'demand is up {round((a["trend"] - 1) * 100)}% week over week.',
                [f'Average daily sales this week are higher than last week by {round((a["trend"] - 1) * 100)}%.', "The forecast and order size already include this growth."])
        if a["anomalies"]:
            add(a, "info", "spike", f'unusual sales spike on day {a["anomalies"][0] + 1} of the last {len(a["history"])}. Check for bulk purchases or data errors.',
                ["One day of sales was far above the normal range for this medicine."])
        b = bayes.assess(sup, a)
        if b["stockout"] > .5 and a["status"] not in ("Critical", "Expired"):
            add(a, "medium", "risk", f'has a {round(b["stockout"] * 100)}% estimated chance of a stock-out.',
                [f'Chance demand is rising: {round(b["demand_up"] * 100)}%.', f'Chance {sup.name} delivers late: {round(b["supplier_delay"] * 100)}%.', "Combining both gives the stock-out chance shown."])
        ev = evidence.assess(a["category"], a["trend_raw"], month)
        if ev["decision"] == "conflict":
            add(a, "info", "conflict", "has conflicting demand signals. " + ev["advice"],
                [f'Recent sales trend and the season ({ev["season_label"]}) point in opposite directions.', f'Conflict between the two sources: {round(ev["conflict"] * 100)}%.'])
    order = {"high": 0, "medium": 1, "info": 2}
    return sorted(out, key=lambda x: order[x["severity"]])
