"""Dempster-Shafer combination of two sources about demand: sales trend and season.
   Frame: R (rising), F (falling), T (either / unknown)."""
RISING = {"Respiratory": {10, 11, 12, 1, 2}, "Antihistamine": {10, 11, 12, 1, 2, 3}, "Antibiotic": {6, 7, 8, 9}}

def _combine(a, b):
    k = a["R"] * b["F"] + a["F"] * b["R"]                  # conflicting mass
    if k >= .999:
        return {"R": 0, "F": 0, "T": 1}, 1.0
    n = 1 - k
    return {"R": (a["R"] * b["R"] + a["R"] * b["T"] + a["T"] * b["R"]) / n,
            "F": (a["F"] * b["F"] + a["F"] * b["T"] + a["T"] * b["F"]) / n,
            "T": a["T"] * b["T"] / n}, k

def assess(category, trend_raw, month):
    d = trend_raw - 1
    s = min(.85, abs(d) * 3)
    trend = {"R": s if d > 0 else 0, "F": s if d < 0 else 0}
    trend["T"] = 1 - trend["R"] - trend["F"]
    if category in RISING:
        up = month in RISING[category]
        season = {"R": .7 if up else 0, "F": 0 if up else .7, "T": .3}
        label = "peak season, demand usually rises" if up else "off season, demand usually falls"
    else:
        season, label = {"R": 0, "F": 0, "T": 1}, "no strong seasonal pattern"
    m, k = _combine(trend, season)
    r = lambda x: round(x, 2)
    if k > .4:
        decision, advice = "conflict", "Sources disagree. Keep the current forecast, add a 10% safety buffer and review in 3 days."
    elif m["R"] - m["F"] > .15:
        decision, advice = "rising", "Evidence points to rising demand. Plan stock for the higher forecast."
    elif m["F"] - m["R"] > .15:
        decision, advice = "falling", "Evidence points to falling demand. Avoid ordering more than the minimum."
    else:
        decision, advice = "uncertain", "Evidence is weak either way. Follow the standard forecast."
    return {"trend": {k_: r(v) for k_, v in trend.items()}, "season": {k_: r(v) for k_, v in season.items()},
            "season_label": label, "conflict": r(k), "belief_rising": r(m["R"]), "plausibility_rising": r(m["R"] + m["T"]),
            "belief_falling": r(m["F"]), "decision": decision, "advice": advice}
