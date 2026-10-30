"""Demand pattern classification with fuzzy memberships (regular vs sporadic)."""
import math

def _ramp_down(x, lo, hi):          # 1 below lo, 0 above hi, linear between
    return 1.0 if x <= lo else 0.0 if x >= hi else (hi - x) / (hi - lo)

def classify(h):
    nz = [x for x in h if x > 0]
    n = len(h)
    adi = n / len(nz) if nz else float(n)                  # average days between demands
    if len(nz) > 1:
        m = sum(nz) / len(nz)
        cv2 = (math.sqrt(sum((x - m) ** 2 for x in nz) / len(nz)) / m) ** 2   # variability of demand size
    else:
        cv2 = 0.0
    degree = min(_ramp_down(adi, 1.1, 1.8), _ramp_down(cv2, 0.3, 0.8))       # fuzzy AND = min
    label = "regular" if degree >= 0.5 else "sporadic"
    croston = (sum(nz) / len(nz)) / adi if nz else 0.0     # demand per day for sporadic items
    rule = ("Regular demand: forecast from the recent weekly average and trend; safety stock from demand variation."
            if label == "regular" else
            "Sporadic demand: forecast from average size and gap between demands; keep a buffer sized to the largest recent demand.")
    return {"label": label, "degree": round(degree, 2), "adi": round(adi, 2), "cv2": round(cv2, 2),
            "croston": croston, "rule": rule}
